"""
PhishGuard AI — WHOIS Service

Provides modular WHOIS domain queries, normalized attribute mapping,
robust error handling, and in-memory TTL caching.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from urllib.parse import urlparse

import whois

logger = logging.getLogger("phishguard")


class WhoisService:
    """Service to handle WHOIS lookup queries, normalization, and caching."""

    # In-memory cache mapping domain -> (timestamp, normalized_data)
    _cache: Dict[str, tuple[datetime, Dict[str, Any]]] = {}
    
    # Cache duration (TTL): 24 hours
    CACHE_TTL_SECONDS = 86400

    @classmethod
    def _extract_domain(cls, target: str) -> str:
        """Helper to extract domain host from any target URL or host string."""
        target = target.strip()
        if not target:
            return ""
        try:
            # If target has no protocol scheme, prefix with http:// for urlparse to work
            if "://" not in target:
                parsed = urlparse(f"http://{target}")
            else:
                parsed = urlparse(target)
            host = parsed.netloc or parsed.path.split("/")[0]
            # Strip port if present
            if ":" in host:
                host = host.split(":")[0]
            # Strip www.
            if host.startswith("www."):
                host = host[4:]
            return host.lower()
        except Exception:
            return target.lower()

    @classmethod
    def _normalize_date(cls, date_val: Any) -> Optional[datetime]:
        """Normalizes various date formats returned by python-whois to a standard datetime."""
        if not date_val:
            return None
        
        # If it's a list, python-whois returned multiple updates/dates, take the first one
        if isinstance(date_val, list):
            for d in date_val:
                res = cls._normalize_date(d)
                if res:
                    return res
            return None
            
        if isinstance(date_val, datetime):
            return date_val
            
        if isinstance(date_val, str):
            # Try a couple of common ISO parses
            for fmt in (
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d",
                "%d-%b-%Y"
            ):
                try:
                    return datetime.strptime(date_val.strip(), fmt)
                except ValueError:
                    continue
        return None

    @classmethod
    def _normalize_string(cls, val: Any) -> Optional[str]:
        """Normalizes whois strings (handles lists of strings)."""
        if not val:
            return None
        if isinstance(val, list):
            # Filter empty values and take the first non-empty string
            non_empty = [str(x).strip() for x in val if x]
            return non_empty[0] if non_empty else None
        return str(val).strip()

    @classmethod
    def get_whois_data(cls, target: str) -> Dict[str, Any]:
        """
        Perform a WHOIS query for the given URL/domain.
        Returns a normalized dictionary. Utilizes local caching.
        """
        domain = cls._extract_domain(target)
        if not domain:
            return {
                "domain": "",
                "registrar": None,
                "domain_age_days": None,
                "creation_date": None,
                "expiration_date": None,
                "owner": None,
                "country": None,
                "cached": False,
                "status": "INVALID_DOMAIN"
            }

        # Check Cache
        now = datetime.now(timezone.utc)
        if domain in cls._cache:
            cache_time, cached_data = cls._cache[domain]
            if (now - cache_time).total_seconds() < cls.CACHE_TTL_SECONDS:
                # Return cached data marked as cached
                result = cached_data.copy()
                result["cached"] = True
                return result

        logger.info(f"Performing live WHOIS lookup for domain: {domain}")
        try:
            # Query whois registry
            w = whois.whois(domain)
            
            # Extract and normalize creation and expiration dates
            creation = cls._normalize_date(w.get("creation_date"))
            expiration = cls._normalize_date(w.get("expiration_date"))

            # Calculate domain age in days
            age_days = None
            if creation:
                # Make creation offset-naive for safe subtraction against local naive utcnow
                creation_naive = creation.replace(tzinfo=None)
                age_days = (datetime.utcnow() - creation_naive).days
                # Prevent negative age due to clock drift
                age_days = max(0, age_days)

            # Map fields
            normalized = {
                "domain": domain,
                "registrar": cls._normalize_string(w.get("registrar")),
                "domain_age_days": age_days,
                "creation_date": creation.isoformat() if creation else None,
                "expiration_date": expiration.isoformat() if expiration else None,
                "owner": cls._normalize_string(w.get("org") or w.get("name")),
                "country": cls._normalize_string(w.get("country")),
                "cached": False,
                "status": "SUCCESS"
            }
            
            # Store in cache
            cls._cache[domain] = (now, normalized)
            return normalized

        except Exception as err:
            logger.error(f"WHOIS lookup failed for {domain}: {err}")
            # Return fallback schema with status code instead of throwing
            return {
                "domain": domain,
                "registrar": None,
                "domain_age_days": None,
                "creation_date": None,
                "expiration_date": None,
                "owner": None,
                "country": None,
                "cached": False,
                "status": f"ERROR: {str(err)}"
            }
