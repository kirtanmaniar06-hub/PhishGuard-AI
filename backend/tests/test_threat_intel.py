"""
PhishGuard AI — Threat Intelligence Tests

Covers unit tests for individual services and integration tests for the
multi-engine orchestration endpoint. Scenarios tested:
  - Successful lookups
  - Timeout / network errors
  - Invalid API key (unconfigured)
  - Rate limiting (HTTP 429)
  - Invalid URL input validation
"""

from unittest.mock import AsyncMock, patch, MagicMock

import httpx
import pytest
from httpx import AsyncClient

# ════════════════════════════════════════════════════════════
# Unit Tests — VirusTotal Service
# ════════════════════════════════════════════════════════════


class TestVirusTotalService:
    """Unit tests for VirusTotalService with mocked HTTP responses."""

    @pytest.mark.asyncio
    async def test_scan_url_success(self) -> None:
        """VT returns a well-formed analysis report — verdict is computed correctly."""
        from app.services.threat_intel.virustotal import VirusTotalService

        svc = VirusTotalService(api_key="test-vt-key")

        mock_json = {
            "data": {
                "id": "u-abc123",
                "attributes": {
                    "last_analysis_stats": {
                        "harmless": 60,
                        "malicious": 5,
                        "suspicious": 2,
                        "undetected": 3,
                    },
                    "categories": {"vendor1": "phishing"},
                },
                "links": {"self": "https://www.virustotal.com/api/v3/urls/u-abc123"},
            }
        }

        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = mock_json

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.request = AsyncMock(return_value=mock_response)

        report = await svc.scan_url(mock_client, "https://evil.example.com")

        assert report.verdict in ("suspicious", "malicious")
        assert report.malicious_count == 5
        assert report.total_engines == 70
        assert report.reputation_score > 0

    @pytest.mark.asyncio
    async def test_scan_url_not_found(self) -> None:
        """VT returns 404 for unknown URL — should return unknown verdict."""
        from app.services.threat_intel.virustotal import VirusTotalService

        svc = VirusTotalService(api_key="test-vt-key")

        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 404

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.request = AsyncMock(return_value=mock_response)

        report = await svc.scan_url(mock_client, "https://unknown-url.test")

        assert report.verdict == "unknown"

    @pytest.mark.asyncio
    async def test_scan_url_timeout(self) -> None:
        """VT times out — should raise TimeoutException after retries."""
        from app.services.threat_intel.virustotal import VirusTotalService

        svc = VirusTotalService(api_key="test-vt-key")

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.request = AsyncMock(side_effect=httpx.TimeoutException("timeout"))

        with pytest.raises(httpx.TimeoutException):
            await svc.scan_url(mock_client, "https://example.com")

    @pytest.mark.asyncio
    async def test_scan_url_invalid_api_key(self) -> None:
        """Empty API key — should raise ValueError."""
        from app.services.threat_intel.virustotal import VirusTotalService

        svc = VirusTotalService(api_key="")

        mock_client = AsyncMock(spec=httpx.AsyncClient)

        with pytest.raises(ValueError, match="not configured"):
            await svc.scan_url(mock_client, "https://example.com")

    @pytest.mark.asyncio
    async def test_scan_url_rate_limited(self) -> None:
        """VT returns 429 repeatedly — should exhaust retries and raise status error."""
        from app.services.threat_intel.virustotal import VirusTotalService

        svc = VirusTotalService(api_key="test-vt-key")

        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 429
        mock_response.request = MagicMock()

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.request = AsyncMock(return_value=mock_response)

        # After max retries, _check_status raises HTTPStatusError
        with pytest.raises(httpx.HTTPStatusError):
            await svc.scan_url(mock_client, "https://example.com")


# ════════════════════════════════════════════════════════════
# Unit Tests — Google Safe Browsing Service
# ════════════════════════════════════════════════════════════


class TestGoogleSafeBrowsingService:
    """Unit tests for GoogleSafeBrowsingService with mocked HTTP responses."""

    @pytest.mark.asyncio
    async def test_scan_url_clean(self) -> None:
        """GSB returns empty matches list — URL is clean."""
        from app.services.threat_intel.safebrowsing import GoogleSafeBrowsingService

        svc = GoogleSafeBrowsingService(api_key="test-gsb-key")

        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {}  # No "matches" key

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.request = AsyncMock(return_value=mock_response)

        report = await svc.scan_url(mock_client, "https://safe-site.com")

        assert report.is_flagged is False
        assert report.verdict == "clean"
        assert len(report.threat_types) == 0

    @pytest.mark.asyncio
    async def test_scan_url_flagged(self) -> None:
        """GSB returns matches — URL is malicious."""
        from app.services.threat_intel.safebrowsing import GoogleSafeBrowsingService

        svc = GoogleSafeBrowsingService(api_key="test-gsb-key")

        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "matches": [
                {"threatType": "SOCIAL_ENGINEERING", "platformType": "ANY_PLATFORM"},
                {"threatType": "MALWARE", "platformType": "WINDOWS"},
            ]
        }

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.request = AsyncMock(return_value=mock_response)

        report = await svc.scan_url(mock_client, "https://phishing.bad")

        assert report.is_flagged is True
        assert report.verdict == "malicious"
        assert "SOCIAL_ENGINEERING" in report.threat_types

    @pytest.mark.asyncio
    async def test_scan_url_invalid_key(self) -> None:
        """Empty API key — should raise ValueError."""
        from app.services.threat_intel.safebrowsing import GoogleSafeBrowsingService

        svc = GoogleSafeBrowsingService(api_key="")
        mock_client = AsyncMock(spec=httpx.AsyncClient)

        with pytest.raises(ValueError, match="not configured"):
            await svc.scan_url(mock_client, "https://test.com")


# ════════════════════════════════════════════════════════════
# Unit Tests — AbuseIPDB Service
# ════════════════════════════════════════════════════════════


class TestAbuseIpDbService:
    """Unit tests for AbuseIpDbService with mocked HTTP responses."""

    @pytest.mark.asyncio
    async def test_scan_ip_clean(self) -> None:
        """AbuseIPDB returns low confidence — clean verdict."""
        from app.services.threat_intel.abuseipdb import AbuseIpDbService

        svc = AbuseIpDbService(api_key="test-abuse-key")

        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "ipAddress": "8.8.8.8",
                "isPublic": True,
                "ipVersion": 4,
                "abuseConfidenceScore": 0,
                "totalReports": 0,
                "isp": "Google LLC",
                "countryCode": "US",
            }
        }

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.request = AsyncMock(return_value=mock_response)

        report = await svc.scan_ip(mock_client, "8.8.8.8")

        assert report.verdict == "clean"
        assert report.abuse_confidence_score == 0
        assert report.isp == "Google LLC"

    @pytest.mark.asyncio
    async def test_scan_ip_malicious(self) -> None:
        """AbuseIPDB returns high abuse score — malicious verdict."""
        from app.services.threat_intel.abuseipdb import AbuseIpDbService

        svc = AbuseIpDbService(api_key="test-abuse-key")

        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "ipAddress": "1.2.3.4",
                "abuseConfidenceScore": 95,
                "totalReports": 412,
                "isp": "Bad ISP",
            }
        }

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.request = AsyncMock(return_value=mock_response)

        report = await svc.scan_ip(mock_client, "1.2.3.4")

        assert report.verdict == "malicious"
        assert report.abuse_confidence_score == 95

    @pytest.mark.asyncio
    async def test_scan_url_dns_failure(self) -> None:
        """URL domain cannot be resolved — returns unknown verdict."""
        from app.services.threat_intel.abuseipdb import AbuseIpDbService

        svc = AbuseIpDbService(api_key="test-abuse-key")
        mock_client = AsyncMock(spec=httpx.AsyncClient)

        # Patch _resolve_ip to simulate DNS failure
        with patch.object(svc, "_resolve_ip", return_value=""):
            report = await svc.scan_url(mock_client, "https://unresolvable.invalid")

        assert report.verdict == "unknown"
        assert report.ip_address == ""

    @pytest.mark.asyncio
    async def test_scan_ip_invalid_key(self) -> None:
        """Empty API key — should raise ValueError."""
        from app.services.threat_intel.abuseipdb import AbuseIpDbService

        svc = AbuseIpDbService(api_key="")
        mock_client = AsyncMock(spec=httpx.AsyncClient)

        with pytest.raises(ValueError, match="not configured"):
            await svc.scan_ip(mock_client, "1.2.3.4")


# ════════════════════════════════════════════════════════════
# Unit Tests — URLScan Service
# ════════════════════════════════════════════════════════════


class TestUrlScanService:
    """Unit tests for UrlScanService with mocked HTTP responses."""

    @pytest.mark.asyncio
    async def test_scan_url_history_hit(self) -> None:
        """URLScan finds a cached history result — returns immediately."""
        from app.services.threat_intel.urlscan import UrlScanService

        svc = UrlScanService(api_key="test-urlscan-key")

        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [{
                "_id": "uuid-abc",
                "task": {"url": "https://example.com", "domain": "example.com"},
                "page": {"ip": "93.184.216.34", "server": "nginx", "country": "US"},
                "verdicts": {"overall": {"score": 0, "malicious": False}},
                "result": "https://urlscan.io/result/uuid-abc/",
            }]
        }

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.request = AsyncMock(return_value=mock_response)

        report = await svc.scan_url(mock_client, "https://example.com")

        assert report.uuid == "uuid-abc"
        assert report.verdict == "clean"
        assert report.domain == "example.com"

    @pytest.mark.asyncio
    async def test_scan_url_invalid_key(self) -> None:
        """Empty API key — should raise ValueError."""
        from app.services.threat_intel.urlscan import UrlScanService

        svc = UrlScanService(api_key="")
        mock_client = AsyncMock(spec=httpx.AsyncClient)

        with pytest.raises(ValueError, match="not configured"):
            await svc.scan_url(mock_client, "https://example.com")


# ════════════════════════════════════════════════════════════
# Unit Tests — ThreatIntelManager Orchestration
# ════════════════════════════════════════════════════════════


class TestThreatIntelManager:
    """Unit tests for ThreatIntelManager orchestration logic."""

    @pytest.mark.asyncio
    async def test_scan_target_no_engines_configured(self) -> None:
        """No API keys configured — returns unknown verdict, no sub-reports."""
        from app.services.threat_intel.manager import ThreatIntelManager

        with patch.dict("os.environ", {
            "VIRUSTOTAL_API_KEY": "",
            "URLSCAN_API_KEY": "",
            "GOOGLE_SAFE_BROWSING_API_KEY": "",
            "ABUSEIPDB_API_KEY": "",
        }):
            manager = ThreatIntelManager()
            # Override all services to appear unconfigured
            for svc in manager.services.values():
                svc.api_key = ""

            report = await manager.scan_target("https://example.com")

        assert report.summary_verdict == "unknown"
        assert report.max_reputation_score == 0.0
        assert report.virustotal is None
        assert report.urlscan is None

    @pytest.mark.asyncio
    async def test_scan_target_partial_failure(self) -> None:
        """One engine throws, others succeed — should return partial results."""
        from app.services.threat_intel.manager import ThreatIntelManager
        from app.schemas.threat_intel import VirusTotalReport, SafeBrowsingReport

        manager = ThreatIntelManager()

        # Mock all services as configured
        for svc in manager.services.values():
            svc.api_key = "mock-key"

        # VT succeeds
        vt_report = VirusTotalReport(
            resource="https://example.com",
            reputation_score=10.0,
            verdict="clean",
        )
        manager.services["virustotal"].scan_url = AsyncMock(return_value=vt_report)

        # URLScan throws
        manager.services["urlscan"].scan_url = AsyncMock(
            side_effect=httpx.TimeoutException("timeout")
        )

        # GSB succeeds
        gsb_report = SafeBrowsingReport(
            url="https://example.com",
            is_flagged=False,
            verdict="clean",
        )
        manager.services["safebrowsing"].scan_url = AsyncMock(return_value=gsb_report)

        # AbuseIPDB throws
        manager.services["abuseipdb"].scan_url = AsyncMock(
            side_effect=ValueError("key error")
        )

        report = await manager.scan_target("https://example.com")

        assert report.virustotal is not None
        assert report.virustotal.verdict == "clean"
        assert report.urlscan is None  # failed
        assert report.safebrowsing is not None
        assert report.abuseipdb is None  # failed
        assert report.summary_verdict == "clean"

    def test_detect_target_type_url(self) -> None:
        """URL targets are classified as 'url'."""
        from app.services.threat_intel.manager import ThreatIntelManager

        manager = ThreatIntelManager()
        assert manager._detect_target_type("https://example.com") == "url"
        assert manager._detect_target_type("http://sub.domain.org/path") == "url"

    def test_detect_target_type_ip(self) -> None:
        """IP targets are classified as 'ip'."""
        from app.services.threat_intel.manager import ThreatIntelManager

        manager = ThreatIntelManager()
        assert manager._detect_target_type("8.8.8.8") == "ip"
        assert manager._detect_target_type("192.168.1.1") == "ip"


# ════════════════════════════════════════════════════════════
# Integration Tests — /api/v1/threat-intel Endpoints
# ════════════════════════════════════════════════════════════


class TestThreatIntelEndpoints:
    """Integration tests hitting the FastAPI test client."""

    @pytest.mark.asyncio
    async def test_scan_endpoint_success(self, client: AsyncClient) -> None:
        """POST /threat-intel/scan with mocked manager returns consolidated report."""
        from app.schemas.threat_intel import ThreatIntelReport
        from datetime import datetime

        mock_report = ThreatIntelReport(
            target="https://example.com",
            target_type="url",
            scanned_at=datetime.utcnow(),
            summary_verdict="clean",
            max_reputation_score=5.0,
        )

        with patch(
            "app.api.v1.endpoints.threat_intel.ThreatIntelManager"
        ) as MockManager:
            instance = MockManager.return_value
            instance.scan_target = AsyncMock(return_value=mock_report)

            response = await client.post(
                "/api/v1/threat-intel/scan",
                json={"target": "https://example.com"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["target"] == "https://example.com"
        assert data["summary_verdict"] == "clean"

    @pytest.mark.asyncio
    async def test_scan_endpoint_invalid_url(self, client: AsyncClient) -> None:
        """POST /threat-intel/scan with too-short target triggers validation error."""
        response = await client.post(
            "/api/v1/threat-intel/scan",
            json={"target": "ab"},  # min_length=4
        )

        assert response.status_code == 422  # Unprocessable Entity

    @pytest.mark.asyncio
    async def test_scan_endpoint_orchestrator_error(self, client: AsyncClient) -> None:
        """POST /threat-intel/scan when manager raises — returns 500."""
        with patch(
            "app.api.v1.endpoints.threat_intel.ThreatIntelManager"
        ) as MockManager:
            instance = MockManager.return_value
            instance.scan_target = AsyncMock(
                side_effect=RuntimeError("catastrophic failure")
            )

            response = await client.post(
                "/api/v1/threat-intel/scan",
                json={"target": "https://example.com"},
            )

        assert response.status_code == 500
        assert "orchestrator error" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_engines_endpoint(self, client: AsyncClient) -> None:
        """GET /threat-intel/engines — returns engine status map."""
        with patch(
            "app.api.v1.endpoints.threat_intel.ThreatIntelManager"
        ) as MockManager:
            instance = MockManager.return_value
            instance.services = {
                "virustotal": MagicMock(is_configured=MagicMock(return_value=True)),
                "urlscan": MagicMock(is_configured=MagicMock(return_value=False)),
                "safebrowsing": MagicMock(is_configured=MagicMock(return_value=True)),
                "abuseipdb": MagicMock(is_configured=MagicMock(return_value=False)),
            }

            response = await client.get("/api/v1/threat-intel/engines")

        assert response.status_code == 200
        data = response.json()
        assert data["virustotal"] is True
        assert data["urlscan"] is False

    @pytest.mark.asyncio
    async def test_virustotal_endpoint_unconfigured(self, client: AsyncClient) -> None:
        """GET /threat-intel/virustotal/* with no key — returns 400."""
        with patch(
            "app.api.v1.endpoints.threat_intel.VirusTotalService"
        ) as MockSvc:
            MockSvc.return_value.is_configured.return_value = False

            response = await client.get(
                "/api/v1/threat-intel/virustotal/https://example.com"
            )

        assert response.status_code == 400
        assert "not configured" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_abuseipdb_endpoint_unconfigured(self, client: AsyncClient) -> None:
        """GET /threat-intel/abuseipdb/* with no key — returns 400."""
        with patch(
            "app.api.v1.endpoints.threat_intel.AbuseIpDbService"
        ) as MockSvc:
            MockSvc.return_value.is_configured.return_value = False

            response = await client.get("/api/v1/threat-intel/abuseipdb/8.8.8.8")

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_safebrowsing_endpoint_unconfigured(self, client: AsyncClient) -> None:
        """POST /threat-intel/safebrowsing/check with no key — returns 400."""
        with patch(
            "app.api.v1.endpoints.threat_intel.GoogleSafeBrowsingService"
        ) as MockSvc:
            MockSvc.return_value.is_configured.return_value = False

            response = await client.post(
                "/api/v1/threat-intel/safebrowsing/check?url=https://test.com"
            )

        assert response.status_code == 400
