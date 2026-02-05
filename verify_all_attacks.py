"""
Verify that mock targets are reachable and attack actions execute.

This script starts the local mock targets (if needed), then exercises the
configured action space using WebSecEnv. It does not retrain models and does
not require autonomous_scan.py.
"""

from __future__ import annotations

import argparse
import io
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import requests

from env.web_sec_env import WebSecEnv


if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


@dataclass
class TargetConfig:
    name: str
    url: str
    app: str
    port: int


@dataclass
class ActionResult:
    action_id: int
    real_action_id: int
    name: str
    reward: float
    status_code: Optional[int]
    url: Optional[str]
    had_response: bool
    request_error: bool
    exception: Optional[str] = None


TARGETS: Dict[str, TargetConfig] = {
    "ecommerce": TargetConfig(
        name="E-Commerce",
        url="http://localhost:5002",
        app="env/target_app_ecommerce.py",
        port=5002,
    ),
    "social": TargetConfig(
        name="Social Media",
        url="http://localhost:5003",
        app="env/target_app_social.py",
        port=5003,
    ),
    "banking": TargetConfig(
        name="Banking",
        url="http://localhost:5004",
        app="env/target_app_banking.py",
        port=5004,
    ),
    "blog": TargetConfig(
        name="Blog",
        url="http://localhost:5005",
        app="env/target_app_blog.py",
        port=5005,
    ),
    "fileshare": TargetConfig(
        name="File Share",
        url="http://localhost:5006",
        app="env/target_app_fileshare.py",
        port=5006,
    ),
}


def is_reachable(url: str, timeout: float = 1.0) -> Tuple[bool, Optional[int]]:
    try:
        response = requests.get(url, timeout=timeout, allow_redirects=True)
        return True, response.status_code
    except requests.RequestException:
        return False, None


def wait_for_target(url: str, timeout_seconds: float = 12.0) -> Tuple[bool, Optional[int]]:
    start = time.time()
    while time.time() - start < timeout_seconds:
        ok, status = is_reachable(url)
        if ok:
            return True, status
        time.sleep(0.5)
    return False, None


def start_target(config: TargetConfig, startup_timeout: float) -> Tuple[Optional[subprocess.Popen], bool, str]:
    already_running, _ = is_reachable(config.url)
    if already_running:
        return None, True, "already_running"

    process = subprocess.Popen(
        [sys.executable, config.app],
        cwd=os.getcwd(),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    ok, _ = wait_for_target(config.url, timeout_seconds=startup_timeout)
    status = "started" if ok else "failed_to_start"
    return process, ok, status


def stop_process(process: Optional[subprocess.Popen]) -> None:
    if not process:
        return
    try:
        process.terminate()
        process.wait(timeout=3)
    except Exception:
        try:
            process.kill()
            process.wait(timeout=3)
        except Exception:
            pass


def resolve_action_name(env: WebSecEnv, func) -> str:
    for name, value in env.__dict__.items():
        if value is func:
            return name

    if hasattr(func, "__func__"):
        func_obj = func.__func__
        for name in dir(env):
            try:
                bound = getattr(env, name)
            except Exception:
                continue
            if hasattr(bound, "__func__") and bound.__func__ is func_obj:
                return name

    return getattr(func, "__name__", "unknown")


def build_action_plan(env: WebSecEnv, full_actions: bool) -> List[Tuple[int, int, str]]:
    if full_actions:
        action_ids = sorted(env.action_book.keys())
        id_map = {action_id: action_id for action_id in action_ids}
    else:
        action_ids = list(range(env.action_space.n))
        id_map = {action_id: env.mock_action_map.get(action_id, 0) for action_id in action_ids}

    plan = []
    for action_id in action_ids:
        real_action_id = id_map[action_id]
        action_func = env.action_book.get(real_action_id)
        if action_func:
            name = resolve_action_name(env, action_func)
        else:
            name = f"missing_action_{real_action_id}"
        plan.append((action_id, real_action_id, name))

    return plan


def run_action(env: WebSecEnv, action_id: int, real_action_id: int, name: str) -> ActionResult:
    try:
        _, reward, terminated, truncated, info = env.step(action_id)
        response = env.last_response if info.get("url") else None
        status_code = response.status_code if response else None
        had_response = response is not None
        request_error = terminated and not info and response is None
        return ActionResult(
            action_id=action_id,
            real_action_id=real_action_id,
            name=name,
            reward=reward,
            status_code=status_code,
            url=info.get("url"),
            had_response=had_response,
            request_error=request_error,
        )
    except Exception as exc:
        return ActionResult(
            action_id=action_id,
            real_action_id=real_action_id,
            name=name,
            reward=0.0,
            status_code=None,
            url=None,
            had_response=False,
            request_error=True,
            exception=str(exc),
        )


def summarize_results(results: List[ActionResult]) -> Dict[str, int]:
    total = len(results)
    response_ok = sum(1 for r in results if r.had_response)
    request_errors = sum(1 for r in results if r.request_error)
    no_response = sum(1 for r in results if not r.had_response and not r.request_error)
    return {
        "total": total,
        "response_ok": response_ok,
        "request_errors": request_errors,
        "no_response": no_response,
    }


def print_failures(results: List[ActionResult], verbose: bool) -> None:
    failures = [r for r in results if r.request_error or not r.had_response]
    if not failures:
        print("  All actions returned a response.")
        return

    print("  Actions with errors or no response:")
    for result in failures:
        status = "error" if result.request_error else "no_response"
        detail = f"status={status}"
        if result.status_code is not None:
            detail += f", http={result.status_code}"
        if result.exception:
            detail += f", exception={result.exception}"
        if verbose and result.url:
            detail += f", url={result.url}"
        print(
            f"    - action={result.action_id} real={result.real_action_id} name={result.name} ({detail})"
        )


def parse_targets(value: str) -> List[str]:
    value = value.strip().lower()
    if value in {"all", "*"}:
        return list(TARGETS.keys())
    return [item.strip() for item in value.split(",") if item.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that targets are reachable and attacks execute."
    )
    parser.add_argument(
        "--targets",
        default="all",
        help="Comma-separated target names or 'all' (default: all)",
    )
    parser.add_argument(
        "--full-actions",
        action="store_true",
        help="Use full 150-action space instead of mock 50-action space",
    )
    parser.add_argument(
        "--reset-each",
        action="store_true",
        help="Reset environment before each action (slower but cleaner)",
    )
    parser.add_argument(
        "--startup-timeout",
        type=float,
        default=12.0,
        help="Seconds to wait for each target to start (default: 12)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print additional per-action details",
    )
    args = parser.parse_args()

    target_names = parse_targets(args.targets)
    unknown = [name for name in target_names if name not in TARGETS]
    if unknown:
        print(f"Unknown targets: {', '.join(unknown)}")
        return 2

    reset_each = args.reset_each

    processes: Dict[str, Optional[subprocess.Popen]] = {}
    start_status: Dict[str, str] = {}
    all_ok = True

    print("Starting targets...")
    for name in target_names:
        config = TARGETS[name]
        process, ok, status = start_target(config, args.startup_timeout)
        processes[name] = process
        start_status[name] = status
        if not ok:
            all_ok = False
            print(f"  {config.name}: failed to start")
        else:
            print(f"  {config.name}: {status}")

    if not all_ok:
        for process in processes.values():
            stop_process(process)
        return 1

    overall_failures = 0
    overall_actions = 0

    try:
        for name in target_names:
            config = TARGETS[name]
            print(f"\nRunning action checks for {config.name} ({config.url})")

            mode = "standard" if args.full_actions else "mock_targets"
            env = WebSecEnv(target_url=config.url, mode=mode)

            plan = build_action_plan(env, args.full_actions)
            if not plan:
                print("  No actions found to test.")
                env.close()
                overall_failures += 1
                continue

            env.max_steps_per_episode = len(plan) + 5

            results: List[ActionResult] = []
            if not reset_each:
                env.reset()

            for action_id, real_action_id, action_name in plan:
                if reset_each:
                    env.reset()
                result = run_action(env, action_id, real_action_id, action_name)
                results.append(result)
                if not reset_each and result.request_error:
                    env.reset()

            summary = summarize_results(results)
            overall_actions += summary["total"]
            overall_failures += summary["request_errors"] + summary["no_response"]

            print(
                "  Summary: "
                f"total={summary['total']} "
                f"response_ok={summary['response_ok']} "
                f"no_response={summary['no_response']} "
                f"request_errors={summary['request_errors']}"
            )
            print_failures(results, verbose=args.verbose)
            env.close()
    finally:
        for process in processes.values():
            stop_process(process)

    print(
        f"\nOverall: actions={overall_actions} failures={overall_failures} "
        f"(mode={'full' if args.full_actions else 'mock'})"
    )

    return 0 if overall_failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
