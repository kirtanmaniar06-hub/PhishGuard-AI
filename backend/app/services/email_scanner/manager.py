"""
PhishGuard AI — Email Scanner Manager

Coordinates parsing, threat analysis, and risk scoring routines for email content scanning.
"""

from typing import Dict, Any
from app.services.email_scanner.parser import EmailParser
from app.services.email_scanner.analyzer import EmailAnalyzer
from app.services.email_scanner.scoring import EmailScoring


class EmailScannerManager:
    """
    Orchestrates email threat scanning processes.
    """

    def __init__(self) -> None:
        self.parser = EmailParser()
        self.analyzer = EmailAnalyzer()
        self.scoring = EmailScoring()

    def scan_email(self, raw_email: str) -> Dict[str, Any]:
        """
        Executes full parsing, heuristics analysis, and risk aggregation for an email.
        """
        # 1. Parse email components
        parsed = self.parser.parse(raw_email)

        # 2. Analyze components for threat indicators
        indicators = self.analyzer.analyze(parsed)

        # 3. Calculate risk score & status
        risk_report = self.scoring.compute_risk(indicators)

        return {
            "score": risk_report["score"],
            "status": risk_report["status"],
            "explanation": risk_report["explanation"],
            "sender": parsed["sender"],
            "subject": parsed["subject"],
            "links": parsed["links"],
            "keywords": parsed["keywords"],
            "attachments": [a["filename"] for a in parsed["attachments"]],
            "indicators": [ind["message"] for ind in indicators]
        }
