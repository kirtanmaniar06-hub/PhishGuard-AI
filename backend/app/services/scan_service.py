"""
PhishGuard AI — Scan Service

Encapsulates data persistence and heuristic analysis for URL and email scans.
"""

import json
from typing import List, Optional
from urllib.parse import urlparse

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.scan import Scan
from app.schemas.scan import ScanCreate
from app.services.feature_extraction import FeatureExtractionPipeline
from app.services.whois_service import WhoisService
from app.services.ssl_service import SslService


class ScanService:
    """Handles core business logic and database access for threat scans."""

    @staticmethod
    async def get_by_id(db: AsyncSession, scan_id: int) -> Optional[Scan]:
        """Retrieve a scan record by primary key."""
        result = await db.execute(select(Scan).where(Scan.id == scan_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_multi(
        db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[Scan]:
        """Retrieve a paginated list of scans ordered by newest first."""
        result = await db.execute(
            select(Scan).order_by(Scan.created_at.desc()).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def create_scan(
        db: AsyncSession, scan_in: ScanCreate
    ) -> Scan:
        """
        Analyze a target and persist the scan results.
        Runs concrete, SOLID feature extractors, WHOIS analysis, and SSL evaluation.
        """
        target = scan_in.target.strip()

        # 1. Run URL Feature Extraction Pipeline
        pipeline = FeatureExtractionPipeline()
        features = pipeline.extract_features(target)

        # 2. Run WHOIS registry check
        whois_data = WhoisService.get_whois_data(target)

        # 3. Run SSL Certificate analysis (if target is HTTPS)
        ssl_data = None
        if features["is_https"]:
            ssl_data = SslService.analyze_ssl(target)

        # Evaluate score based on features, WHOIS registry, and SSL attributes
        score = 0
        indicators = []

        # 1. Check protocol security
        if not features["is_https"]:
            score += 20
            indicators.append("Unencrypted connection (HTTP)")

        # 2. Check length obfuscation
        url_len = features["url_length"]
        if url_len > 75:
            score += 15
            indicators.append(f"Excessive URL character length ({url_len} chars)")

        # 3. Check dots count
        domain_dots = features["dots_count"]["domain"]
        if domain_dots > 2:
            score += 15
            indicators.append(f"High number of dots in domain ({domain_dots})")

        # 4. Check subdomain nesting
        subdomain_cnt = features["subdomains"]["count"]
        if subdomain_cnt > 1:
            score += 15
            indicators.append(f"Excessive subdomain nesting ({subdomain_cnt} levels)")

        # 5. Check raw IP hostname
        if features["is_ip_address"]:
            score += 35
            indicators.append("Raw IP address used as host identifier")

        # 6. Check special characters / obfuscation flags
        spec_chars = features["special_characters"]
        if spec_chars.get("@", 0) > 0:
            score += 30
            indicators.append("Credential redirection char '@' detected")
        if spec_chars.get("-", 0) > 2:
            score += 10
            indicators.append("Suspicious hyphen usage in domain name")

        # 7. Check percent-encoded obfuscation
        if features["encoded_characters"]["has_encoding"]:
            score += 15
            indicators.append("URL contains percent-encoded obfuscated characters")

        # 8. Check suspicious keywords
        kw = features["suspicious_keywords"]
        if kw["brands"]:
            score += 25
            indicators.append(f"Brand spoofing indicator matching: '{kw['brands'][0]}'")
        if kw["urgency"]:
            score += 20
            indicators.append(f"Urgent authentication keyword matching: '{kw['urgency'][0]}'")

        # 9. Evaluate domain registration age from WHOIS
        domain_age = whois_data.get("domain_age_days")
        if domain_age is not None:
            if domain_age < 90:
                score += 25
                indicators.append(f"Newly registered domain (Age: {domain_age} days)")
            elif domain_age < 365:
                score += 10
                indicators.append(f"Recent domain registration (Age: {domain_age} days)")

        # 10. Evaluate SSL Certificate Trust
        if ssl_data:
            if not ssl_data.get("valid"):
                status_msg = ssl_data.get("status") or "verification failed"
                if "CONNECTION_FAILURE" in status_msg:
                    score += 15
                    indicators.append("Secure connection failed (TLS handshake timeout or port closed)")
                else:
                    score += 30
                    indicators.append(f"Untrusted SSL/TLS certificate ({status_msg})")
            else:
                trust_score = ssl_data.get("trust_score", 100)
                if trust_score < 100:
                    score += 15
                    indicators.append(f"Weak SSL/TLS certificate profile (Trust Score: {trust_score})")

        # Bound score between 1 and 99
        score = max(1, min(score, 99))

        # Set status based on score thresholds
        if score >= 70:
            status = "CRITICAL"
            verdict = "Warning: AI neural heuristics flagged this URL as high risk for brand spoofing and social engineering."
        elif score >= 35:
            status = "SUSPICIOUS"
            verdict = "Caution: Anomalous indicators detected. Mismatched certificates or newly registered domain traits found."
        else:
            status = "SAFE"
            verdict = "Safe: Scan complete. Low threat matching profile detected, aligned with nominal host signatures."
            if not indicators:
                indicators.append("Standard domain alignment")

        db_scan = Scan(
            target=target,
            type=scan_in.type,
            score=score,
            status=status,
            verdict=verdict,
            indicators=json.dumps(indicators),
        )

        db.add(db_scan)
        await db.commit()
        await db.refresh(db_scan)
        return db_scan
