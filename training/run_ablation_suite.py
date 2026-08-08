"""
Ablation Suite Runner: One Command For The Whole Study
==========================================================

Runs everything training/train_ablation.py + evaluate_variant.py +
stats_ablation.py can do, in the right order, for every (variant, seed)
combination -- this is the single command to kick off overnight and walk
away from.

5 trainable variants (random needs no training, just eval) x N seeds x
3,000 episodes each, then a deterministic eval pass per combo, then the
Friedman/Wilcoxon stats script at the end so results are sitting there
ready when you check back.

Resumable: if a checkpoint or eval_summary.json already exists for a given
(variant, seed), that step is skipped by default -- so if this gets
interrupted (crash, reboot, Ctrl-C), rerunning the same command picks up
where it left off instead of restarting the whole study. Pass --force to
redo everything anyway.

One run that fails (exception, bad checkpoint, whatever) is logged to
logs/ablation/suite_errors.log and the suite moves on to the next
combination rather than dying -- you don't want to come back in the
morning to find it stopped at combo 3 of 30 over one bad seed.

Usage:
    python training/run_ablation_suite.py                       # seeds 1-5, 3000 episodes (default)
    python training/run_ablation_suite.py --seeds 1,2,3          # only 3 seeds
    python training/run_ablation_suite.py --episodes 3000 --eval-episodes 20
    python training/run_ablation_suite.py --force                 # ignore existing results, redo all
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import io
import json
import time
import traceback

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)

TRAINABLE_VARIANTS = ["dqn", "d3qn_full", "d3qn_no_per", "d3qn_no_noisy", "d3qn_no_multistep"]
ALL_VARIANTS = ["random"] + TRAINABLE_VARIANTS
ERROR_LOG = "logs/ablation/suite_errors.log"


def _log_error(context, exc):
    os.makedirs(os.path.dirname(ERROR_LOG), exist_ok=True)
    with open(ERROR_LOG, "a", encoding="utf-8") as f:
        f.write(f"\n{'=' * 60}\n{time.ctime()} -- {context}\n")
        f.write("".join(traceback.format_exception(type(exc), exc, exc.__traceback__)))
    print(f"❌ {context}: {exc}  (logged to {ERROR_LOG}, continuing with next combo)")


def checkpoint_exists(variant, seed):
    from training.train_ablation import CHECKPOINT_DIR
    import glob

    return len(glob.glob(f"{CHECKPOINT_DIR}/{variant}_seed{seed}_ep*.pth")) > 0


def eval_exists(variant, seed):
    from training.train_ablation import LOG_ROOT

    return os.path.exists(os.path.join(LOG_ROOT, f"{variant}_seed{seed}", "eval_summary.json"))


def run_suite(seeds, episodes, eval_episodes, max_steps, force):
    total_combos = len(ALL_VARIANTS) * len(seeds)
    print("=" * 70)
    print("ABLATION SUITE")
    print("=" * 70)
    print(f"Variants: {ALL_VARIANTS}")
    print(f"Seeds: {seeds}")
    print(f"Episodes/run (trainable variants): {episodes}   Eval episodes/target: {eval_episodes}")
    print(f"Total (variant, seed) combos: {total_combos}  "
          f"(training runs needed: {len(TRAINABLE_VARIANTS) * len(seeds)})")
    print("=" * 70)

    suite_start = time.time()
    done, skipped, failed = 0, 0, 0

    for variant in ALL_VARIANTS:
        for seed in seeds:
            combo = f"{variant}_seed{seed}"
            print(f"\n--- [{combo}] ({done + skipped + failed + 1}/{total_combos}) ---")

            # Training step (skipped entirely for random -- nothing to learn).
            # AblationTrainer now resumes from whatever checkpoint exists
            # (see train_ablation.py) -- so this always calls train() rather
            # than skipping the whole combo on any existing checkpoint. A
            # fully-finished combo just resumes past the target episode and
            # returns instantly; a partially-finished one (suite got killed
            # mid-run) picks up where it left off instead of restarting.
            if variant in TRAINABLE_VARIANTS:
                try:
                    from training.train_ablation import AblationTrainer

                    trainer = AblationTrainer(variant=variant, seed=seed, max_steps=max_steps, fresh=force)
                    trainer.train(total_episodes=episodes)
                except Exception as e:
                    _log_error(f"training {combo}", e)
                    failed += 1
                    continue

            # Eval step (always needed, including for random).
            if not force and eval_exists(variant, seed):
                print(f"[{combo}] eval already exists -- skipping")
                skipped += 1
                continue
            try:
                from training.evaluate_variant import evaluate

                evaluate(variant, seed, eval_episodes=eval_episodes, max_steps=max_steps)
                done += 1
            except Exception as e:
                _log_error(f"evaluating {combo}", e)
                failed += 1
                continue

    elapsed_hr = (time.time() - suite_start) / 3600
    print("\n" + "=" * 70)
    print(f"SUITE COMPLETE in {elapsed_hr:.2f}h -- done={done} skipped={skipped} failed={failed}")
    print("=" * 70)
    if failed:
        print(f"⚠️  {failed} combo(s) failed -- see {ERROR_LOG} before trusting the stats below.")

    # Run the stats script automatically so results are ready on wake-up.
    try:
        from training.stats_ablation import run as run_stats

        print("\nRunning Friedman/Wilcoxon stats (metric=mean_reward)...")
        run_stats(metric="mean_reward")
        print("\nRunning Friedman/Wilcoxon stats (metric=overall_detection_rate)...")
        run_stats(metric="overall_detection_rate")
    except Exception as e:
        _log_error("stats_ablation", e)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", default="1,2,3,4,5", help="Comma-separated seed list.")
    parser.add_argument("--episodes", type=int, default=3000)
    parser.add_argument("--eval-episodes", type=int, default=20, help="Eval episodes PER target (x5 targets).")
    parser.add_argument("--max-steps", type=int, default=75)
    parser.add_argument("--force", action="store_true", help="Redo everything, ignoring existing results.")
    args = parser.parse_args()

    seed_list = [int(s.strip()) for s in args.seeds.split(",") if s.strip()]
    run_suite(
        seeds=seed_list, episodes=args.episodes, eval_episodes=args.eval_episodes,
        max_steps=args.max_steps, force=args.force,
    )
