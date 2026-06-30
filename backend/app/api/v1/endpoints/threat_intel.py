"""
PhishGuard AI — Threat Intelligence API Router Contracts

Exposes API endpoints to request VirusTotal, URLScan, Google Safe Browsing,
AbuseIPDB, and aggregated threat reports.
"""

from typing import Dict
import httpx
from fastapi import APIRouter, HTTPException, Query, status

from app.core.config import settings
from app.schemas.threat_intel import (
    AbuseIpDbReport,
    SafeBrowsingReport,
    ThreatIntelReport,
    ThreatIntelScanRequest,
    UrlScanReport,
    VirusTotalReport,
)
from app.services.threat_intel.manager import ThreatIntelManager
from app.services.threat_intel.virustotal import VirusTotalService
from app.services.threat_intel.urlscan import UrlScanService
from app.services.threat_intel.safebrowsing import GoogleSafeBrowsingService
from app.services.threat_intel.abuseipdb import AbuseIpDbService

router = APIRouter()


@router.post(
    "/scan",
    response_model=ThreatIntelReport,
    status_code=status.HTTP_200_OK,
    summary="Perform multi-engine threat intelligence lookup",
    response_description="Consolidated findings from all designated threat intelligence engines",
)
async def scan_target(request: ThreatIntelScanRequest) -> ThreatIntelReport:
    """
    Submit a URL or IP to be scanned across multiple configured threat intelligence sources.

    Runs parallel lookups and combines their respective detection stats, domain context,
    reputation, and calculated risk level.
    """
    try:
        manager = ThreatIntelManager()
        return await manager.scan_target(request.target, request.engines)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Threat intelligence scanning orchestrator error: {exc}",
        )


@router.get(
    "/engines",
    response_model=Dict[str, bool],
    status_code=status.HTTP_200_OK,
    summary="Get status of threat intelligence engines",
    response_description="A mapping of engine names to their configuration readiness",
)
async def list_engines() -> Dict[str, bool]:
    """
    List all integrated threat intelligence engine providers and check if they
    are currently configured with API keys.
    """
    manager = ThreatIntelManager()
    return {name: service.is_configured() for name, service in manager.services.items()}


@router.get(
    "/virustotal/{resource:path}",
    response_model=VirusTotalReport,
    status_code=status.HTTP_200_OK,
    summary="Retrieve report from VirusTotal",
)
async def get_virustotal_report(resource: str) -> VirusTotalReport:
    """
    Query VirusTotal API directly for the scanning results and reputation details of
    a specific URL, domain, or IP.
    """
    service = VirusTotalService(settings.VIRUSTOTAL_API_KEY)
    if not service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="VirusTotal API Key is not configured in environment.",
        )
    
    manager = ThreatIntelManager()
    target_type = manager._detect_target_type(resource)

    try:
        async with httpx.AsyncClient() as client:
            if target_type == "ip":
                return await service.scan_ip(client, resource)
            return await service.scan_url(client, resource)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"VirusTotal lookup failed: {exc}",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"VirusTotal integration communication error: {exc}",
        )


@router.get(
    "/urlscan/{uuid}",
    response_model=UrlScanReport,
    status_code=status.HTTP_200_OK,
    summary="Retrieve report from URLScan",
)
async def get_urlscan_report(uuid: str) -> UrlScanReport:
    """
    Fetch raw scan results, screenshot URLs, page asset data, and security markers
    from urlscan.io using a past scan UUID.
    """
    service = UrlScanService(settings.URLSCAN_API_KEY)
    if not service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URLScan API Key is not configured in environment.",
        )
    
    try:
        async with httpx.AsyncClient() as client:
            return await service.fetch_scan_result(client, uuid)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"URLScan lookup failed: {exc}",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"URLScan integration communication error: {exc}",
        )


@router.post(
    "/safebrowsing/check",
    response_model=SafeBrowsingReport,
    status_code=status.HTTP_200_OK,
    summary="Check URL reputation on Google Safe Browsing",
)
async def check_safebrowsing(url: str = Query(..., description="Target URL to check")) -> SafeBrowsingReport:
    """
    Query Google Safe Browsing threat lists to verify if a URL is currently flagged
    for hosting malware, social engineering, or unwanted software.
    """
    service = GoogleSafeBrowsingService(settings.GOOGLE_SAFE_BROWSING_API_KEY)
    if not service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google Safe Browsing API Key is not configured in environment.",
        )

    try:
        async with httpx.AsyncClient() as client:
            return await service.scan_url(client, url)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"Google Safe Browsing lookup failed: {exc}",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Google Safe Browsing integration communication error: {exc}",
        )


@router.get(
    "/abuseipdb/{ip}",
    response_model=AbuseIpDbReport,
    status_code=status.HTTP_200_OK,
    summary="Retrieve IP reputation report from AbuseIPDB",
)
async def get_abuseipdb_report(ip: str) -> AbuseIpDbReport:
    """
    Lookup an IP address reputation, abuse reports frequency, country code, ISP,
    and abuse confidence level from AbuseIPDB.
    """
    service = AbuseIpDbService(settings.ABUSEIPDB_API_KEY)
    if not service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="AbuseIPDB API Key is not configured in environment.",
        )

    try:
        async with httpx.AsyncClient() as client:
            return await service.scan_ip(client, ip)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"AbuseIPDB lookup failed: {exc}",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AbuseIPDB integration communication error: {exc}",
        )
