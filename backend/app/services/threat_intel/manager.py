"""
PhishGuard AI — Threat Intelligence Service Manager

Consolidates and manages instances of all threat intelligence providers,
offering a unified manager interface to run scans against one or more engines.
"""

import asyncio
from datetime import datetime
import ipaddress
import logging
from typing import Dict, List, Optional
from urllib.parse import urlparse
import httpx

from app.core.config import settings
from app.schemas.threat_intel import ThreatIntelReport
from app.services.threat_intel.base import BaseThreatIntelService
from app.services.threat_intel.virustotal import VirusTotalService
from app.services.threat_intel.urlscan import UrlScanService
from app.services.threat_intel.safebrowsing import GoogleSafeBrowsingService
from app.services.threat_intel.abuseipdb import AbuseIpDbService

logger = logging.getLogger("phishguard")


class ThreatIntelManager:
    """Orchestrator to configure, select, and invoke threat intelligence lookups."""

    def __init__(self):
        """Initialize the configured threat intelligence engines."""
        self.services: Dict[str, BaseThreatIntelService] = {
            "virustotal": VirusTotalService(settings.VIRUSTOTAL_API_KEY),
            "urlscan": UrlScanService(settings.URLSCAN_API_KEY),
            "safebrowsing": GoogleSafeBrowsingService(settings.GOOGLE_SAFE_BROWSING_API_KEY),
            "abuseipdb": AbuseIpDbService(settings.ABUSEIPDB_API_KEY),
        }

    def get_configured_engines(self) -> List[str]:
        """Return list of threat intel engine names that are fully configured with API keys."""
        return [name for name, service in self.services.items() if service.is_configured()]

    def _detect_target_type(self, target: str) -> str:
        """Classify target string as either 'ip' or 'url'."""
        host = target.strip()
        if "://" in host:
            try:
                host = urlparse(host).netloc or host.split("://")[1]
            except Exception:
                host = host.split("://")[1]
        
        if "/" in host:
            host = host.split("/")[0]
        if ":" in host:
            host = host.split(":")[0]

        try:
            ipaddress.ip_address(host)
            return "ip"
        except ValueError:
            return "url"

    async def scan_target(
        self,
        target: str,
        engines: Optional[List[str]] = None,
    ) -> ThreatIntelReport:
        """
        Scan a target (URL or IP) across multiple threat intelligence engines.

        Runs scans in parallel across selected/available services and consolidates results
        using a single, shared httpx.AsyncClient for connection pooling.
        """
        target_type = self._detect_target_type(target)
        
        # Determine engines to execute
        available_engines = self.get_configured_engines()
        if engines:
            selected_engines = [eng.lower() for eng in engines if eng.lower() in available_engines]
        else:
            selected_engines = available_engines

        if not selected_engines:
            # Return empty response if no engines are configured/requested
            return ThreatIntelReport(
                target=target,
                target_type=target_type,
                scanned_at=datetime.utcnow(),
                summary_verdict="unknown",
                max_reputation_score=0.0,
            )

        # Initialize single httpx AsyncClient for connection reuse
        async with httpx.AsyncClient() as client:
            tasks = []
            engine_order = []
            for name in selected_engines:
                service = self.services[name]
                engine_order.append(name)
                if target_type == "ip":
                    tasks.append(service.scan_ip(client, target))
                else:
                    tasks.append(service.scan_url(client, target))

            # Run concurrently with exception tolerance
            results = await asyncio.gather(*tasks, return_exceptions=True)

        # Associate results to providers
        reports = {}
        for name, result in zip(engine_order, results):
            if isinstance(result, Exception):
                logger.error(f"Engine {name} failed during analysis: {result}")
                reports[name] = None
            else:
                reports[name] = result

        # Extract individual reports
        virustotal = reports.get("virustotal")
        urlscan = reports.get("urlscan")
        safebrowsing = reports.get("safebrowsing")
        abuseipdb = reports.get("abuseipdb")

        # Consolidated scores & verdicts calculation
        verdicts = []
        scores = []

        if virustotal:
            verdicts.append(virustotal.verdict)
            scores.append(virustotal.reputation_score)
        if urlscan:
            verdicts.append(urlscan.verdict)
            scores.append(urlscan.score)
        if safebrowsing:
            verdicts.append(safebrowsing.verdict)
            scores.append(100.0 if safebrowsing.is_flagged else 0.0)
        if abuseipdb:
            verdicts.append(abuseipdb.verdict)
            scores.append(float(abuseipdb.abuse_confidence_score))

        # Max score across engines
        max_score = max(scores) if scores else 0.0

        # Summary verdict calculation
        if "malicious" in verdicts:
            summary_verdict = "malicious"
        elif "suspicious" in verdicts:
            summary_verdict = "suspicious"
        elif "clean" in verdicts:
            summary_verdict = "clean"
        else:
            summary_verdict = "unknown"

        return ThreatIntelReport(
            target=target,
            target_type=target_type,
            scanned_at=datetime.utcnow(),
            virustotal=virustotal,
            urlscan=urlscan,
            safebrowsing=safebrowsing,
            abuseipdb=abuseipdb,
            summary_verdict=summary_verdict,
            max_reputation_score=max_score,
        )
