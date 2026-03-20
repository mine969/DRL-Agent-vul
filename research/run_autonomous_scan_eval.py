import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evaluate_fill_excel import TARGETS, classify, impact_for, parse_report_findings, run_ground_truth_scan


@dataclass(frozen=True)
class ScanConfig:
    runs: int
    depth: int
    intensity: int
    model: str
    timeout: int
    ai_mode: bool
    persist: bool
    pentester: bool


def default_model_path() -> str:
    candidates = [
        Path("checkpoints_backup_v21_success/multi_target_10k_ep10100.pth"),
        Path("legacy/dqn_web_sec_model.pth"),
        Path("dqn_web_sec_model.pth"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return str(candidates[0])


def is_reachable(url: str, timeout: float = 1.0) -> bool:
    try:
        requests.get(url, timeout=timeout)
        return True
    except requests.RequestException:
        return False


def wait_for_target(url: str, timeout_seconds: float = 20.0) -> bool:
    start = time.time()
    while time.time() - start < timeout_seconds:
        if is_reachable(url):
            return True
        time.sleep(0.5)
    return False


def start_target(config, startup_timeout: float = 20.0):
    if is_reachable(config.url):
        return None, True, "already_running"

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    process = subprocess.Popen(
        [sys.executable, config.app],
        cwd=str(ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=env,
    )
    ok = wait_for_target(config.url, timeout_seconds=startup_timeout)
    return process, ok, "started" if ok else "failed_to_start"


def stop_process(process):
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


def snapshot_reports():
    return set(Path("reports").glob("*.md"))


def newest_path(paths):
    if not paths:
        return None
    return max(paths, key=lambda item: item.stat().st_ctime)


def find_report_after(before_snapshot):
    after_snapshot = set(Path("reports").glob("*.md"))
    new_reports = list(after_snapshot - before_snapshot)
    if new_reports:
        return newest_path(new_reports)
    return newest_path(list(after_snapshot))


def deduped_category_counts(report_path: Path):
    findings = parse_report_findings(report_path)
    found = defaultdict(set)
    for finding in findings:
        technical_name = (finding.get("technical_name") or "").strip()
        if not technical_name:
            continue
        category = classify(technical_name)
        if category == "Other":
            continue
        found[category].add(technical_name)
    return {category: len(items) for category, items in found.items()}


def build_scan_command(target_url: str, config: ScanConfig):
    command = [
        sys.executable,
        "autonomous_scan.py",
        target_url,
        "--depth",
        str(config.depth),
        "--intensity",
        str(config.intensity),
        "--model",
        config.model,
    ]
    if config.ai_mode:
        command.append("--ai-mode")
    if config.persist:
        command.append("--persist")
    if config.pentester:
        command.append("--pentester")
    return command


def run_single_scan(target_key: str, target_cfg, run_index: int, config: ScanConfig, logs_dir: Path):
    log_path = logs_dir / f"{target_key}_run_{run_index + 1}.log"
    command = build_scan_command(target_cfg.url, config)
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"

    with log_path.open("w", encoding="utf-8", errors="ignore") as log_file:
        log_file.write("COMMAND: " + " ".join(command) + "\n\n")
        completed = subprocess.run(
            command,
            cwd=str(ROOT),
            stdout=log_file,
            stderr=subprocess.STDOUT,
            timeout=config.timeout,
            check=False,
            env=env,
        )

    report_path = newest_path(list(Path("reports").glob("*.md")))
    if completed.returncode != 0:
        raise RuntimeError(
            f"Scan failed for {target_cfg.name} run {run_index + 1}. See {log_path}"
        )
    if report_path is None or not report_path.exists():
        raise RuntimeError(
            f"No report generated for {target_cfg.name} run {run_index + 1}. See {log_path}"
        )

    archived_report = logs_dir / f"{target_key}_run_{run_index + 1}_report.md"
    shutil.copyfile(report_path, archived_report)

    return {
        "run": run_index + 1,
        "report": str(archived_report).replace("\\", "/"),
        "log": str(log_path).replace("\\", "/"),
        "category_counts": deduped_category_counts(archived_report),
    }


def build_markdown_table(results):
    lines = [
        "| Website | Vulnerability Type | Total Existing | Average Findings (5 Runs) | Detection Rate | Severity |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]

    for target_key in ["ecommerce", "social", "banking", "blog", "fileshare"]:
        if target_key not in results["targets"]:
            continue
        target = results["targets"][target_key]
        for row in target["rows"]:
            lines.append(
                "| {website} | {category} | {total} | {average} | {rate} | {severity} |".format(
                    website=target["name"],
                    category=row["category"],
                    total=row["total_existing"],
                    average=row["average_detected"],
                    rate=row["detection_rate"],
                    severity=row["severity"],
                )
            )
    return "\n".join(lines) + "\n"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run autonomous_scan.py repeatedly across mock targets and average findings."
    )
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--depth", type=int, default=20)
    parser.add_argument("--intensity", type=int, default=5)
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--model", default=default_model_path())
    parser.add_argument(
        "--targets",
        nargs="+",
        choices=list(TARGETS.keys()),
        default=list(TARGETS.keys()),
    )
    parser.add_argument(
        "--output-json",
        default="research/results/autonomous_scan_average_findings.json",
    )
    parser.add_argument(
        "--output-md",
        default="research/results/autonomous_scan_average_findings.md",
    )
    parser.add_argument("--ai-mode", action="store_true")
    parser.add_argument("--persist", action="store_true")
    parser.add_argument("--pentester", action="store_true")
    return parser.parse_args()


def main():
    os.chdir(ROOT)
    args = parse_args()
    config = ScanConfig(
        runs=max(1, args.runs),
        depth=max(1, args.depth),
        intensity=max(1, args.intensity),
        model=str(Path(args.model)),
        timeout=max(60, args.timeout),
        ai_mode=bool(args.ai_mode),
        persist=bool(args.persist),
        pentester=bool(args.pentester),
    )

    if not Path(config.model).exists():
        raise FileNotFoundError(f"Model checkpoint not found: {config.model}")

    Path("reports").mkdir(exist_ok=True)
    logs_dir = Path("research/results/autonomous_scan_logs")
    logs_dir.mkdir(parents=True, exist_ok=True)

    processes = {}
    all_ok = True

    print(f"Model: {config.model}")
    print(f"Runs per target: {config.runs}")
    print(f"Depth: {config.depth} | Intensity: {config.intensity}")
    print(f"AI mode: {config.ai_mode} | Persist: {config.persist} | Pentester: {config.pentester}")
    print("Starting targets...")

    for target_key, target_cfg in TARGETS.items():
        if target_key not in args.targets:
            continue
        process, ok, status = start_target(target_cfg)
        processes[target_key] = process
        print(f"- {target_cfg.name}: {status}")
        if not ok:
            all_ok = False

    if not all_ok:
        for process in processes.values():
            stop_process(process)
        raise SystemExit(1)

    results = {
        "config": {
            "runs": config.runs,
            "depth": config.depth,
            "intensity": config.intensity,
            "model": config.model.replace("\\", "/"),
            "timeout": config.timeout,
            "ai_mode": config.ai_mode,
            "persist": config.persist,
            "pentester": config.pentester,
        },
        "targets": {},
    }

    try:
        for target_key, target_cfg in TARGETS.items():
            if target_key not in args.targets:
                continue
            if not is_reachable(target_cfg.url):
                replacement_process, ok, status = start_target(target_cfg)
                if replacement_process is not None:
                    stop_process(processes.get(target_key))
                    processes[target_key] = replacement_process
                if not ok:
                    raise RuntimeError(f"Target not reachable: {target_cfg.name} ({status})")

            print(f"\nRunning scans for {target_cfg.name}...")
            ground_truth = run_ground_truth_scan(target_cfg.app)
            scan_runs = []
            for run_index in range(config.runs):
                print(f"  Run {run_index + 1}/{config.runs}")
                scan_runs.append(
                    run_single_scan(target_key, target_cfg, run_index, config, logs_dir)
                )

            ordered_categories = list(ground_truth.keys())
            rows = []
            for category in ordered_categories:
                total_existing = len(ground_truth[category])
                if total_existing == 0:
                    continue
                per_run_counts = [
                    min(run_data["category_counts"].get(category, 0), total_existing)
                    for run_data in scan_runs
                ]
                average_detected = round(sum(per_run_counts) / len(per_run_counts), 1)
                detection_rate = f"{(average_detected / total_existing) * 100:.1f}%"
                rows.append(
                    {
                        "category": category,
                        "total_existing": total_existing,
                        "per_run_counts": per_run_counts,
                        "average_detected": int(average_detected)
                        if average_detected.is_integer()
                        else average_detected,
                        "detection_rate": detection_rate,
                        "severity": str(impact_for(category)).title(),
                    }
                )

            results["targets"][target_key] = {
                "name": target_cfg.name,
                "url": target_cfg.url,
                "app": target_cfg.app,
                "runs": scan_runs,
                "rows": rows,
            }
    finally:
        for process in processes.values():
            stop_process(process)

    output_json = Path(args.output_json)
    output_md = Path(args.output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)

    output_json.write_text(json.dumps(results, indent=2), encoding="utf-8")
    output_md.write_text(build_markdown_table(results), encoding="utf-8")

    print(f"\nSaved JSON results to {output_json}")
    print(f"Saved Markdown table to {output_md}")


if __name__ == "__main__":
    main()
