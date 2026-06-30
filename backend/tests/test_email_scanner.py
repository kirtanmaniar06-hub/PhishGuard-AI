"""
PhishGuard AI — Email Scanner Tests

Verifies parsing, heuristics analysis, risk scoring, and endpoint integrations
for valid, empty, phishing, and safe email samples.
"""

import pytest
from httpx import AsyncClient
from app.services.email_scanner.manager import EmailScannerManager


class TestEmailScannerModule:
    """
    Unit tests for the email parsing and heuristics evaluation engine.
    """

    def test_empty_email(self) -> None:
        """Scanning empty string returns blank structures and a safe verdict."""
        manager = EmailScannerManager()
        report = manager.scan_email("")

        assert report["score"] == 0
        assert report["status"] == "SAFE"
        assert report["sender"] == ""
        assert report["subject"] == ""
        assert len(report["links"]) == 0
        assert len(report["keywords"]) == 0
        assert len(report["attachments"]) == 0

    def test_safe_sample_email(self) -> None:
        """Standard safe email triggers zero malicious warnings."""
        manager = EmailScannerManager()
        safe_msg = (
            "From: colleague@company.com\n"
            "Subject: Project sync reminder\n"
            "Date: Tue, 30 Jun 2026 14:00:00 +0000\n"
            "Authentication-Results: spf=pass dkim=pass\n"
            "Dkim-Signature: v=1; a=rsa-sha256; d=company.com;\n"
            "\n"
            "Hey, just a heads-up that our weekly project sync is scheduled for tomorrow at 10 AM."
        )

        report = manager.scan_email(safe_msg)

        assert report["score"] == 0
        assert report["status"] == "SAFE"
        assert report["sender"] == "colleague@company.com"
        assert report["subject"] == "Project sync reminder"
        assert len(report["indicators"]) == 0

    def test_phishing_sample_email(self) -> None:
        """Phishing email containing invalid SPF, brand mismatch, and urgency terms triggers critical warnings."""
        manager = EmailScannerManager()
        phish_msg = (
            "From: security-alert@paypal-update-login.com\n"
            "Subject: URGENT: Action required to verify billing account\n"
            "Authentication-Results: spf=fail dkim=fail\n"
            "\n"
            "Immediate login required. We detected a suspicious billing charge on your account. "
            "Please go to http://fake-login-paypal.net/auth to verify your identity and credit card."
        )

        report = manager.scan_email(phish_msg)

        assert report["score"] >= 60
        assert report["status"] == "CRITICAL"
        assert "spf=fail" in report["indicators"][0].lower() or "spf validation failed" in report["indicators"][0].lower()
        assert any("urgency" in ind.lower() or "phishing keywords" in ind.lower() for ind in report["indicators"])
        assert any("mismatch" in ind.lower() for ind in report["indicators"])
        assert "billing" in report["keywords"] or "verify" in report["keywords"]


class TestEmailScannerEndpoints:
    """
    Integration tests for the /api/v1/email-scanner scan endpoint.
    """

    @pytest.mark.asyncio
    async def test_endpoint_valid_scan(self, client: AsyncClient) -> None:
        """POST /email-scanner/scan with valid MIME payload returns scan report successfully."""
        payload = {
            "raw_email": (
                "From: info@brand.com\n"
                "Subject: Special offer\n"
                "\n"
                "Buy now at http://brand.com/deals"
            )
        }
        response = await client.post("/api/v1/email-scanner/scan", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        assert "score" in data
        assert "status" in data
        assert data["sender"] == "info@brand.com"
        assert "explanation" in data

    @pytest.mark.asyncio
    async def test_endpoint_empty_payload(self, client: AsyncClient) -> None:
        """POST /email-scanner/scan with empty body handles request and returns safe default scan."""
        payload = {"raw_email": ""}
        response = await client.post("/api/v1/email-scanner/scan", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SAFE"
        assert data["score"] == 0
