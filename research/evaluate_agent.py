"""
Agent Evaluation Framework
==========================

Comprehensive evaluation script that tests the DRL agent against all mock applications
and compares findings with the ground truth vulnerability database.

Usage:
    python research/evaluate_agent.py --agent improved --episodes 1000

Outputs:
- Detection accuracy metrics
- False positive/negative analysis
- Performance comparison
- Detailed vulnerability reports
"""

import sys
import os
import json
import time
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional, Set
from dataclasses import dataclass
import argparse
from urllib.parse import urlparse

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from config import get_config
    from agent.improved_dqn_agent import ImprovedDQNAgent
    from agent.dqn_agent import DQNAgent
    from env.web_sec_env import WebSecurityGym

    _IMPORTS_SUCCESSFUL = True
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running from the project root directory")
    _IMPORTS_SUCCESSFUL = False
    get_config = None
    ImprovedDQNAgent = None
    DQNAgent = None
    WebSecurityGym = None


@dataclass
class VulnerabilityFinding:
    """Represents a vulnerability finding from the agent."""

    vuln_id: str
    vuln_type: str
    endpoint: str
    method: str
    confidence: float
    payload: str = ""
    description: str = ""
    verified: bool = False


@dataclass
class EvaluationMetrics:
    """Evaluation metrics for agent performance."""

    true_positives: int = 0
    false_positives: int = 0
    false_negatives: int = 0
    true_negatives: int = 0

    @property
    def precision(self) -> float:
        """TP / (TP + FP)"""
        denominator = self.true_positives + self.false_positives
        return self.true_positives / denominator if denominator > 0 else 0.0

    @property
    def recall(self) -> float:
        """TP / (TP + FN)"""
        denominator = self.true_positives + self.false_negatives
        return self.true_positives / denominator if denominator > 0 else 0.0

    @property
    def f1_score(self) -> float:
        """2 * (P * R) / (P + R)"""
        p, r = self.precision, self.recall
        return 2 * (p * r) / (p + r) if (p + r) > 0 else 0.0

    @property
    def accuracy(self) -> float:
        """(TP + TN) / Total"""
        total = (
            self.true_positives
            + self.false_positives
            + self.false_negatives
            + self.true_negatives
        )
        return (self.true_positives + self.true_negatives) / total if total > 0 else 0.0


class AgentEvaluator:
    """Evaluates agent performance against ground truth vulnerabilities."""

    def __init__(
        self, agent_type: str = "improved", checkpoint_path: Optional[str] = None
    ):
        """
        Initialize evaluator.

        Args:
            agent_type: "baseline" or "improved"
            checkpoint_path: Path to trained checkpoint (optional)
        """
        self.agent_type = agent_type
        self.checkpoint_path = checkpoint_path
        if not _IMPORTS_SUCCESSFUL or get_config is None:
            raise RuntimeError("Required imports not available. Run from project root.")

        self.config = get_config()

        # Load ground truth vulnerabilities
        self.ground_truth = self._load_ground_truth()

        # Initialize results storage
        self.results = {}
        self.agent = None

    def _load_ground_truth(self) -> Dict[str, List[Dict]]:
        """Load ground truth vulnerability database."""
        ground_truth_file = Path(__file__).parent / "ground_truth_vulnerabilities.md"
        if not ground_truth_file.exists():
            print(f"Ground truth file not found: {ground_truth_file}")
            return self._get_sample_ground_truth()

        try:
            return self._parse_ground_truth_file(ground_truth_file)
        except Exception as e:
            print(f"Failed to parse ground truth file: {e}")
            print("Falling back to sample ground truth data")
            return self._get_sample_ground_truth()

    def _parse_ground_truth_file(
        self, file_path: Path
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Parse ground truth vulnerabilities from markdown."""
        vulnerabilities: Dict[str, List[Dict[str, Any]]] = {
            "ecommerce": [],
            "social": [],
            "banking": [],
            "blog": [],
            "fileshare": [],
        }

        current_app: Optional[str] = None
        current_vuln: Optional[Dict[str, Any]] = None

        def flush_vuln() -> None:
            nonlocal current_vuln
            if (
                current_app
                and current_vuln
                and current_vuln.get("endpoint")
                and current_vuln.get("method")
            ):
                vulnerabilities[current_app].append(current_vuln)
            current_vuln = None

        for raw_line in file_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line:
                continue

            if line.startswith("## "):
                flush_vuln()
                app_key = self._app_key_from_heading(line)
                if app_key:
                    current_app = app_key
                continue

            if line.startswith("#### "):
                flush_vuln()
                heading = line.replace("####", "", 1).strip()
                heading = re.sub(r"^\d+(?:\.\d+)*\s+", "", heading)
                severity_match = re.search(r"\(([^)]+)\)\s*$", heading)
                severity = severity_match.group(1) if severity_match else ""
                heading = re.sub(r"\s*\([^)]*\)\s*$", "", heading).strip()
                base_type = heading.split(" - ", 1)[0].strip()
                current_vuln = {
                    "id": "",
                    "type": base_type,
                    "name": heading,
                    "endpoint": "",
                    "method": "",
                    "severity": severity,
                    "owasp_category": "",
                    "description": "",
                }
                continue

            if current_vuln is None:
                continue

            field_value = self._extract_md_field(line, "CVE-like ID")
            if field_value:
                current_vuln["id"] = field_value
                continue

            field_value = self._extract_md_field(line, "Endpoint")
            if field_value:
                current_vuln["endpoint"] = field_value
                continue

            field_value = self._extract_md_field(line, "Method")
            if field_value:
                current_vuln["method"] = field_value.upper()
                continue

            field_value = self._extract_md_field(line, "OWASP Category")
            if field_value:
                current_vuln["owasp_category"] = field_value
                continue

            field_value = self._extract_md_field(line, "Description")
            if field_value:
                current_vuln["description"] = field_value
                continue

        flush_vuln()
        return vulnerabilities

    def _app_key_from_heading(self, heading: str) -> Optional[str]:
        lowered = heading.lower()
        if "e-commerce" in lowered or "ecommerce" in lowered:
            return "ecommerce"
        if "social media" in lowered or "social" in lowered:
            return "social"
        if "banking" in lowered:
            return "banking"
        if "blog" in lowered:
            return "blog"
        if (
            "file share" in lowered
            or "file sharing" in lowered
            or "fileshare" in lowered
        ):
            return "fileshare"
        return None

    def _extract_md_field(self, line: str, field: str) -> Optional[str]:
        pattern = rf"^- \*\*{re.escape(field)}:\*\*\s*(.+)$"
        match = re.match(pattern, line)
        if not match:
            return None
        value = match.group(1).strip()
        return value.strip("`")

    def _get_sample_ground_truth(self) -> Dict[str, List[Dict]]:
        """Sample ground truth data (replace with actual parsing)."""
        return {
            "ecommerce": [
                {
                    "id": "EC-001",
                    "type": "Mass Assignment",
                    "endpoint": "/api/register",
                    "method": "POST",
                },
                {
                    "id": "EC-002",
                    "type": "SQL Injection",
                    "endpoint": "/api/login",
                    "method": "POST",
                },
                {
                    "id": "EC-003",
                    "type": "SQL Injection",
                    "endpoint": "/api/products",
                    "method": "GET",
                },
                {
                    "id": "EC-004",
                    "type": "IDOR",
                    "endpoint": "/api/products/<id>",
                    "method": "PUT",
                },
                {
                    "id": "EC-005",
                    "type": "IDOR",
                    "endpoint": "/api/orders/<id>",
                    "method": "GET",
                },
                {
                    "id": "EC-006",
                    "type": "Broken Access Control",
                    "endpoint": "/api/admin/users",
                    "method": "GET",
                },
                {
                    "id": "EC-007",
                    "type": "Business Logic",
                    "endpoint": "/api/cart/add",
                    "method": "POST",
                },
                {
                    "id": "EC-008",
                    "type": "Race Condition",
                    "endpoint": "/api/checkout",
                    "method": "POST",
                },
                {
                    "id": "EC-009",
                    "type": "Business Logic",
                    "endpoint": "/api/checkout",
                    "method": "POST",
                },
                {
                    "id": "EC-010",
                    "type": "Business Logic",
                    "endpoint": "/api/payment/process",
                    "method": "POST",
                },
                {
                    "id": "EC-011",
                    "type": "Info Disclosure",
                    "endpoint": "/api/admin/stats",
                    "method": "GET",
                },
            ],
            "social": [
                {
                    "id": "SM-001",
                    "type": "Weak Password",
                    "endpoint": "/api/register",
                    "method": "POST",
                },
                {
                    "id": "SM-002",
                    "type": "Session Fixation",
                    "endpoint": "/api/login",
                    "method": "POST",
                },
                {
                    "id": "SM-003",
                    "type": "Weak Reset Token",
                    "endpoint": "/api/password-reset",
                    "method": "POST",
                },
                {
                    "id": "SM-004",
                    "type": "IDOR",
                    "endpoint": "/api/profile/<id>",
                    "method": "GET",
                },
                {
                    "id": "SM-005",
                    "type": "IDOR",
                    "endpoint": "/api/profile/<id>",
                    "method": "PUT",
                },
                {
                    "id": "SM-006",
                    "type": "IDOR",
                    "endpoint": "/api/posts/<id>",
                    "method": "DELETE",
                },
                {
                    "id": "SM-007",
                    "type": "IDOR",
                    "endpoint": "/api/messages/<id>",
                    "method": "GET",
                },
                {
                    "id": "SM-008",
                    "type": "XSS",
                    "endpoint": "/api/posts",
                    "method": "POST",
                },
                {
                    "id": "SM-009",
                    "type": "XSS",
                    "endpoint": "/api/posts/<id>/comments",
                    "method": "GET",
                },
                {
                    "id": "SM-010",
                    "type": "XSS",
                    "endpoint": "/api/posts/<id>/comments",
                    "method": "POST",
                },
                {
                    "id": "SM-011",
                    "type": "XSS",
                    "endpoint": "/api/messages/send",
                    "method": "POST",
                },
                {
                    "id": "SM-012",
                    "type": "File Upload",
                    "endpoint": "/api/upload",
                    "method": "POST",
                },
                {
                    "id": "SM-013",
                    "type": "Path Traversal",
                    "endpoint": "/uploads/<filename>",
                    "method": "GET",
                },
                {
                    "id": "SM-014",
                    "type": "CSRF",
                    "endpoint": "/api/friends/add",
                    "method": "POST",
                },
                {
                    "id": "SM-015",
                    "type": "SQL Injection",
                    "endpoint": "/api/search",
                    "method": "GET",
                },
            ],
            "banking": [
                {
                    "id": "BA-001",
                    "type": "CSRF",
                    "endpoint": "/transfer",
                    "method": "POST",
                },
                {
                    "id": "BA-002",
                    "type": "IDOR",
                    "endpoint": "/transfer",
                    "method": "POST",
                },
            ],
            "blog": [
                {
                    "id": "BL-001",
                    "type": "XSS",
                    "endpoint": "/new-post",
                    "method": "POST",
                },
                {
                    "id": "BL-002",
                    "type": "XSS",
                    "endpoint": "/post/<id>/comment",
                    "method": "POST",
                },
            ],
            "fileshare": [
                {
                    "id": "FS-001",
                    "type": "File Upload",
                    "endpoint": "/upload",
                    "method": "POST",
                },
                {
                    "id": "FS-002",
                    "type": "IDOR",
                    "endpoint": "/download/<id>",
                    "method": "GET",
                },
                {
                    "id": "FS-003",
                    "type": "Path Traversal",
                    "endpoint": "/download/<id>",
                    "method": "GET",
                },
                {
                    "id": "FS-004",
                    "type": "IDOR",
                    "endpoint": "/delete/<id>",
                    "method": "GET",
                },
            ],
        }

    def load_agent(self) -> None:
        """Load or create the agent."""
        if not _IMPORTS_SUCCESSFUL:
            raise RuntimeError("Required imports not available. Run from project root.")

        if self.checkpoint_path and Path(self.checkpoint_path).exists():
            print(f"Loading agent from checkpoint: {self.checkpoint_path}")
            if self.agent_type == "improved":
                if ImprovedDQNAgent is None:
                    raise RuntimeError("ImprovedDQNAgent not available")
                self.agent = ImprovedDQNAgent(
                    state_dim=self.config.agent.state_dim,
                    action_dim=self.config.agent.action_dim,
                    use_prioritized_replay=True,
                    use_noisy_networks=True,
                    n_step=3,
                )
                self.agent.load(self.checkpoint_path)
            else:
                if DQNAgent is None:
                    raise RuntimeError("DQNAgent not available")
                self.agent = DQNAgent(
                    state_dim=self.config.agent.state_dim,
                    action_dim=self.config.agent.action_dim,
                )
                # Load checkpoint for baseline agent (would need implementation)
        else:
            print(f"Creating new {self.agent_type} agent")
            if self.agent_type == "improved":
                if ImprovedDQNAgent is None:
                    raise RuntimeError("ImprovedDQNAgent not available")
                self.agent = ImprovedDQNAgent(
                    state_dim=self.config.agent.state_dim,
                    action_dim=self.config.agent.action_dim,
                    use_prioritized_replay=True,
                    use_noisy_networks=True,
                    n_step=3,
                )
            else:
                if DQNAgent is None:
                    raise RuntimeError("DQNAgent not available")
                self.agent = DQNAgent(
                    state_dim=self.config.agent.state_dim,
                    action_dim=self.config.agent.action_dim,
                )

    def evaluate_application(self, app_name: str, url: str) -> Dict[str, Any]:
        """
        Evaluate agent performance on a single application.

        Args:
            app_name: Name of the application (ecommerce, social, etc.)
            url: URL of the application

        Returns:
            Dictionary with evaluation results
        """
        print(f"\n🔍 Evaluating {app_name} at {url}")

        if WebSecurityGym is None:
            raise RuntimeError("WebSecurityGym not available")
        if self.agent is None:
            raise RuntimeError("Agent not loaded. Call load_agent() first.")

        # Create environment
        env = WebSecurityGym(target_url=url, mode="mock_targets")

        # Get ground truth for this application
        ground_truth = self.ground_truth.get(app_name, [])
        print(f"Ground truth: {len(ground_truth)} vulnerabilities")

        # Agent scanning simulation
        findings = []
        state, _ = env.reset()
        max_steps = getattr(env, "max_steps_per_episode", 100)

        print("Scanning in progress...")
        for step in range(max_steps):
            # Agent action
            action = self.agent.act(state, training=False)

            # Execute action
            next_state, reward, terminated, truncated, info = env.step(action)

            action_name = self._resolve_action_name(env, action)
            if info.get("vuln_found") == 1:
                endpoint_url = info.get("url") or url
                endpoint_path = self._normalize_path(urlparse(endpoint_url).path)
                method = (info.get("method") or "GET").upper()

                finding = VulnerabilityFinding(
                    vuln_id=f"{app_name.upper()}-F{len(findings) + 1:03d}",
                    vuln_type=self._action_to_vuln_type(action_name),
                    endpoint=endpoint_path,
                    method=method,
                    confidence=self._reward_to_confidence(reward),
                    payload=info.get("payload", ""),
                    verified=True,
                )
                findings.append(finding)

            state = next_state
            if terminated or truncated:
                break

        print(f"Agent found {len(findings)} potential vulnerabilities")

        # Compare with ground truth
        metrics = self._calculate_metrics(findings, ground_truth, app_name)

        # Create detailed results
        result = {
            "application": app_name,
            "url": url,
            "ground_truth_count": len(ground_truth),
            "findings_count": len(findings),
            "metrics": {
                "precision": metrics.precision,
                "recall": metrics.recall,
                "f1_score": metrics.f1_score,
                "accuracy": metrics.accuracy,
                "true_positives": metrics.true_positives,
                "false_positives": metrics.false_positives,
                "false_negatives": metrics.false_negatives,
                "true_negatives": metrics.true_negatives,
            },
            "findings": [
                {
                    "id": f.vuln_id,
                    "type": f.vuln_type,
                    "endpoint": f.endpoint,
                    "method": f.method,
                    "confidence": f.confidence,
                    "verified": f.verified,
                }
                for f in findings
            ],
            "ground_truth": ground_truth,
        }

        return result

    def _calculate_metrics(
        self,
        findings: List[VulnerabilityFinding],
        ground_truth: List[Dict],
        app_name: str,
    ) -> EvaluationMetrics:
        """
        Calculate evaluation metrics by comparing findings with ground truth.

        This is a simplified implementation. In practice, you'd need more
        sophisticated matching between agent findings and ground truth.
        """
        metrics = EvaluationMetrics()

        matched_ids = set()
        for finding in findings:
            match = self._match_finding_to_ground_truth(
                finding, ground_truth, matched_ids
            )
            if match:
                metrics.true_positives += 1
                matched_ids.add(match["id"])
            else:
                metrics.false_positives += 1

        metrics.false_negatives = max(0, len(ground_truth) - len(matched_ids))
        metrics.true_negatives = 0

        return metrics

    def _resolve_action_name(self, env: Any, action_id: int) -> str:
        if hasattr(env, "mock_action_map"):
            real_action_id = env.mock_action_map.get(action_id, action_id)
        else:
            real_action_id = action_id
        action_fn = env.action_book.get(real_action_id)
        return action_fn.__name__ if action_fn else "unknown_action"

    def _reward_to_confidence(self, reward: float) -> float:
        if reward >= 1.0:
            return 0.9
        if reward > 0:
            return min(0.8, reward)
        return 0.5

    def _normalize_path(self, path: str) -> str:
        if not path:
            return "/"
        if path != "/" and path.endswith("/"):
            return path[:-1]
        return path

    def _normalize_type(self, vuln_type: str) -> str:
        name = vuln_type.lower()
        if "sql injection" in name or "sqli" in name:
            return "sql injection"
        if "xss" in name:
            return "xss"
        if "idor" in name:
            return "idor"
        if "broken access" in name or "bac" in name or "access control" in name:
            return "broken access control"
        if "mass assignment" in name:
            return "mass assignment"
        if "csrf" in name:
            return "csrf"
        if "path traversal" in name or "lfi" in name:
            return "path traversal"
        if "file upload" in name:
            return "file upload"
        if "weak password" in name:
            return "weak password"
        if "session fixation" in name:
            return "session fixation"
        if "reset token" in name or "password reset" in name:
            return "weak reset token"
        if "info disclosure" in name or "sensitive data" in name:
            return "info disclosure"
        if "race condition" in name:
            return "race condition"
        if (
            "business logic" in name
            or "price manipulation" in name
            or "payment bypass" in name
            or "negative quantity" in name
        ):
            return "business logic"
        return name

    def _action_to_vuln_type(self, action_name: str) -> str:
        name = action_name.lower()
        if "idor" in name:
            return "IDOR"
        if "sqli" in name or "sql" in name or "login_bypass" in name:
            return "SQL Injection"
        if "xss" in name:
            return "XSS"
        if "mass_assignment" in name:
            return "Mass Assignment"
        if "csrf" in name:
            return "CSRF"
        if "path_traversal" in name or "lfi" in name:
            return "Path Traversal"
        if "file_upload" in name:
            return "File Upload"
        if "session_fixation" in name:
            return "Session Fixation"
        if "weak_password" in name:
            return "Weak Password"
        if "password_reset" in name:
            return "Weak Reset Token"
        if "info_disclosure" in name:
            return "Info Disclosure"
        if "race_condition" in name:
            return "Race Condition"
        if (
            "price_manipulation" in name
            or "negative_quantity" in name
            or "payment_bypass" in name
            or "business_logic" in name
        ):
            return "Business Logic"
        if "authorization_bypass" in name or "role_escalation" in name or "bac" in name:
            return "Broken Access Control"
        return action_name.replace("_", " ").title()

    def _endpoint_matches(
        self, finding_endpoint: str, ground_truth_endpoint: str
    ) -> bool:
        finding_norm = self._normalize_path(finding_endpoint)
        gt_norm = self._normalize_path(ground_truth_endpoint)
        if finding_norm == gt_norm:
            return True
        if "<" in gt_norm and ">" in gt_norm:
            pattern = re.escape(gt_norm)
            pattern = re.sub(r"\\<[^>]+\\>", r"[^/]+", pattern)
            return re.fullmatch(pattern, finding_norm) is not None
        return False

    def _match_finding_to_ground_truth(
        self,
        finding: VulnerabilityFinding,
        ground_truth: List[Dict[str, Any]],
        matched_ids: Set[str],
    ) -> Optional[Dict[str, Any]]:
        finding_type = self._normalize_type(finding.vuln_type)
        for gt in ground_truth:
            if gt.get("id") in matched_ids:
                continue
            gt_method = (gt.get("method") or "").upper()
            if gt_method and finding.method and gt_method != finding.method.upper():
                continue
            if not self._endpoint_matches(finding.endpoint, gt.get("endpoint", "")):
                continue
            gt_type = self._normalize_type(gt.get("type", ""))
            if gt_type and finding_type and gt_type != finding_type:
                continue
            return gt
        return None

    def run_full_evaluation(self) -> Dict[str, Any]:
        """Run evaluation on all applications."""
        print("=" * 60)
        print("🤖 DRL Agent Vulnerability Detection Evaluation")
        print("=" * 60)
        print(f"Agent Type: {self.agent_type}")
        print(f"Checkpoint: {self.checkpoint_path or 'None (new agent)'}")
        print()

        # Application configurations
        applications = [
            ("ecommerce", "http://localhost:5002"),
            ("social", "http://localhost:5003"),
            ("banking", "http://localhost:5004"),
            ("blog", "http://localhost:5005"),
            ("fileshare", "http://localhost:5006"),
        ]

        all_results = {}

        for app_name, url in applications:
            try:
                result = self.evaluate_application(app_name, url)
                all_results[app_name] = result

                # Print summary
                metrics = result["metrics"]
                print(f"📊 {app_name.upper()}:")
                print(f"   Precision: {metrics['precision']:.3f}")
                print(f"   Recall:    {metrics['recall']:.3f}")
                print(f"   F1-Score:  {metrics['f1_score']:.3f}")
                print(f"   Accuracy:  {metrics['accuracy']:.3f}")
                print()

            except Exception as e:
                print(f"❌ Error evaluating {app_name}: {e}")
                continue

        # Overall summary
        self._print_overall_summary(all_results)

        return all_results

    def _print_overall_summary(self, results: Dict[str, Any]) -> None:
        """Print overall evaluation summary."""
        print("=" * 60)
        print("📈 OVERALL EVALUATION SUMMARY")
        print("=" * 60)

        total_tp = sum(r["metrics"]["true_positives"] for r in results.values())
        total_fp = sum(r["metrics"]["false_positives"] for r in results.values())
        total_fn = sum(r["metrics"]["false_negatives"] for r in results.values())
        total_tn = sum(r["metrics"]["true_negatives"] for r in results.values())

        overall_precision = (
            total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0
        )
        overall_recall = (
            total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0
        )
        overall_f1 = (
            2
            * (overall_precision * overall_recall)
            / (overall_precision + overall_recall)
            if (overall_precision + overall_recall) > 0
            else 0
        )
        overall_accuracy = (
            (total_tp + total_tn) / (total_tp + total_fp + total_fn + total_tn)
            if (total_tp + total_fp + total_fn + total_tn) > 0
            else 0
        )

        print(f"Total True Positives:  {total_tp}")
        print(f"Total False Positives: {total_fp}")
        print(f"Total False Negatives: {total_fn}")
        print(f"Total True Negatives:  {total_tn}")
        print()
        print(f"Overall Precision: {overall_precision:.3f}")
        print(f"Overall Recall:    {overall_recall:.3f}")
        print(f"Overall F1-Score:  {overall_f1:.3f}")
        print(f"Overall Accuracy:  {overall_accuracy:.3f}")
        print()
        print("🎯 Research Quality Assessment:")
        if overall_f1 >= 0.9:
            print("   ⭐ Excellent (Publication-ready)")
        elif overall_f1 >= 0.8:
            print("   ✅ Very Good (Strong results)")
        elif overall_f1 >= 0.7:
            print("   ⚠️ Good (Needs improvement)")
        else:
            print("   ❌ Needs work (Further development required)")

    def save_results(
        self, results: Dict[str, Any], output_file: Optional[str] = None
    ) -> None:
        """Save evaluation results to file."""
        if output_file is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_file = (
                f"research/results/evaluation_{self.agent_type}_{timestamp}.json"
            )

        # Create output directory
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)

        # Convert dataclasses to dicts for JSON serialization
        serializable_results = {}
        for app_name, app_results in results.items():
            serializable_results[app_name] = {
                "application": app_results["application"],
                "url": app_results["url"],
                "ground_truth_count": app_results["ground_truth_count"],
                "findings_count": app_results["findings_count"],
                "metrics": app_results["metrics"],
                "findings": [
                    {
                        "id": f["id"],
                        "type": f["type"],
                        "endpoint": f["endpoint"],
                        "method": f["method"],
                        "confidence": f["confidence"],
                        "verified": f["verified"],
                    }
                    for f in app_results["findings"]
                ],
                "ground_truth": app_results["ground_truth"],
            }

        with open(output_file, "w") as f:
            json.dump(serializable_results, f, indent=2)

        print(f"✅ Results saved to: {output_file}")


def main():
    """Main evaluation function."""
    if not _IMPORTS_SUCCESSFUL:
        return

    parser = argparse.ArgumentParser(description="Evaluate DRL Agent Performance")
    parser.add_argument(
        "--agent",
        choices=["baseline", "improved"],
        default="improved",
        help="Agent type to evaluate",
    )
    parser.add_argument(
        "--checkpoint", type=str, help="Path to trained checkpoint (optional)"
    )
    parser.add_argument("--output", type=str, help="Output file for results (optional)")

    args = parser.parse_args()

    # Create evaluator
    evaluator = AgentEvaluator(agent_type=args.agent, checkpoint_path=args.checkpoint)

    # Load agent
    evaluator.load_agent()

    # Run evaluation
    results = evaluator.run_full_evaluation()

    # Save results
    evaluator.save_results(results, args.output)


if __name__ == "__main__":
    main()
