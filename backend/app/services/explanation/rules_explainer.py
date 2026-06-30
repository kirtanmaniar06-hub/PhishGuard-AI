"""
PhishGuard AI — Rule-Based Explanation Service

Implements deterministic explanations using heuristic signals and threat intelligence indicators.
"""

from typing import Dict, Any
from app.services.explanation.base import BaseExplanationService


class RuleBasedExplanationService(BaseExplanationService):
    """
    Constructs threat explanations deterministically by inspecting key signals.
    """

    async def explain(
        self,
        url: str,
        verdict: str,
        heuristics: Dict[str, Any],
        threat_intel: Dict[str, Any]
    ) -> str:
        # Collect signals
        signals = []

        # Heuristics checks
        is_https = heuristics.get("is_https", True)
        if not is_https:
            signals.append("utilizes insecure HTTP protocol instead of HTTPS")

        is_ip = heuristics.get("is_ip_address", False)
        if is_ip:
            signals.append("obfuscates host identity by displaying a raw IP address")

        length = heuristics.get("url_length", 0)
        if length > 75:
            signals.append(f"has an unusually long character layout ({length} characters) typical of link redirection")

        subdomains = heuristics.get("subdomains", {}).get("count", 0)
        if subdomains > 3:
            signals.append(f"contains an excessive count of subdomains ({subdomains}) used to mimic trusted brand names")

        keywords = heuristics.get("suspicious_keywords", {}).get("all_matched", [])
        if keywords:
            matched_kws = ", ".join(f"'{kw}'" for kw in keywords[:3])
            signals.append(f"incorporates high-risk keywords ({matched_kws}) commonly found in credential-harvesting phishing kits")

        # Threat Intel checks
        vt = threat_intel.get("virustotal")
        if vt and vt.get("malicious_count", 0) > 0:
            signals.append(f"is flagged as malicious by {vt['malicious_count']} VirusTotal security engines")

        gsb = threat_intel.get("safebrowsing")
        if gsb and gsb.get("is_flagged", False):
            signals.append("is blacklisted by Google Safe Browsing as a known social engineering target")

        abuse = threat_intel.get("abuseipdb")
        if abuse and abuse.get("abuse_confidence_score", 0) > 30:
            signals.append(f"resolves to an IP address blacklisted on AbuseIPDB (abuse confidence: {abuse['abuse_confidence_score']}%)")

        if not signals:
            if verdict == "phishing" or verdict == "critical" or verdict == "suspicious":
                return "This URL triggered multiple heuristic flags. It exhibits suspicious structural elements and is highly advised to avoid."
            return "This URL appears clean. No malicious records found in threat databases, and it matches standard safe domain patterns."

        # Compile concise explanation
        prefix = "This URL is classified as suspicious because it "
        if verdict == "safe" or verdict == "clean":
            prefix = "Although currently marked as safe, this target "

        reasons = ", ".join(signals[:-1])
        if reasons:
            explanation = f"{prefix}{reasons}, and {signals[-1]}."
        else:
            explanation = f"{prefix}{signals[0]}."

        return explanation
