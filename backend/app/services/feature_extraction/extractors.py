"""
PhishGuard AI — Concrete Feature Extractors

Contains concrete implementations of BaseFeatureExtractor, each targeting
a specific heuristic signal or structural property of a URL.
"""

import re
from ipaddress import ip_address
from urllib.parse import urlparse
from typing import Dict, List, Any

from app.services.feature_extraction.base import BaseFeatureExtractor


class UrlLengthExtractor(BaseFeatureExtractor):
    """Extracts the overall character length of the URL."""

    @property
    def feature_name(self) -> str:
        return "url_length"

    def extract(self, url: str) -> int:
        return len(url)


class DotsCountExtractor(BaseFeatureExtractor):
    """Extracts the count of dots in both the full URL and the host domain."""

    @property
    def feature_name(self) -> str:
        return "dots_count"

    def extract(self, url: str) -> Dict[str, int]:
        try:
            parsed = urlparse(url if "://" in url else f"http://{url}")
            host = parsed.netloc or parsed.path.split("/")[0]
        except Exception:
            host = ""
        
        return {
            "total": url.count("."),
            "domain": host.count(".")
        }


class SubdomainsExtractor(BaseFeatureExtractor):
    """Extracts subdomain components from the domain portion of the URL."""

    @property
    def feature_name(self) -> str:
        return "subdomains"

    def extract(self, url: str) -> Dict[str, Any]:
        try:
            parsed = urlparse(url if "://" in url else f"http://{url}")
            host = parsed.netloc or parsed.path.split("/")[0]
            # Strip port if present
            if ":" in host:
                host = host.split(":")[0]
        except Exception:
            host = ""

        # Remove common prefix like www.
        if host.startswith("www."):
            host = host[4:]

        parts = host.split(".")
        
        # Simple heuristic to isolate subdomains:
        # e.g., 'sub1.sub2.example.com' -> parts: ['sub1', 'sub2', 'example', 'com']
        # If parts has less than 3 elements (e.g. 'example.com'), no subdomains.
        # Handle multi-part suffixes (e.g., 'example.co.uk' -> parts: ['example', 'co', 'uk'])
        is_multipart_tld = len(parts) >= 3 and parts[-2] in ("co", "com", "org", "net", "edu", "gov", "ac")
        
        slice_offset = -3 if is_multipart_tld else -2
        
        subdomains = []
        if len(parts) + slice_offset > 0:
            subdomains = parts[:slice_offset]

        return {
            "list": subdomains,
            "count": len(subdomains)
        }


class SpecialCharactersExtractor(BaseFeatureExtractor):
    """Extracts count of special character characters often seen in malicious URLs."""

    @property
    def feature_name(self) -> str:
        return "special_characters"

    def extract(self, url: str) -> Dict[str, int]:
        # Characters typically used in obfuscation, subdomains, redirection or query spam
        target_chars = ["@", "-", "_", "?", "=", "&", "//"]
        counts = {}
        for char in target_chars:
            counts[char] = url.count(char)
        return counts


class HttpsExtractor(BaseFeatureExtractor):
    """Checks if the URL utilizes safe SSL/TLS protocol."""

    @property
    def feature_name(self) -> str:
        return "is_https"

    def extract(self, url: str) -> bool:
        return url.lower().startswith("https://")


class IpAddressExtractor(BaseFeatureExtractor):
    """Determines if the domain is a raw IP address (obfuscation technique)."""

    @property
    def feature_name(self) -> str:
        return "is_ip_address"

    def extract(self, url: str) -> bool:
        try:
            parsed = urlparse(url if "://" in url else f"http://{url}")
            host = parsed.netloc or parsed.path.split("/")[0]
            if ":" in host:
                host = host.split(":")[0]
            # Try parsing host as IPv4/IPv6
            ip_address(host)
            return True
        except ValueError:
            return False


class EncodedCharactersExtractor(BaseFeatureExtractor):
    """Checks for URL percent-encoded characters (%20, %3D, etc.)."""

    @property
    def feature_name(self) -> str:
        return "encoded_characters"

    def extract(self, url: str) -> Dict[str, Any]:
        # Match percent symbol followed by two hex digits
        matches = re.findall(r"%[0-9a-fA-F]{2}", url)
        return {
            "has_encoding": len(matches) > 0,
            "count": len(matches),
            "matches": list(set(matches))  # Unique list
        }


class SuspiciousKeywordsExtractor(BaseFeatureExtractor):
    """Checks for phishing or brand keywords within the domain/path."""

    # Pre-defined list of common phishing indicators
    KEYWORDS = {
        "urgency": [
            "login", "signin", "auth", "verification", "update", "recovery", "password", 
            "secure", "confirm", "account", "billing", "support", "service", "helpdesk"
        ],
        "brands": [
            "paypal", "chase", "wellsfargo", "bank", "netflix", "microsoft", "google", 
            "apple", "amazon", "facebook", "evil", "phish", "hack", "malicious", "virus"
        ]
    }

    @property
    def feature_name(self) -> str:
        return "suspicious_keywords"

    def extract(self, url: str) -> Dict[str, List[str]]:
        url_lower = url.lower()
        matched_urgency = [kw for kw in self.KEYWORDS["urgency"] if kw in url_lower]
        matched_brands = [kb for kb in self.KEYWORDS["brands"] if kb in url_lower]
        
        return {
            "urgency": matched_urgency,
            "brands": matched_brands,
            "all_matched": list(set(matched_urgency + matched_brands))
        }
