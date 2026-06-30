"""
PhishGuard AI — Email Threat Scoring & Reporting Component

Aggregates threat analysis indicators into a final risk score, risk status, and descriptive summary.
"""

from typing import Dict, Any, List


class EmailScoring:
    """
    Computes numerical risk score and final classification verdict for scanned emails.
    """

    def compute_risk(self, indicators: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregate indicators and determine the overall email risk report.
        """
        score = 0
        critical_count = 0
        suspicious_count = 0

        for ind in indicators:
            if ind["severity"] == "critical":
                score += 35
                critical_count += 1
            else:
                score += 15
                suspicious_count += 1

        # Bound score to maximum of 100
        score = min(score, 100)

        # Determine status
        if score >= 60 or critical_count >= 2:
            status = "CRITICAL"
        elif score >= 20 or suspicious_count >= 1:
            status = "SUSPICIOUS"
        else:
            status = "SAFE"

        # Generate summary explanation
        explanation = self._build_explanation(status, critical_count, suspicious_count, indicators)

        return {
            "score": score,
            "status": status,
            "explanation": explanation
        }

    def _build_explanation(
        self,
        status: str,
        critical_count: int,
        suspicious_count: int,
        indicators: List[Dict[str, Any]]
    ) -> str:
        if status == "SAFE":
            return "This email appears safe. No critical authentication failures, suspicious links, or threat keywords were detected."

        reasons = []
        for ind in indicators[:3]:
            # Clean up message for single sentence inclusion
            msg = ind["message"]
            if msg.endswith("."):
                msg = msg[:-1]
            reasons.append(msg)

        prefix = "This email is flagged as highly malicious due to " if status == "CRITICAL" else "This email is marked as suspicious due to "
        
        if len(reasons) > 1:
            reasons_str = "; ".join(reasons[:-1]) + "; and " + reasons[-1]
        elif reasons:
            reasons_str = reasons[0]
        else:
            reasons_str = "multiple structural threat signals"

        return f"{prefix}{reasons_str}."
