"""
Ablation Suite Runner: Parallel Worker
========================================

Same job as training/run_ablation_suite.py (train + eval every (variant,
seed) combo), but designed to be launched as N separate OS processes running
at the same time instead of one process working through everything
sequentially.

Why this exists: the bottleneck in this training setup is not the GPU (the
network is tiny -- a few hundred KB of weights -- so the GPU spends most of
its time idle waiting on Python). The real bottleneck is env.step(), which is
single-threaded Flask request/response handling. Running multiple seeds as
separate OS processes lets the OS schedule them onto different CPU cores
concurrently, which is where the actual speedup comes from. The GPU picks up
some slack too since forward/backward passes from multiple processes can
interleave on it, but CPU parallelism is the main win here, not GPU
parallelism.

The one thing that does NOT work by accident: all 5 mock target apps
(env/target_app_*.py) hardcode DB_NAME to a single shared file under env/
(env/banking.db, etc). Naively running training/train_ablation.py directly
in multiple terminals at once means multiple processes writing to the same
SQLite files concurrently -- lock errors, or silently corrupted/interleaved
data (since the agent's own actions -- registering fake users, posting,
uploading files -- mutate these DBs during training, this is not a
read-only-so-it's-fine situation).

This script fixes that by setting the MOCK_DB_DIR environment variable
before anything imports the target apps (env/target_app_*.py all read
DB_NAME from os.environ.get("MOCK_DB_DIR", "env")), and gives each worker
its own private copy of the 5 db files under env/_workers/worker<N>/,
seeded once from whatever's currently in env/*.db (run init_targets.py in
the shared env/ folder first, same as always -- this script does not seed
from scratch).

Usage -- open N terminals, one command per terminal, same episode/seed
settings in each:

    python training/run_ablation_parallel.py --worker-id 0 --total-workers 3
    python training/run_ablation_parallel.py --worker-id 1 --total-workers 3
    python training/run_ablation_parallel.py --worker-id 2 --total-workers 3

Each worker takes every Nth (variant, seed) combo (round-robin, not a
contiguous block) so the work -- and the mix of cheap "random" runs vs
expensive D3QN runs -- is spread evenly rather than one worker getting stuck
with all the slow combos.

Resumable exactly like run_ablation_suite.py: a combo with an existing
checkpoint/eval result is skipped (or resumed mid-training) unless --force
is passed. Safe to re-run the same 3-terminal command after an interruption.

After ALL workers finish, run the stats step once by hand (not from inside
a worker, since stats needs every combo done first):

    python training/stats_ablation.py --metric mean_reward
    python training/stats_ablation.py --metric overall_detection_rate

How many workers to actually use: match your CPU core count, not GPU count
-- there is only one GPU, and every worker process shares it fine for a
network this small (each process gets its own CUDA context, small VRAM
overhead per context, negligible on an 8GB+ card for a model this size).

Tuning --total-workers and --cpu-threads-per-worker together: each worker
process defaults to using 1 CPU thread for its own numpy/torch internals
(see _pin_cpu_threads() below for why more isn't automatically better).
Python's GIL means the actual bottleneck -- env.step()'s Flask request
handling -- is single-threaded per process no matter what, so the real
lever is process count, not thread count. Rule of thumb: leave 1-2 cores
free for the OS/GPU driver, use the rest as workers.

    12 logical cores -> --total-workers 8 to 10 is a solid default
    6 logical cores  -> --total-workers 4 to 5
    4 logical cores  -> --total-workers 2 to 3

If workers < (cores - 2), the leftover cores are going unused -- e.g. 12
cores with only 4 workers could reasonably try --cpu-threads-per-worker 2
on each to use more of the idle capacity, though the process-count lever
usually matters more than the thread-count one for this workload.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import glob
import io
import shutil
import time
import traceback

# Note: this file deliberately does NOT `import numpy` or `import torch` at
# module level -- those only get pulled in lazily inside run_worker(), via
# `from training.train_ablation import AblationTrainer`. That's intentional:
# it lets run_worker() set OMP_NUM_THREADS/MKL_NUM_THREADS/etc *before* those
# libraries initialize, which they must be set before to take effect. See
# the comment on _pin_cpu_threads() for why this matters.

TRAINABLE_VARIANTS = ["dqn", "d3qn_full", "d3qn_no_per", "d3qn_no_noisy", "d3qn_no_multistep"]
ALL_VARIANTS = ["random"] + TRAINABLE_VARIANTS
DB_FILES = ["banking.db", "ecommerce.db", "blog.db", "fileshare.db", "social.db"]


def _log_error(context, exc, error_log):
    os.makedirs(os.path.dirname(error_log), exist_ok=True)
    with open(error_log, "a", encoding="utf-8") as f:
        f.write(f"\n{'=' * 60}\n{time.ctime()} -- {context}\n")
        f.write("".join(traceback.format_exception(type(exc), exc, exc.__traceback__)))
    print(f"[worker] ERROR {context}: {exc}  (logged to {error_log}, continuing with next combo)")


def _pin_cpu_threads(n_threads, worker_id):
    """Caps how many CPU threads THIS process's numpy/torch internals may
    use. Must be called before numpy/torch have been imported by anything
    (the env vars below are read once at library init time, not re-checked
    later) -- run_worker() calls this first, before the AblationTrainer
    import that pulls those libraries in.

    Why this matters for "use GPU and CPU together, tuned": without this,
    every one of the N parallel worker processes defaults to using ALL
    available CPU cores for its own tensor/array math (numpy's BLAS
    backend, torch's intra-op thread pool). Run N of those at once and
    they all fight over the same cores -- oversubscription -- which can
    make "parallel" training slower than just running one process
    sequentially. The actual speedup here comes from having N independent
    OS processes (each free to use the GPU whenever it needs to, and each
    running its own single-threaded-by-Python's-GIL env.step() loop on its
    own core), not from each process ALSO being internally multi-threaded.
    One thread per worker is the safe default; raise
    --cpu-threads-per-worker only if you have meaningfully more cores than
    workers (e.g. 12 cores, 4 workers -> 2-3 threads/worker is reasonable).
    """
    n_threads = str(max(1, n_threads))
    os.environ["OMP_NUM_THREADS"] = n_threads
    os.environ["MKL_NUM_THREADS"] = n_threads
    os.environ["OPENBLAS_NUM_THREADS"] = n_threads
    os.environ["NUMEXPR_NUM_THREADS"] = n_threads
    import torch

    torch.set_num_threads(int(n_threads))
    gpu_note = f"cuda:{torch.cuda.get_device_name(0)}" if torch.cuda.is_available() else "no GPU detected -- CPU only"
    print(f"[worker {worker_id}] CPU threads pinned to {n_threads} | GPU: {gpu_note}")


def _seed_worker_db(worker_db_dir):
    """One-time copy of the shared env/*.db templates into this worker's
    private db directory. Skipped for any file that already exists there
    (so re-running after an interruption doesn't wipe progress-mutated
    data the worker already accumulated)."""
    os.makedirs(worker_db_dir, exist_ok=True)
    for db_file in DB_FILES:
        dest = os.path.join(worker_db_dir, db_file)
        if os.path.exists(dest):
            continue
        src = os.path.join("env", db_file)
        if not os.path.exists(src):
            print(f"[worker] WARNING: {src} not found -- run `python init_targets.py` first. "
                  f"This worker's target apps will create an empty db at {dest} instead.")
            continue
        shutil.copy2(src, dest)
        print(f"[worker] seeded {dest} from {src}")


def checkpoint_exists(variant, seed):
    from training.train_ablation import CHECKPOINT_DIR

    return len(glob.glob(f"{CHECKPOINT_DIR}/{variant}_seed{seed}_ep*.pth")) > 0


def eval_exists(variant, seed):
    from training.train_ablation import LOG_ROOT

    return os.path.exists(os.path.join(LOG_ROOT, f"{variant}_seed{seed}", "eval_summary.json"))


def run_worker(worker_id, total_workers, seeds, episodes, eval_episodes, max_steps, force, cpu_threads_per_worker=1):
    worker_db_dir = f"env/_workers/worker{worker_id}"
    error_log = f"logs/ablation/suite_errors_worker{worker_id}.log"

    # Order matters: this must run before the first numpy/torch import
    # anywhere in the process (see _pin_cpu_threads docstring). It's also
    # the point where torch gets imported for the first time in this
    # process, which is fine -- everything below only needs it lazily.
    _pin_cpu_threads(cpu_threads_per_worker, worker_id)

    # MUST happen before any import that eventually imports env/target_app_*.py
    # (env.inprocess_client.build_target_sessions does that import lazily
    # inside AblationTrainer.__init__, so this is early enough).
    os.environ["MOCK_DB_DIR"] = worker_db_dir
    _seed_worker_db(worker_db_dir)

    all_combos = [(v, s) for v in ALL_VARIANTS for s in seeds]
    my_combos = all_combos[worker_id::total_workers]  # round-robin, not a contiguous block

    print("=" * 70)
    print(f"ABLATION WORKER {worker_id}/{total_workers}")
    print("=" * 70)
    print(f"DB isolation dir: {worker_db_dir}")
    print(f"This worker's combos ({len(my_combos)}/{len(all_combos)} total): "
          f"{[f'{v}_seed{s}' for v, s in my_combos]}")
    print("=" * 70)

    worker_start = time.time()
    done, skipped, failed = 0, 0, 0

    for variant, seed in my_combos:
        combo = f"{variant}_seed{seed}"
        print(f"\n--- [worker {worker_id}] [{combo}] ---")

        if variant in TRAINABLE_VARIANTS:
            try:
                from training.train_ablation import AblationTrainer

                trainer = AblationTrainer(variant=variant, seed=seed, max_steps=max_steps, fresh=force)
                trainer.train(total_episodes=episodes)
            except Exception as e:
                _log_error(f"training {combo}", e, error_log)
                failed += 1
                continue

        if not force and eval_exists(variant, seed):
            print(f"[worker {worker_id}] [{combo}] eval already exists -- skipping")
            skipped += 1
            continue
        try:
            from training.evaluate_variant import evaluate

            evaluate(variant, seed, eval_episodes=eval_episodes, max_steps=max_steps)
            done += 1
        except Exception as e:
            _log_error(f"evaluating {combo}", e, error_log)
            failed += 1
            continue

    elapsed_hr = (time.time() - worker_start) / 3600
    print("\n" + "=" * 70)
    print(f"WORKER {worker_id} DONE in {elapsed_hr:.2f}h -- done={done} skipped={skipped} failed={failed}")
    if failed:
        print(f"WARNING: {failed} combo(s) failed -- see {error_log}")
    print("Once ALL workers report done, run stats by hand:")
    print("  python training/stats_ablation.py --metric mean_reward")
    print("  python training/stats_ablation.py --metric overall_detection_rate")
    print("=" * 70)


if __name__ == "__main__":
    import argparse

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--worker-id", type=int, required=True, help="0-indexed worker number for this process.")
    parser.add_argument("--total-workers", type=int, required=True, help="How many parallel workers you're running total.")
    parser.add_argument("--seeds", default="1,2,3,4,5", help="Comma-separated seed list.")
    parser.add_argument("--episodes", type=int, default=3000)
    parser.add_argument("--eval-episodes", type=int, default=20, help="Eval episodes PER target (x5 targets).")
    parser.add_argument("--max-steps", type=int, default=75)
    parser.add_argument("--force", action="store_true", help="Redo everything, ignoring existing results.")
    parser.add_argument(
        "--cpu-threads-per-worker", type=int, default=1,
        help="CPU threads this process's numpy/torch internals may use (default 1 -- see run_worker() docs "
             "for why more isn't automatically better when running several workers at once). Raise this only "
             "if (your CPU core count) / (--total-workers) is meaningfully more than 1 -- e.g. 12 cores with "
             "4 workers can reasonably try --cpu-threads-per-worker 2 or 3.",
    )
    args = parser.parse_args()

    if not (0 <= args.worker_id < args.total_workers):
        raise SystemExit(f"--worker-id must be in [0, {args.total_workers - 1}]")

    seed_list = [int(s.strip()) for s in args.seeds.split(",") if s.strip()]
    run_worker(
        worker_id=args.worker_id, total_workers=args.total_workers, seeds=seed_list,
        episodes=args.episodes, eval_episodes=args.eval_episodes, max_steps=args.max_steps, force=args.force,
        cpu_threads_per_worker=args.cpu_threads_per_worker,
    )
