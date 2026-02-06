import os
import sys
import time
import subprocess
import io
import re
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Iterable, List, Set, Tuple
from collections import defaultdict

import requests
import openpyxl

from utils.vulnerability_database import VULNERABILITY_DATABASE


@dataclass
class TargetConfig:
    name: str
    url: str
    app: str
    port: int


TARGETS: Dict[str, TargetConfig] = {
    "ecommerce": TargetConfig(
        name="E-Commerce (5002)",
        url="http://localhost:5002",
        app="env/target_app_ecommerce.py",
        port=5002,
    ),
    "social": TargetConfig(
        name="Social Media (5003)",
        url="http://localhost:5003",
        app="env/target_app_social.py",
        port=5003,
    ),
    "banking": TargetConfig(
        name="Banking (5004)",
        url="http://localhost:5004",
        app="env/target_app_banking.py",
        port=5004,
    ),
    "blog": TargetConfig(
        name="Blog (5005)",
        url="http://localhost:5005",
        app="env/target_app_blog.py",
        port=5005,
    ),
    "fileshare": TargetConfig(
        name="File Share (5006)",
        url="http://localhost:5006",
        app="env/target_app_fileshare.py",
        port=5006,
    ),
}

MODEL_PATH = "checkpoints/improved_mock_ep6000.pth"
SCAN_DEPTH = 120
SCAN_INTENSITY = 10
SCAN_PERSIST = True
SCAN_AI_MODE = True
SCAN_PENTESTER = True
SCAN_TIMEOUT_SECONDS = 1800
TARGET_STARTUP_TIMEOUT_SECONDS = 20.0


@dataclass(frozen=True)
class ScanPassConfig:
    name: str
    depth: int
    intensity: int
    persist: bool
    ai_mode: bool
    pentester: bool
    timeout_seconds: int


SCAN_PASSES: Tuple[ScanPassConfig, ...] = (
    ScanPassConfig(
        name="broad_ai",
        depth=SCAN_DEPTH,
        intensity=SCAN_INTENSITY,
        persist=SCAN_PERSIST,
        ai_mode=SCAN_AI_MODE,
        pentester=False,
        timeout_seconds=SCAN_TIMEOUT_SECONDS,
    ),
    ScanPassConfig(
        name="chain_attack",
        depth=max(60, SCAN_DEPTH // 2),
        intensity=SCAN_INTENSITY,
        persist=True,
        ai_mode=True,
        pentester=SCAN_PENTESTER,
        timeout_seconds=SCAN_TIMEOUT_SECONDS,
    ),
)


if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True
    )
    sys.stderr = io.TextIOWrapper(
        sys.stderr.buffer, encoding="utf-8", errors="replace", line_buffering=True
    )


CATEGORY_ORDER = [
    "SQL Injection",
    "Cross-Site Scripting (XSS)",
    "Insecure Direct Object Reference (IDOR)",
    "Broken Access Control (BAC)",
    "Cross-Site Request Forgery (CSRF)",
    "File Upload",
    "Path Traversal",
    "Server-Side Template Injection (SSTI)",
    "Server-Side Request Forgery (SSRF)",
    "Command Injection",
    "Insecure Deserialization",
    "Mass Assignment",
    "Business Logic",
    "Sensitive Data Exposure",
    "Weak Password",
    "Session Fixation",
    "Weak Reset Token",
    "OAuth Bypass",
    "JWT Bypass",
    "SAML Bypass",
]


CUSTOM_IMPACT = {
    "File Upload": "CRITICAL",
    "Mass Assignment": "HIGH",
    "Business Logic": "MEDIUM",
    "Weak Password": "HIGH",
    "Session Fixation": "HIGH",
    "Weak Reset Token": "HIGH",
    "OAuth Bypass": "HIGH",
    "JWT Bypass": "HIGH",
    "SAML Bypass": "HIGH",
}


def is_reachable(url: str, timeout: float = 1.0) -> bool:
    try:
        requests.get(url, timeout=timeout)
        return True
    except requests.RequestException:
        return False


def wait_for_target(url: str, timeout_seconds: float = 12.0) -> bool:
    start = time.time()
    while time.time() - start < timeout_seconds:
        if is_reachable(url):
            return True
        time.sleep(0.5)
    return False


def start_target(config: TargetConfig, startup_timeout: float = 12.0):
    if is_reachable(config.url):
        return None, True, "already_running"

    process = subprocess.Popen(
        [sys.executable, config.app],
        cwd=os.getcwd(),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    ok = wait_for_target(config.url, timeout_seconds=startup_timeout)
    status = "started" if ok else "failed_to_start"
    return process, ok, status


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


def classify(action_name: str) -> str:
    if not action_name:
        return "Other"
    raw = action_name.lower()
    name = re.sub(r"[^a-z0-9]+", "_", raw)

    if "weak_password" in name or name == "test_weak_passwords":
        return "Weak Password"
    if "session_fixation" in name:
        return "Session Fixation"
    if "password_reset" in name or "reset_token" in name or "predictable_reset" in name:
        return "Weak Reset Token"
    if "oauth" in name:
        return "OAuth Bypass"
    if "jwt" in name:
        return "JWT Bypass"
    if "saml" in name:
        return "SAML Bypass"

    if "sqli" in name or "sql_injection" in name or " sql " in f" {raw} ":
        return "SQL Injection"
    if "xss" in name:
        return "Cross-Site Scripting (XSS)"
    if "idor" in name:
        return "Insecure Direct Object Reference (IDOR)"
    if name.startswith("attack_bac_") or "bac_" in name:
        return "Broken Access Control (BAC)"
    if "csrf" in name:
        return "Cross-Site Request Forgery (CSRF)"
    if "file_upload" in name or ("upload" in name and "idor" not in name):
        return "File Upload"
    if "path_traversal" in name or "traversal" in name:
        return "Path Traversal"
    if "ssti" in name:
        return "Server-Side Template Injection (SSTI)"
    if "ssrf" in name:
        return "Server-Side Request Forgery (SSRF)"
    if "command_injection" in name or "cmd_injection" in name or "shell_injection" in name:
        return "Command Injection"
    if "deserialization" in name:
        return "Insecure Deserialization"
    if "mass_assignment" in name:
        return "Mass Assignment"
    if any(token in name for token in ["negative_quantity", "price_", "payment", "coupon", "race_"]):
        return "Business Logic"
    if "info_disclosure" in name or "insecure_api_keys" in name or "secret" in name:
        return "Sensitive Data Exposure"

    return "Other"


def impact_for(category: str) -> str:
    if category in VULNERABILITY_DATABASE:
        return VULNERABILITY_DATABASE[category].get("impact", "UNKNOWN")
    if category in CUSTOM_IMPACT:
        return CUSTOM_IMPACT[category]
    return "MEDIUM"


def run_ground_truth_scan(app_path: str):
    found = defaultdict(set)

    patterns = [
        ("SQL Injection", "sql_injection", [["sql injection"], ["sqli"]]),
        ("Cross-Site Scripting (XSS)", "xss", [["xss"]]),
        ("Insecure Direct Object Reference (IDOR)", "idor", [["idor"]]),
        ("Cross-Site Request Forgery (CSRF)", "csrf", [["csrf"]]),
        (
            "File Upload",
            "file_upload",
            [["file upload"], ["unrestricted upload"], ["upload"]],
        ),
        ("Path Traversal", "path_traversal", [["path traversal"], ["traversal"]]),
        (
            "Server-Side Template Injection (SSTI)",
            "ssti",
            [["ssti"], ["template injection"]],
        ),
        ("Server-Side Request Forgery (SSRF)", "ssrf", [["ssrf"]]),
        ("Command Injection", "command_injection", [["command injection"]]),
        ("Mass Assignment", "mass_assignment", [["mass assignment"]]),
        ("Weak Password", "weak_password", [["weak password"]]),
        ("Session Fixation", "session_fixation", [["session fixation"]]),
        (
            "Weak Reset Token",
            "weak_reset",
            [["reset token"], ["predictable reset"]],
        ),
        (
            "OAuth Bypass",
            "oauth_bypass",
            [["oauth", "state"], ["oauth", "bypass"]],
        ),
        (
            "JWT Bypass",
            "jwt_bypass",
            [["jwt", "alg"], ["jwt", "none"], ["jwt", "bypass"], ["jwt", "signature"]],
        ),
        (
            "SAML Bypass",
            "saml_bypass",
            [["saml", "bypass"], ["saml", "signature"], ["saml", "xml"]],
        ),
        (
            "Sensitive Data Exposure",
            "info_disclosure",
            [["info disclosure"], ["secret leak"], ["secret key"], ["exposure"]],
        ),
        ("Business Logic", "negative_quantity", [["negative quantity"]]),
        ("Business Logic", "price_manipulation", [["price manipulation"]]),
        ("Business Logic", "coupon_abuse", [["coupon abuse"]]),
        ("Business Logic", "race_condition", [["race condition"]]),
        ("Business Logic", "payment_bypass", [["payment bypass"]]),
    ]

    route_re = re.compile(r"^\s*@app\.route\(([^)]*)\)")
    func_re = re.compile(r"^\s*def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(")
    string_re = re.compile(r"['\"]([^'\"]+)['\"]")

    lines = Path(app_path).read_text(encoding="utf-8", errors="ignore").splitlines()

    pending_routes: List[str] = []
    block_routes: List[str] = []
    current_func = ""
    block_lines: List[str] = []

    def flush_block(routes: Iterable[str], func_name: str, content: List[str]) -> None:
        if not content:
            return
        joined = "\n".join(content)
        lowered = joined.lower()
        routes_key = "|".join(sorted(set(routes))) if routes else "<no-route>"
        base_key = f"{routes_key}:{func_name or '<anon>'}"

        marker_patterns = [
            r'X-Vuln-Confirmed"\]\s*=\s*"([^"]+)"',
            r"X-Vuln-Confirmed'\]\s*=\s*'([^']+)'",
            r"CTF\{[^}]+\}",
            r'"vuln"\s*:\s*"([^"]+)"',
            r"'vuln'\s*:\s*'([^']+)'",
        ]
        markers: Set[str] = set()
        for marker_re in marker_patterns:
            markers.update(re.findall(marker_re, joined, flags=re.IGNORECASE))
        for line in content:
            if "vuln" in line.lower() or "vulnerability" in line.lower():
                markers.add(line.strip())

        for marker in markers:
            category = classify(marker)
            if category != "Other":
                marker_key = re.sub(r"[^a-z0-9]+", "_", marker.lower()).strip("_")[:80] or "marker"
                found[category].add(f"{base_key}|{marker_key}")

        for category, pattern_id, keyword_groups in patterns:
            for terms in keyword_groups:
                if all(term in lowered for term in terms):
                    found[category].add(f"{base_key}|{pattern_id}")

    for line in lines:
        route_match = route_re.match(line)
        if route_match:
            route_bits = string_re.findall(route_match.group(1))
            if route_bits:
                pending_routes.extend(route_bits)
            continue

        func_match = func_re.match(line)
        if func_match:
            flush_block(block_routes, current_func, block_lines)
            current_func = func_match.group(1)
            block_routes = pending_routes[:] if pending_routes else []
            pending_routes = []
            block_lines = [line]
            continue

        if block_lines:
            block_lines.append(line)

    flush_block(block_routes, current_func, block_lines)

    return found


def snapshot_reports():
    return set(Path("reports").glob("*.md"))


def find_latest_report():
    reports = list(Path("reports").glob("*.md"))
    if not reports:
        return None
    return max(reports, key=lambda p: p.stat().st_ctime)


def find_new_report(before_snapshot):
    after_snapshot = set(Path("reports").glob("*.md"))
    new_reports = list(after_snapshot - before_snapshot)
    if new_reports:
        return max(new_reports, key=lambda p: p.stat().st_ctime)
    return None


def parse_report_findings(report_path):
    if not report_path or not Path(report_path).exists():
        return []

    try:
        lines = Path(report_path).read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception:
        return []

    findings = []
    current = {}
    in_section = False

    tech_re = re.compile(r"Technical Name\*\*: `([^`]+)`")
    url_re = re.compile(r"\*\*Vulnerable URL\*\*: `([^`]+)`")

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## ") and "Confirmed Vulnerabilities" in stripped:
            in_section = True
            continue
        if in_section and stripped.startswith("## "):
            break
        if not in_section:
            continue

        if stripped.startswith("### "):
            if current:
                findings.append(current)
            current = {}
            continue

        tech_match = tech_re.search(stripped)
        if tech_match:
            current["technical_name"] = tech_match.group(1)
            continue

        url_match = url_re.search(stripped)
        if url_match:
            current["url"] = url_match.group(1)
            continue

    if current:
        findings.append(current)

    return [f for f in findings if f.get("technical_name")]


def run_scan_pass(target_url: str, pass_config: ScanPassConfig):
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    before_reports = snapshot_reports()

    cmd = [
        sys.executable,
        "autonomous_scan.py",
        target_url,
        "--model",
        MODEL_PATH,
        "--depth",
        str(pass_config.depth),
        "--intensity",
        str(pass_config.intensity),
    ]

    if pass_config.persist:
        cmd.append("--persist")
    if pass_config.ai_mode:
        cmd.append("--ai-mode")
    if pass_config.pentester:
        cmd.append("--pentester")

    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")
    env.setdefault("PYTHONUTF8", "1")

    try:
        subprocess.run(
            cmd,
            env=env,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=pass_config.timeout_seconds,
        )
    except subprocess.TimeoutExpired:
        pass

    report_path = find_new_report(before_reports)
    if report_path is None:
        report_path = find_latest_report()
    findings = parse_report_findings(report_path)

    found = defaultdict(set)
    for finding in findings:
        technical = finding.get("technical_name")
        if not technical:
            continue
        category = classify(technical)
        if category == "Other":
            continue
        url = finding.get("url", "")
        dedup_key = f"{technical}|{url}" if url else technical
        found[category].add(dedup_key)

    return found


def run_model_scan(target_url: str):
    combined = defaultdict(set)
    for pass_config in SCAN_PASSES:
        print(
            f"    pass={pass_config.name} depth={pass_config.depth} intensity={pass_config.intensity} "
            f"persist={pass_config.persist} ai_mode={pass_config.ai_mode} pentester={pass_config.pentester}"
        )
        current = run_scan_pass(target_url, pass_config)
        for category, entries in current.items():
            combined[category].update(entries)

    return combined


def main():
    processes = {}
    all_ok = True

    print("Starting targets...")
    for key, cfg in TARGETS.items():
        proc, ok, status = start_target(cfg, startup_timeout=TARGET_STARTUP_TIMEOUT_SECONDS)
        processes[key] = proc
        if not ok:
            print(f"  {cfg.name}: failed to start")
            all_ok = False
        else:
            print(f"  {cfg.name}: {status}")

    if not all_ok:
        for proc in processes.values():
            stop_process(proc)
        raise SystemExit(1)

    ground_truth = {}
    detected = {}

    try:
        for key, cfg in TARGETS.items():
            print(f"\n[Ground Truth] Scanning actions for {cfg.name}...")
            ground_truth[key] = run_ground_truth_scan(cfg.app)

            print(f"[Model] Running model scan for {cfg.name}...")
            detected[key] = run_model_scan(cfg.url)

    finally:
        for proc in processes.values():
            stop_process(proc)

    rows = []
    site_index = 1
    for key, cfg in TARGETS.items():
        gt = ground_truth.get(key, {})
        det = detected.get(key, {})

        categories = [c for c in CATEGORY_ORDER if c in gt]
        extra = sorted([c for c in gt.keys() if c not in CATEGORY_ORDER])
        categories += extra

        first_row = True
        for category in categories:
            total = len(gt.get(category, set()))
            if total == 0:
                continue
            detected_set = det.get(category, set())
            detected_count = min(len(detected_set), total)
            percent = (detected_count / total) * 100 if total else 0.0
            impact = impact_for(category)

            rows.append(
                [
                    site_index if first_row else None,
                    cfg.name if first_row else None,
                    category,
                    total,
                    detected_count,
                    f"{percent:.0f}%",
                    impact.title() if isinstance(impact, str) else impact,
                ]
            )
            first_row = False

        site_index += 1

    wb = openpyxl.load_workbook("Evaluation Form.xlsx")
    ws = wb.active
    if ws is None:
        raise RuntimeError("Workbook has no active worksheet")
    ws.delete_rows(2, ws.max_row)

    for idx, row in enumerate(rows, start=2):
        for col, value in enumerate(row, start=1):
            ws.cell(row=idx, column=col, value=value)

    wb.save("Evaluation Form.xlsx")
    print("\n✅ Evaluation Form.xlsx updated with current test results.")


if __name__ == "__main__":
    main()
