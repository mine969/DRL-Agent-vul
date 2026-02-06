"""
False Positive Filter
=====================

Filters out common false positives from security scan findings.
"""

from typing import List, Dict
import re


class FalsePositiveFilter:
    """Filters false positive findings from security scans."""

    def __init__(self):
        # Common false positive patterns
        self.false_positive_patterns = {
            # WordPress paths on non-WordPress sites
            "wordpress_on_non_wp": {
                "paths": ["/wp-admin", "/wp-login.php", "/wp-content", "/wp-includes"],
                "indicators": [
                    "juice",
                    "dvwa",
                    "webgoat",
                ],  # If URL contains these, it's not WordPress
            },
            # Generic admin paths that return 404
            "generic_404": {
                "status_codes": [404],
                "min_reward": 0,  # Any positive reward on 404 is suspicious
            },
            # Low-confidence findings
            "low_confidence": {
                "min_reward": 10,  # Findings with reward < 10 are likely noise
                "max_confidence": "Low",
            },
        }

    def filter_findings(self, findings: List, target_url: str = "") -> List:
        """
        Filter out false positives from findings.

        Args:
            findings: List of Finding objects
            target_url: Base URL of the target being scanned

        Returns:
            Filtered list of findings
        """
        filtered = []

        for finding in findings:
            if self._is_false_positive(finding, target_url):
                print(
                    f"  🗑️  Filtered false positive: {finding.vuln_type} at {finding.url}"
                )
                continue
            filtered.append(finding)

        return filtered

        return False

    def _is_false_positive(self, finding, target_url: str) -> bool:
        """Check if a finding is a false positive."""

        # Rule 0: Safety Override - Environment-confirmed findings are never filtered
        if getattr(finding, "env_confirmed", False):
            return False

        # Rule 0.25: High reward findings (normalized reward model)
        # In current environment, confirmed vulnerabilities are typically >= 1.0 reward.
        if finding.reward >= 1.0:
            return False

        # Rule 0.5: User Override - Preserve "Validator Rejected" items if Phase 2 kept them
        # The user explicitly wants to see findings that the Validator missed but the Agent found.
        if "Validator Rejected" in finding.confidence:
            return False

        # Rule 1: WordPress paths on non-WordPress sites
        if self._is_wordpress_false_positive(finding, target_url):
            return True

        # Rule 2: 404 checks - REMOVED as checking URL string is too aggressive
        # if self._is_404_false_positive(finding):
        #    return True

        # Rule 3: Very low reward findings
        if finding.reward <= 0:  # Only filter if non-positive
            return True

        # Rule 4: Generic "found endpoint" without actual vulnerability
        if self._is_endpoint_discovery_only(finding):
            return True

        return False

    def _is_wordpress_false_positive(self, finding, target_url: str) -> bool:
        """Check if this is a WordPress path on a non-WordPress site."""
        wp_paths = self.false_positive_patterns["wordpress_on_non_wp"]["paths"]
        non_wp_indicators = self.false_positive_patterns["wordpress_on_non_wp"][
            "indicators"
        ]

        # Check if finding URL contains WordPress paths
        is_wp_path = any(wp_path in finding.url.lower() for wp_path in wp_paths)

        # Check if target is NOT WordPress
        is_non_wp_site = any(
            indicator in target_url.lower() or indicator in finding.url.lower()
            for indicator in non_wp_indicators
        )

        return is_wp_path and is_non_wp_site

    def _is_404_false_positive(self, finding) -> bool:
        """Deprecated: Too aggressive."""
        return False

    def _is_endpoint_discovery_only(self, finding) -> bool:
        """Check if this is just endpoint discovery, not an actual vulnerability."""
        # If vulnerability type is just "Found" or "Discovered" without specifics
        generic_types = ["found", "discovered", "endpoint", "page"]
        if any(generic in finding.vuln_type.lower() for generic in generic_types):
            if finding.reward < 10:  # Lowered threshold from 50
                return True
        return False


def apply_false_positive_filter(findings: List, target_url: str = "") -> List:
    """
    Convenience function to filter false positives.

    Usage:
        filtered_findings = apply_false_positive_filter(findings, target_url)
    """
    filter_obj = FalsePositiveFilter()
    return filter_obj.filter_findings(findings, target_url)
