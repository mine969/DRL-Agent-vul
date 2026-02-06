import io
import os
import re
import sys
import time
import subprocess
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

import openpyxl
import requests

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from agent.improved_dqn_agent import ImprovedDQNAgent
from env.web_sec_env import WebSecEnv
from utils.model_loader import load_model_smart


@dataclass
class Target:
    name: str
    url: str
    app: str
    port: int


TARGETS = [
    Target("E-Commerce", "http://localhost:5002", "env/target_app_ecommerce.py", 5002),
    Target("Social Media", "http://localhost:5003", "env/target_app_social.py", 5003),
    Target("Banking", "http://localhost:5004", "env/target_app_banking.py", 5004),
    Target("Blog", "http://localhost:5005", "env/target_app_blog.py", 5005),
    Target("File Share", "http://localhost:5006", "env/target_app_fileshare.py", 5006),
]

MODEL_PATH = "dqn_web_sec_model.pth"
SCAN_DEPTH = 12
SCAN_INTENSITY = 15

TYPE_ORDER = [
    "SQL Injection",
    "Cross-Site Scripting (XSS)",
    "Insecure Direct Object Reference (IDOR)",
    "Broken Access Control (BAC)",
    "Mass Assignment",
    "Business Logic",
    "Race Condition",
    "Cross-Site Request Forgery (CSRF)",
    "Path Traversal",
    "File Upload",
    "Server-Side Template Injection (SSTI)",
    "Server-Side Request Forgery (SSRF)",
    "Command Injection",
    "Insecure Deserialization",
    "Weak Password",
    "Session Fixation",
    "Weak Reset Token",
    "OAuth Bypass",
    "JWT Bypass",
    "SAML Bypass",
    "Information Disclosure",
    "Sensitive Data Exposure",
    "Auth Bypass",
]

IMPACT_MAP = {
    "SQL Injection": "Critical",
    "Cross-Site Scripting (XSS)": "High",
    "Insecure Direct Object Reference (IDOR)": "Medium",
    "Broken Access Control (BAC)": "High",
    "Mass Assignment": "High",
    "Business Logic": "Medium",
    "Race Condition": "Medium",
    "Cross-Site Request Forgery (CSRF)": "Medium",
    "Path Traversal": "High",
    "File Upload": "Critical",
    "Server-Side Template Injection (SSTI)": "Critical",
    "Server-Side Request Forgery (SSRF)": "High",
    "Command Injection": "Critical",
    "Insecure Deserialization": "Critical",
    "Weak Password": "High",
    "Session Fixation": "High",
    "Weak Reset Token": "High",
    "OAuth Bypass": "High",
    "JWT Bypass": "High",
    "SAML Bypass": "High",
    "Information Disclosure": "High",
    "Sensitive Data Exposure": "High",
    "Auth Bypass": "High",
}


def classify_marker(text: str) -> Optional[str]:
    if not text:
        return None
    t = text.lower()
    if "sqli" in t or "sql injection" in t or "sql" in t:
        return "SQL Injection"
    if "xss" in t:
        return "Cross-Site Scripting (XSS)"
    if "idor" in t or "insecure direct object" in t:
        return "Insecure Direct Object Reference (IDOR)"
    if "csrf" in t:
        return "Cross-Site Request Forgery (CSRF)"
    if "upload" in t:
        return "File Upload"
    if "traversal" in t or "path traversal" in t:
        return "Path Traversal"
    if "ssti" in t or "template injection" in t:
        return "Server-Side Template Injection (SSTI)"
    if "ssrf" in t or "server-side request forgery" in t:
        return "Server-Side Request Forgery (SSRF)"
    if "command injection" in t or "cmd_injection" in t or "cmd injection" in t:
        return "Command Injection"
    if "deserialization" in t:
        return "Insecure Deserialization"
    if "mass assignment" in t:
        return "Mass Assignment"
    if "race condition" in t or "race" in t:
        return "Race Condition"
    if (
        "business logic" in t
        or "price manipulation" in t
        or "payment bypass" in t
        or "negative quantity" in t
        or "coupon" in t
    ):
        return "Business Logic"
    if "weak password" in t or "weak auth" in t:
        return "Weak Password"
    if "session fixation" in t:
        return "Session Fixation"
    if "reset token" in t or "password reset" in t or "predictable reset" in t:
        return "Weak Reset Token"
    if "oauth" in t or "state" in t and "oauth" in t:
        return "OAuth Bypass"
    if "jwt" in t:
        return "JWT Bypass"
    if "saml" in t:
        return "SAML Bypass"
    if "info disclosure" in t or "information disclosure" in t or "secret" in t:
        return "Information Disclosure"
    if "sensitive data" in t or "api key" in t:
        return "Sensitive Data Exposure"
    if "broken access control" in t or "bac" in t or "admin users" in t:
        return "Broken Access Control (BAC)"
    if "auth bypass" in t:
        return "Auth Bypass"
    return None


def extract_route_blocks(file_path: str) -> List[str]:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.read().splitlines()

    blocks: List[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.lstrip().startswith("@app.route"):
            j = i + 1
            while j < len(lines) and not lines[j].lstrip().startswith("def "):
                j += 1
            if j >= len(lines):
                break
            func_indent = len(lines[j]) - len(lines[j].lstrip())
            k = j + 1
            while k < len(lines):
                if lines[k].lstrip().startswith("@app.route") and (
                    len(lines[k]) - len(lines[k].lstrip()) == func_indent
                ):
                    break
                k += 1
            blocks.append("\n".join(lines[j:k]))
            i = k
        else:
            i += 1
    return blocks


def extract_markers(block: str) -> Set[str]:
    markers: Set[str] = set()
    markers.update(re.findall(r'X-Vuln-Confirmed"\]\s*=\s*"([^"]+)"', block))
    markers.update(re.findall(r"X-Vuln-Confirmed'\]\s*=\s*'([^']+)'", block))
    markers.update(re.findall(r"CTF\{[^}]+\}", block))
    markers.update(re.findall(r'"vuln"\s*:\s*"([^"]+)"', block))
    markers.update(re.findall(r"'vuln'\s*:\s*'([^']+)'", block))

    for line in block.splitlines():
        if "VULN" in line or "VULNERABILITY" in line:
            markers.add(line.strip())
    return markers


def ground_truth_counts(file_path: str) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    blocks = extract_route_blocks(file_path)
    for block in blocks:
        types: Set[str] = set()
        for marker in extract_markers(block):
            vuln_type = classify_marker(marker)
            if vuln_type:
                types.add(vuln_type)
        for vuln_type in types:
            counts[vuln_type] = counts.get(vuln_type, 0) + 1
    return counts


def is_reachable(url: str, timeout: float = 1.0) -> bool:
    try:
        requests.get(url, timeout=timeout)
        return True
    except requests.RequestException:
        return False


def wait_for_target(url: str, timeout_seconds: float = 6.0) -> bool:
    start = time.time()
    while time.time() - start < timeout_seconds:
        if is_reachable(url):
            return True
        time.sleep(0.5)
    return False


def start_target(target: Target) -> Tuple[Optional[subprocess.Popen], bool, str]:
    if is_reachable(target.url):
        return None, True, "already_running"
    process = subprocess.Popen(
        [sys.executable, target.app],
        cwd=os.getcwd(),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    ok = wait_for_target(target.url)
    return process, ok, "started" if ok else "failed"


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


def scan_model_counts(target: Target) -> Dict[str, int]:
    env = WebSecEnv(target_url=target.url, mode="mock_targets")
    env.max_steps_per_episode = SCAN_INTENSITY

    agent = ImprovedDQNAgent(state_dim=15, action_dim=50)
    load_model_smart(agent, model_path=MODEL_PATH, auto_checkpoint=True, verbose=True)

    network = getattr(agent, "q_network", None)
    if network:
        network.eval()

    try:
        env.action_login_valid()
    except Exception:
        pass

    buckets: Dict[str, Set[str]] = {}
    state, _ = env.reset()
    for _ in range(SCAN_INTENSITY):
        action = agent.act(state, training=False)
        next_state, _, terminated, truncated, info = env.step(action)

        response = getattr(env, "last_response", None)
        vuln_id = None

        if response is not None and response.headers.get("X-Vuln-Confirmed"):
            vuln_id = response.headers.get("X-Vuln-Confirmed")

        flags = None
        if isinstance(info, dict):
            flags = info.get("flags")

        if not vuln_id and flags:
            vuln_id = flags[0]

        if not vuln_id and response is not None and response.text:
            match = re.search(r"CTF\{[^}]+\}", response.text)
            if match:
                vuln_id = match.group(0)

        if vuln_id:
            real_action_id = action
            if hasattr(env, "mock_action_map"):
                real_action_id = env.mock_action_map.get(action, action)
            action_func = env.action_book.get(real_action_id)
            action_name = action_func.__name__ if action_func else str(action)
            vuln_type = classify_marker(action_name) or classify_marker(vuln_id)
            if vuln_type:
                key = f"{vuln_type}|{action_name}|{vuln_id}"
                buckets.setdefault(vuln_type, set()).add(key)

        state = next_state
        if terminated or truncated:
            break

    env.close()
    return {k: len(v) for k, v in buckets.items()}


def sort_types(types: List[str]) -> List[str]:
    index = {name: i for i, name in enumerate(TYPE_ORDER)}
    return sorted(types, key=lambda name: index.get(name, len(TYPE_ORDER)))


def main() -> int:
    processes: List[Optional[subprocess.Popen]] = []
    try:
        for target in TARGETS:
            proc, ok, status = start_target(target)
            processes.append(proc)
            if not ok:
                print(f"Failed to start {target.name}: {status}")
                return 1

        ground_truth: Dict[str, Dict[str, int]] = {}
        model_results: Dict[str, Dict[str, int]] = {}

        for target in TARGETS:
            ground_truth[target.name] = ground_truth_counts(target.app)

        for target in TARGETS:
            model_results[target.name] = scan_model_counts(target)

        wb = openpyxl.load_workbook("Evaluation Form.xlsx")
        ws = wb.active

        for r in range(2, ws.max_row + 1):
            for c in range(1, 8):
                ws.cell(r, c).value = None

        row = 2
        site_index = 1
        for target in TARGETS:
            gt = ground_truth.get(target.name, {})
            mr = model_results.get(target.name, {})
            types = sort_types(list(gt.keys()))
            for idx, vuln_type in enumerate(types):
                total = gt.get(vuln_type, 0)
                detected = mr.get(vuln_type, 0)
                percent = 0.0 if total == 0 else (detected / total) * 100.0

                if idx == 0:
                    ws.cell(row, 1).value = site_index
                    ws.cell(row, 2).value = f"{target.name} ({target.port})"
                else:
                    ws.cell(row, 1).value = None
                    ws.cell(row, 2).value = None

                ws.cell(row, 3).value = vuln_type
                ws.cell(row, 4).value = total
                ws.cell(row, 5).value = detected
                ws.cell(row, 6).value = f"{percent:.1f}%"
                ws.cell(row, 7).value = IMPACT_MAP.get(vuln_type, "Medium")
                row += 1
            site_index += 1

        wb.save("Evaluation Form.xlsx")
        return 0
    finally:
        for proc in processes:
            stop_process(proc)


if __name__ == "__main__":
    raise SystemExit(main())
