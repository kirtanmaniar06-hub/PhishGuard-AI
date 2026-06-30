"""
PhishGuard AI — Threat Intelligence Pydantic Schemas

Defines validation and serialization schemas for VirusTotal, URLScan,
Google Safe Browsing, AbuseIPDB, and unified threat reports.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class VirusTotalReport(BaseModel):
    """Schema for VirusTotal lookup results."""
    model_config = ConfigDict(from_attributes=True)

    resource: str = Field(..., description="Target URL, domain, or IP scanned")
    scan_id: Optional[str] = Field(None, description="VirusTotal scan ID")
    permalink: Optional[str] = Field(None, description="Link to scan results on VirusTotal")
    harmless_count: int = Field(0, description="Number of engines classifying target as harmless")
    malicious_count: int = Field(0, description="Number of engines classifying target as malicious")
    suspicious_count: int = Field(0, description="Number of engines classifying target as suspicious")
    undetected_count: int = Field(0, description="Number of engines that did not detect threats")
    total_engines: int = Field(0, description="Total engines queried")
    reputation_score: float = Field(0.0, description="Reputation score (0 to 100, where 100 is highly malicious)")
    categories: List[str] = Field(default_factory=list, description="Categories assigned by scanning engines")
    verdict: str = Field("unknown", description="Overall verdict (clean, suspicious, malicious, unknown)")


class UrlScanReport(BaseModel):
    """Schema for URLScan lookup results."""
    model_config = ConfigDict(from_attributes=True)

    url: str = Field(..., description="Target URL scanned")
    uuid: str = Field(..., description="Unique scan identifier on URLScan")
    scan_page_url: str = Field(..., description="Link to the scan details page on URLScan")
    screenshot_url: Optional[str] = Field(None, description="URL of the page screenshot captured by URLScan")
    malicious: bool = Field(False, description="Flag indicating if urlscan.io classified the page as malicious")
    score: int = Field(0, description="Reputation score calculated by urlscan.io (0 to 100)")
    domain: str = Field(..., description="Primary domain of the target URL")
    ip_address: Optional[str] = Field(None, description="Primary IP address serving the target URL")
    server: Optional[str] = Field(None, description="Web server software identified on target URL")
    country: Optional[str] = Field(None, description="Country hosting the target IP address")
    verdict: str = Field("unknown", description="Overall verdict (clean, suspicious, malicious, unknown)")


class SafeBrowsingReport(BaseModel):
    """Schema for Google Safe Browsing lookup results."""
    model_config = ConfigDict(from_attributes=True)

    url: str = Field(..., description="Target URL scanned")
    is_flagged: bool = Field(False, description="Flag indicating if URL is registered in Safe Browsing list")
    threat_types: List[str] = Field(default_factory=list, description="Threat classifications matched (e.g. MALWARE, SOCIAL_ENGINEERING)")
    platform_types: List[str] = Field(default_factory=list, description="Target platforms affected")
    verdict: str = Field("unknown", description="Overall verdict (clean, suspicious, malicious, unknown)")


class AbuseIpDbReport(BaseModel):
    """Schema for AbuseIPDB IP reputation lookup results."""
    model_config = ConfigDict(from_attributes=True)

    ip_address: str = Field(..., description="Target IP address scanned")
    is_public: bool = Field(True, description="Indicates if the IP is public")
    ip_version: int = Field(4, description="IP version (4 or 6)")
    abuse_confidence_score: int = Field(0, description="Score indicating confidence of abuse (0 to 100)")
    total_reports: int = Field(0, description="Total reports submitted against this IP")
    last_reported_at: Optional[str] = Field(None, description="ISO timestamp of the last abuse report")
    country_code: Optional[str] = Field(None, description="Two-letter country code")
    country_name: Optional[str] = Field(None, description="Name of the hosting country")
    isp: Optional[str] = Field(None, description="Internet Service Provider")
    domain: Optional[str] = Field(None, description="Domain registered to this IP")
    usage_type: Optional[str] = Field(None, description="Type of usage (e.g., Data Center, ISP, Mobile)")
    verdict: str = Field("unknown", description="Overall verdict (clean, suspicious, malicious, unknown)")


class ThreatIntelReport(BaseModel):
    """Consolidated threat intelligence report summarizing all providers."""
    model_config = ConfigDict(from_attributes=True)

    target: str = Field(..., description="Scanned target (URL or IP)")
    target_type: str = Field(..., description="Type of target (url or ip)")
    scanned_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of the threat intel analysis")
    virustotal: Optional[VirusTotalReport] = Field(None, description="VirusTotal report results")
    urlscan: Optional[UrlScanReport] = Field(None, description="URLScan report results")
    safebrowsing: Optional[SafeBrowsingReport] = Field(None, description="Google Safe Browsing report results")
    abuseipdb: Optional[AbuseIpDbReport] = Field(None, description="AbuseIPDB report results")
    summary_verdict: str = Field("unknown", description="Aggregated threat level verdict (clean, suspicious, malicious, unknown)")
    max_reputation_score: float = Field(0.0, description="Calculated max risk/reputation level across engines (0 to 100)")


class ThreatIntelScanRequest(BaseModel):
    """Request schema for initiating a custom threat intelligence scan."""

    target: str = Field(..., min_length=4, max_length=2048, description="Target URL or IP address to scan")
    engines: Optional[List[str]] = Field(
        None,
        description="Select specific engines to scan (virustotal, urlscan, safebrowsing, abuseipdb). Defaults to all applicable."
    )
