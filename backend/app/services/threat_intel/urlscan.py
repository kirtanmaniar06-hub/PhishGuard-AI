"""
PhishGuard AI — URLScan Threat Intelligence Service

Implements the urlscan.io search and submission client for URLs and IPs.
"""

from typing import Type
import httpx
from app.schemas.threat_intel import UrlScanReport
from app.services.threat_intel.base import BaseThreatIntelService


class UrlScanService(BaseThreatIntelService):
    """URLScan service client utilizing cached history searching and scan ingestion."""

    @property
    def provider_name(self) -> str:
        return "urlscan"

    @property
    def response_schema(self) -> Type[UrlScanReport]:
        return UrlScanReport

    def _parse_search_result(self, result: dict) -> UrlScanReport:
        """Parse search API results into a normalized UrlScanReport."""
        task = result.get("task", {})
        page = result.get("page", {})
        verdicts = result.get("verdicts", {})
        overall_verdict = verdicts.get("overall", {})

        uuid = result.get("_id", "")
        score = overall_verdict.get("score", 0)
        malicious = overall_verdict.get("malicious", False)

        if malicious or score >= 65:
            verdict = "malicious"
        elif score >= 30:
            verdict = "suspicious"
        else:
            verdict = "clean"

        return UrlScanReport(
            url=task.get("url", ""),
            uuid=uuid,
            scan_page_url=result.get("result", f"https://urlscan.io/result/{uuid}/"),
            screenshot_url=f"https://urlscan.io/screenshots/{uuid}.png",
            malicious=malicious,
            score=score,
            domain=task.get("domain", ""),
            ip_address=page.get("ip"),
            server=page.get("server"),
            country=page.get("country"),
            verdict=verdict,
        )

    async def scan_url(self, client: httpx.AsyncClient, url: str) -> UrlScanReport:
        """Submit/Search URL scanning report from URLScan using the shared client."""
        if not self.is_configured():
            raise ValueError("URLScan API Key is not configured.")

        domain = self._extract_domain(url)
        headers = {
            "API-Key": self.api_key,
            "Content-Type": "application/json",
        }

        # 1. Search history first to avoid 15-20s submission waits
        search_url = f"https://urlscan.io/api/v1/search/?q=domain:{domain}&size=1"
        try:
            search_response = await self._request_with_retry(
                client, "GET", search_url, headers=headers
            )
            if search_response.status_code == 200:
                results = search_response.json().get("results", [])
                if results:
                    return self._parse_search_result(results[0])
        except Exception:
            pass

        # 2. If history is unavailable, submit a new scan
        submit_url = "https://urlscan.io/api/v1/scan/"
        payload = {"url": url, "visibility": "public"}
        
        response = await self._request_with_retry(
            client, "POST", submit_url, json=payload, headers=headers
        )
        
        if response.status_code != 200:
            # If rate-limited or failed, return custom empty/pending response
            return UrlScanReport(
                url=url,
                uuid="",
                scan_page_url="https://urlscan.io",
                malicious=False,
                score=0,
                domain=domain,
                verdict="unknown",
            )

        data = response.json()
        uuid = data.get("uuid", "")
        return UrlScanReport(
            url=url,
            uuid=uuid,
            scan_page_url=data.get("result", f"https://urlscan.io/result/{uuid}/"),
            screenshot_url=f"https://urlscan.io/screenshots/{uuid}.png",
            malicious=False,
            score=0,
            domain=domain,
            verdict="unknown",
        )

    async def scan_ip(self, client: httpx.AsyncClient, ip: str) -> UrlScanReport:
        """Search URLScan cache history for IP details using the shared client."""
        if not self.is_configured():
            raise ValueError("URLScan API Key is not configured.")

        headers = {"API-Key": self.api_key}
        search_url = f"https://urlscan.io/api/v1/search/?q=ip:{ip}&size=1"
        response = await self._request_with_retry(
            client, "GET", search_url, headers=headers
        )

        if response.status_code != 200 or not response.json().get("results", []):
            return UrlScanReport(
                url=ip,
                uuid="",
                scan_page_url="https://urlscan.io",
                malicious=False,
                score=0,
                domain="",
                ip_address=ip,
                verdict="unknown",
            )

        result = response.json()["results"][0]
        return self._parse_search_result(result)

    async def fetch_scan_result(self, client: httpx.AsyncClient, uuid: str) -> UrlScanReport:
        """Fetch raw scan results from urlscan.io using a past scan UUID."""
        if not self.is_configured():
            raise ValueError("URLScan API Key is not configured.")

        endpoint = f"https://urlscan.io/api/v1/result/{uuid}/"
        headers = {"API-Key": self.api_key}

        response = await self._request_with_retry(
            client, "GET", endpoint, headers=headers
        )

        self._check_status(response)
        data = response.json()
        task = data.get("task", {})
        page = data.get("page", {})
        verdicts = data.get("verdicts", {})
        overall_verdict = verdicts.get("overall", {})

        score = overall_verdict.get("score", 0)
        malicious = overall_verdict.get("malicious", False)

        if malicious or score >= 65:
            verdict = "malicious"
        elif score >= 30:
            verdict = "suspicious"
        else:
            verdict = "clean"

        return UrlScanReport(
            url=task.get("url", ""),
            uuid=uuid,
            scan_page_url=f"https://urlscan.io/result/{uuid}/",
            screenshot_url=f"https://urlscan.io/screenshots/{uuid}.png",
            malicious=malicious,
            score=score,
            domain=task.get("domain", ""),
            ip_address=page.get("ip"),
            server=page.get("server"),
            country=page.get("country"),
            verdict=verdict,
        )
