"""
Easy Scanner - User Friendly Interface for AI Security Auditor
Interactive by default, with optional non-interactive auto mode flags.
"""

import os
import sys
import glob
import re
import subprocess
import time
import webbrowser
import urllib.request
import urllib.error
import argparse

# ANSI Colors
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"

TARGET_LABELS = {
    "http://localhost:5002": "E-Commerce Platform",
    "http://localhost:5003": "Social Media Platform",
    "http://localhost:5004": "Banking Application",
    "http://localhost:5005": "Blog Platform",
    "http://localhost:5006": "File Sharing Platform",
}

EXPECTED_VULNS = {
    "http://localhost:5002": [
        "SQL Injection",
        "Mass Assignment",
        "Business Logic Flaws",
        "Race Conditions",
        "IDOR",
        "Payment Bypass",
        "Broken Access Control",
    ],
    "http://localhost:5003": [
        "Stored/Reflected XSS",
        "File Upload",
        "Path Traversal",
        "IDOR",
        "CSRF",
        "Session Fixation",
        "Predictable Reset Tokens",
    ],
    "http://localhost:5004": [
        "CSRF",
        "IDOR",
        "Session Security Issues",
        "Logic Flaws",
    ],
    "http://localhost:5005": [
        "Stored XSS",
        "SSTI",
        "CSRF",
        "Weak Authentication",
    ],
    "http://localhost:5006": [
        "File Upload",
        "Path Traversal",
        "IDOR",
        "No File Type Validation",
    ],
}

SCAN_MODES = {
    "hybrid": {
        "label": "Hybrid-Driven Scan",
        "description": "Scripted recon + AI testing (default depth/intensity matched).",
        "config": {
            "depth": 30,
            "intensity": 3,
            "persist": True,
            "ai_mode": False,
            "pentester": False,
        },
    },
    "ai": {
        "label": "AI-Driven Scan",
        "description": "AI recon + online learning (default depth/intensity matched).",
        "config": {
            "depth": 30,
            "intensity": 3,
            "persist": True,
            "ai_mode": True,
            "pentester": False,
        },
    },
}

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def print_banner():
    clear_screen()
    print(f"{CYAN}{BOLD}")
    print("================================================================")
    print("================================================================")
    print("      [+] AI VULNERABILITY SCANNER - MOCK TARGETS [+]")
    print("================================================================")
    print(f"{RESET}")


def _extract_episode(filename):
    match = re.search(r"ep(\d+)", filename)
    if match:
        return int(match.group(1))
    return None


def _model_sort_key(model):
    kind_priority = 0 if model["kind"] == "checkpoint" else 1
    ep_present = 0 if model["ep"] is not None else 1
    ep_value = -model["ep"] if model["ep"] is not None else 0
    return (kind_priority, ep_present, ep_value, -model["mtime"])


def _format_model_label(model):
    label = model["name"]
    if model["kind"] == "base":
        return f"{label} (Base)"
    if model["ep"] is not None:
        return f"{label} (ep {model['ep']})"
    return label


def get_available_models():
    """Find available models (checkpoints + base models)."""
    models = []

    base_models = ["dqn_web_sec_model.pth", "dqn_juiceshop_model.pth"]
    for path in base_models:
        if os.path.exists(path):
            models.append(
                {
                    "path": path,
                    "ep": None,
                    "name": os.path.basename(path),
                    "kind": "base",
                    "mtime": os.path.getmtime(path),
                }
            )

    checkpoint_paths = glob.glob(os.path.join("checkpoints", "*.pth"))
    for path in checkpoint_paths:
        filename = os.path.basename(path)
        models.append(
            {
                "path": path,
                "ep": _extract_episode(filename),
                "name": filename,
                "kind": "checkpoint",
                "mtime": os.path.getmtime(path),
            }
        )

    deduped = {}
    for model in models:
        norm_path = os.path.normpath(model["path"])
        deduped[norm_path] = model

    sorted_models = list(deduped.values())
    sorted_models.sort(key=_model_sort_key)
    return sorted_models


def select_model():
    print(f"{YELLOW}[?] Select AI Brain Model:{RESET}")
    models = get_available_models()

    if not models:
        print(
            f"{RED}[!] No models found in checkpoints/ or project root!{RESET}"
        )
        print("   Train one with: python train_mock_targets.py --episodes 1000")
        input("Press Enter to exit...")
        sys.exit(1)

    best_model = models[0]
    print(
        f"   {BOLD}0. Auto-Select Best Model ({_format_model_label(best_model)}){RESET}"
    )

    max_display = min(8, len(models))
    for i, m in enumerate(models[:max_display], 1):
        print(f"   {i}. {_format_model_label(m)}")

    choice = input(
        f"\n{CYAN}>>> Select option (0-{max_display}): {RESET}"
    )
    if not choice or choice == "0":
        return best_model["path"]

    try:
        idx = int(choice) - 1
        if 0 <= idx < max_display:
            return models[idx]["path"]
    except:
        pass

    print(f"{RED}Invalid selection, defaulting to best model.{RESET}")
    time.sleep(1)
    return best_model["path"]


def select_target():
    print(f"\n{YELLOW}[?] Select Target Application:{RESET}")
    targets = [
        {"name": "E-Commerce Platform", "url": "http://localhost:5002"},
        {"name": "Social Media Platform", "url": "http://localhost:5003"},
        {"name": "Banking Application", "url": "http://localhost:5004"},
        {"name": "Blog Platform", "url": "http://localhost:5005"},
        {"name": "File Sharing Platform", "url": "http://localhost:5006"},
        {"name": "Custom URL", "url": "CUSTOM"},
        {"name": "Scan ALL Mock Sites", "url": "ALL"},
    ]

    for i, t in enumerate(targets, 1):
        if t["url"] == "ALL":
            print(f"   {i}. {BOLD}{t['name']:<25}{RESET}")
        else:
            print(f"   {i}. {t['name']:<25} - {t['url']}")

    choice = input(f"\n{CYAN}>>> Select target (1-7): {RESET}")

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(targets):
            selected = targets[idx]

            if selected["url"] == "ALL":
                # Return list of all localhost targets
                return [t["url"] for t in targets if "localhost" in t["url"]]

            if selected["url"] == "CUSTOM":
                custom_url = input(
                    f"{YELLOW}>>> Enter Target URL (e.g. http://example.com): {RESET}"
                )
                if not custom_url.startswith("http"):
                    custom_url = "http://" + custom_url
                return [custom_url]

            return [selected["url"]]
    except:
        pass

    print(f"{RED}Invalid selection!{RESET}")
    return []


def get_scan_config(scan_mode):
    mode = SCAN_MODES.get(scan_mode)
    if not mode:
        return SCAN_MODES["hybrid"]["config"]
    return mode["config"]


def _prompt_int(prompt, default_value, min_value=1):
    choice = input(f"{prompt} [Default: {default_value}]: ")
    if not choice:
        return default_value
    try:
        value = int(choice)
        if value < min_value:
            raise ValueError
        return value
    except ValueError:
        print(f"{RED}Invalid input, using default {default_value}.{RESET}")
        time.sleep(1)
        return default_value


def find_latest_report():
    """Finds the most recently created Markdown report."""
    list_of_files = glob.glob("reports/*.md")
    if not list_of_files:
        return None
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file


def open_report(report_path):
    """Opens the report in the default browser/viewer."""
    try:
        abs_path = os.path.abspath(report_path)
        print(f"Opening: {abs_path}")
        webbrowser.open(abs_path)
    except Exception as e:
        print(f"{RED}Failed to open report: {e}{RESET}")


def select_run_mode():
    print(f"{YELLOW}[?] Choose Scan Mode:{RESET}")
    print(
        f"   {BOLD}1. {SCAN_MODES['hybrid']['label']}{RESET} - {SCAN_MODES['hybrid']['description']}"
    )
    print(
        f"   {BOLD}2. {SCAN_MODES['ai']['label']}{RESET} - {SCAN_MODES['ai']['description']}"
    )
    print(f"   {BOLD}3. Open Latest Report{RESET}")
    print(f"   {BOLD}4. Exit{RESET}")
    choice = input(f"\n{CYAN}>>> Select option (1-4) [Default: 1]: {RESET}")

    if not choice or choice == "1":
        return "hybrid"
    if choice == "2":
        return "ai"
    if choice == "3":
        return "report"
    if choice == "4":
        return "exit"

    print(f"{RED}Invalid selection, defaulting to Hybrid-Driven Scan.{RESET}")
    time.sleep(1)
    return "hybrid"


def _is_url_reachable(url, timeout=2):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout):
            return True
    except urllib.error.HTTPError:
        return True
    except Exception:
        return False


def check_targets_reachable(target_urls):
    offline = []
    for url in target_urls:
        if not _is_url_reachable(url):
            offline.append(url)
    return offline


def print_scan_intro():
    print(
        f"\n{YELLOW}[Info] Authorized testing only. Local mock targets recommended.{RESET}"
    )
    print("   - Start mock apps with: python start_services.py")


def print_expected_vulns(target_urls):
    print(f"\n{YELLOW}[Expected] Target vulnerability coverage:{RESET}")
    for url in target_urls:
        label = TARGET_LABELS.get(url, url)
        expected = EXPECTED_VULNS.get(url)
        if expected:
            print(f"   - {label}: {', '.join(expected)}")
        else:
            print(f"   - {label}: No expected list available")


def snapshot_reports():
    return set(glob.glob("reports/*.md"))


def find_new_report(before_snapshot):
    after_snapshot = set(glob.glob("reports/*.md"))
    new_reports = list(after_snapshot - before_snapshot)
    if new_reports:
        return max(new_reports, key=os.path.getctime)
    return find_latest_report()


def parse_confirmed_vulns(report_path):
    if not report_path or not os.path.exists(report_path):
        return []

    try:
        with open(report_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception:
        return []

    confirmed = []
    in_section = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## ") and "Confirmed Vulnerabilities" in stripped:
            in_section = True
            continue
        if in_section and stripped.startswith("## "):
            break
        if in_section and stripped.startswith("### "):
            title = stripped[4:]
            if ". " in title:
                title = title.split(". ", 1)[1]
            title = re.sub(r"[^\x00-\x7F]+", "", title).strip()
            if title:
                confirmed.append(title)
    deduped = []
    seen = set()
    for name in confirmed:
        if name not in seen:
            deduped.append(name)
            seen.add(name)
    return deduped


def print_scan_summary(url, report_path):
    label = TARGET_LABELS.get(url, url)
    expected = EXPECTED_VULNS.get(url, [])
    if expected:
        print(
            f"\n{GREEN}[Expected] {label}: {', '.join(expected)}{RESET}"
        )
    else:
        print(f"\n{YELLOW}[Expected] No list available for {label}.{RESET}")

    confirmed = parse_confirmed_vulns(report_path)
    if confirmed:
        print(
            f"{GREEN}[Summary] Confirmed in latest report: {', '.join(confirmed)}{RESET}"
        )
    else:
        print(
            f"{YELLOW}[Summary] No confirmed vulnerabilities detected in the latest report.{RESET}"
        )
        print("   Tip: Try AI-Driven mode or a more trained model.")


def build_subprocess_env():
    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")
    return env


def build_scan_command(url, model_path, config):
    cmd = [
        sys.executable,
        "autonomous_scan.py",
        url,
        "--model",
        model_path,
        "--depth",
        str(config["depth"]),
        "--intensity",
        str(config["intensity"]),
    ]

    if config.get("persist"):
        cmd.append("--persist")
    if config.get("ai_mode"):
        cmd.append("--ai-mode")
    if config.get("pentester"):
        cmd.append("--pentester")

    return cmd




def normalize_target_url(url):
    value = (url or "").strip()
    if not value:
        return ""
    if not value.startswith(("http://", "https://")):
        value = "http://" + value
    return value


def resolve_model_path(model_arg=None):
    if model_arg:
        if os.path.exists(model_arg):
            return model_arg
        print(f"{RED}[!] Model not found: {model_arg}{RESET}")
        return None

    models = get_available_models()
    if models:
        return models[0]["path"]

    print(f"{RED}[!] No model found in checkpoints/ or project root.{RESET}")
    return None


def resolve_auto_targets(target_arg=None, all_targets=False):
    if all_targets:
        return list(TARGET_LABELS.keys())

    if not target_arg:
        return []

    targets = []
    for raw in target_arg.split(","):
        target = normalize_target_url(raw)
        if target:
            targets.append(target)

    deduped = []
    seen = set()
    for target in targets:
        if target not in seen:
            deduped.append(target)
            seen.add(target)
    return deduped


def run_auto_scan(args):
    scan_mode = args.mode
    config = get_scan_config(scan_mode).copy()

    if args.depth is not None:
        config["depth"] = max(1, args.depth)
    if args.intensity is not None:
        config["intensity"] = max(1, args.intensity)
    if args.persist is not None:
        config["persist"] = args.persist

    model_path = resolve_model_path(args.model)
    if not model_path:
        return False

    target_urls = resolve_auto_targets(args.target, args.all_targets)
    if not target_urls:
        print(
            f"{RED}[!] No targets selected. Use --target <url> or --all-targets with --auto.{RESET}"
        )
        return False

    print_scan_intro()
    print_expected_vulns(target_urls)

    mode_label = SCAN_MODES.get(scan_mode, {}).get("label", scan_mode)
    print()
    print(f"{GREEN}[OK] Auto Mode Enabled{RESET}")
    print(f"{GREEN}[OK] Mode: {mode_label}{RESET}")
    print(f"{GREEN}[OK] Model: {os.path.basename(model_path)}{RESET}")
    print(
        f"{GREEN}[OK] Config: Depth={config['depth']}, Intensity={config['intensity']}, Persist={config['persist']}{RESET}"
    )

    offline = check_targets_reachable(target_urls)
    if offline:
        print()
        print(f"{YELLOW}[Info] Some targets are not reachable:{RESET}")
        for url in offline:
            print(f"   - {url}")
        print("   Continuing because --auto mode is enabled.")

    last_report = None
    for i, url in enumerate(target_urls, 1):
        if len(target_urls) > 1:
            print()
            print(f"{CYAN}{BOLD}>>> STARTING SCAN {i}/{len(target_urls)}: {url}{RESET}")

        before_reports = snapshot_reports()
        cmd = build_scan_command(url, model_path, config)
        print()
        print(f"{CYAN}Scanning {url}...{RESET}")
        print()

        try:
            subprocess.run(cmd, env=build_subprocess_env())
        except KeyboardInterrupt:
            print()
            print(f"{RED}Scan interrupted by user.{RESET}")
            break

        last_report = find_new_report(before_reports)
        print_scan_summary(url, last_report)

    latest_report = last_report or find_latest_report()
    if latest_report:
        print()
        print(f"{GREEN}[+] Latest Report: {latest_report}{RESET}")
        if args.open_report:
            open_report(latest_report)
    else:
        print()
        print(f"{RED}[!] No report found.{RESET}")

    return True


def parse_cli_args():
    parser = argparse.ArgumentParser(
        description="Easy Scanner - interactive CLI + optional auto mode"
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Run non-interactive scan mode (no prompts).",
    )
    parser.add_argument(
        "--mode",
        choices=["hybrid", "ai"],
        default="hybrid",
        help="Scan mode to use in --auto mode (default: hybrid).",
    )
    parser.add_argument(
        "--target",
        help="Single target URL or comma-separated target URLs (auto mode).",
    )
    parser.add_argument(
        "--all-targets",
        action="store_true",
        help="Scan all built-in localhost mock targets (auto mode).",
    )
    parser.add_argument(
        "--model",
        help="Path to model file (auto mode). Defaults to best available model.",
    )
    parser.add_argument("--depth", type=int, help="Override crawl depth (auto mode).")
    parser.add_argument(
        "--intensity", type=int, help="Override attack intensity (auto mode)."
    )
    persist_group = parser.add_mutually_exclusive_group()
    persist_group.add_argument(
        "--persist",
        dest="persist",
        action="store_true",
        help="Force persistence mode on (auto mode).",
    )
    persist_group.add_argument(
        "--no-persist",
        dest="persist",
        action="store_false",
        help="Force persistence mode off (auto mode).",
    )
    parser.set_defaults(persist=None)
    parser.add_argument(
        "--open-report",
        action="store_true",
        help="Automatically open the latest report after scan (auto mode).",
    )
    return parser.parse_args()


def run_scan_flow(scan_mode):
    print_scan_intro()

    # 1. Model
    model_path = select_model()
    print(f"{GREEN}[OK] Loaded Model: {os.path.basename(model_path)}{RESET}")

    # 2. Target
    target_urls = select_target()
    if not target_urls:
        time.sleep(1)
        return False

    if len(target_urls) > 1:
        print(f"{GREEN}[OK] Selected {len(target_urls)} Targets for Batch Scan{RESET}")
    else:
        print(f"{GREEN}[OK] Target Set: {target_urls[0]}{RESET}")

    offline = check_targets_reachable(target_urls)
    if offline:
        print(f"\n{YELLOW}[Info] Some targets are not reachable:{RESET}")
        for url in offline:
            print(f"   - {url}")
        print("   Start mock apps with: python start_services.py")
        proceed = input(f"{CYAN}>>> Continue anyway? (y/N): {RESET}")
        if proceed.lower() != "y":
            return False

    print_expected_vulns(target_urls)

    # 3. Apply scan mode config
    config = get_scan_config(scan_mode).copy()
    mode_label = SCAN_MODES.get(scan_mode, {}).get("label", scan_mode)
    print(
        f"{GREEN}[OK] Mode: {mode_label}{RESET}"
        f"\n{GREEN}[OK] Scan Configured: Depth={config['depth']}, Intensity={config['intensity']}{RESET}"
    )

    customize = input(f"{CYAN}>>> Customize intensity? (y/N): {RESET}")
    if customize.lower() == "y":
        config["intensity"] = _prompt_int(
            f"{CYAN}>>> Enter scan intensity{RESET}", config["intensity"]
        )
        print(
            f"{GREEN}[OK] Custom Intensity Set: {config['intensity']}{RESET}"
        )

    # Confirm
    print(f"\n{YELLOW}Ready to scan {len(target_urls)} target(s)?{RESET}")
    input(f"Press {BOLD}ENTER{RESET} to start scanning...")

    last_report = None

    # Batch Scan Loop
    for i, url in enumerate(target_urls, 1):
        if len(target_urls) > 1:
            print(
                f"\n{CYAN}{BOLD}>>> STARTING SCAN {i}/{len(target_urls)}: {url}{RESET}"
            )

        before_reports = snapshot_reports()

        # Build Command
        cmd = build_scan_command(url, model_path, config)

        # Run
        print(f"\n{CYAN}Scanning {url}... (Press Ctrl+C to skip/stop){RESET}\n")
        try:
            subprocess.run(cmd, env=build_subprocess_env())
        except KeyboardInterrupt:
            print(f"\n{RED}Scan interrupted by user.{RESET}")
            if len(target_urls) > 1:
                skip = input(f"\n{YELLOW}Skip remaining targets? (y/N): {RESET}")
                if skip.lower() == "y":
                    break

        last_report = find_new_report(before_reports)
        print_scan_summary(url, last_report)

    print(f"\n{YELLOW}Batch Scan finished.{RESET}")

    latest_report = last_report or find_latest_report()
    if latest_report:
        print(f"\n{GREEN}[+] Latest Report: {latest_report}{RESET}")
        open_invitation = input(f"{CYAN}>>> Open latest report? (Y/n): {RESET}")
        if open_invitation.lower() != "n":
            open_report(latest_report)
    else:
        print(f"\n{RED}[!] No report found.{RESET}")

    return True


def main():
    while True:
        print_banner()

        mode = select_run_mode()
        if mode == "exit":
            print("\nGoodbye!")
            break

        if mode == "report":
            latest_report = find_latest_report()
            if latest_report:
                print(f"\n{GREEN}[+] Latest Report: {latest_report}{RESET}")
                open_invitation = input(f"{CYAN}>>> Open latest report? (Y/n): {RESET}")
                if open_invitation.lower() != "n":
                    open_report(latest_report)
            else:
                print(f"\n{RED}[!] No report found.{RESET}")
            input(f"\n{CYAN}Press ENTER to return to menu...{RESET}")
            continue

        if mode in ("hybrid", "ai") and not run_scan_flow(mode):
            continue

        choice = input(f"\n{CYAN}>>> Scan another target? (y/n): {RESET}")
        if choice.lower() != "y":
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    os.chdir(PROJECT_ROOT)
    args = parse_cli_args()
    try:
        if args.auto:
            success = run_auto_scan(args)
            if not success:
                sys.exit(1)
        else:
            main()
    except KeyboardInterrupt:
        print("\nGoodbye!")
