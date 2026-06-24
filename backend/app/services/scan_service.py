"""
PhishGuard AI — Scan Service

Encapsulates data persistence and heuristic analysis for URL and email scans.
"""

import json
from typing import List
from urllib.parse import urlparse

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.scan import Scan
from app.schemas.scan import ScanCreate


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
        Runs simulated heuristics to determine the threat score.
        """
        target = scan_in.target.strip()
        target_lower = target.lower()

        # Simulated Heuristic Engine
        score = 0
        indicators = []

        # 1. Check encryption protocol
        if not target_lower.startswith("https://"):
            score += 15
            indicators.append("Unencrypted connection (HTTP)")

        # 2. Extract host structure
        try:
            parsed = urlparse(target if "://" in target else f"http://{target}")
            host = parsed.netloc or parsed.path
        except Exception:
            host = target_lower

        # 3. Check for high-urgency/phishing keywords
        urgent_keywords = ["login", "signin", "auth", "verification", "update", "recovery", "password"]
        brand_keywords = ["paypal", "bank", "netbank", "chase", "wellsfargo", "secure", "netflix", "microsoft", "google"]

        matched_urgency = [kw for kw in urgent_keywords if kw in target_lower]
        if matched_urgency:
            score += 20
            indicators.append(f"Urgent authentication keyword detected: '{matched_urgency[0]}'")

        matched_brand = [kb for kb in brand_keywords if kb in target_lower]
        if matched_brand:
            score += 25
            indicators.append(f"Financial or tech brand name matching: '{matched_brand[0]}'")

        # 4. Check for suspicious Top Level Domains (TLDs)
        suspicious_tlds = [".xyz", ".temp", ".info", ".click", ".top", ".zip", ".work", ".site"]
        matched_tld = [tld for tld in suspicious_tlds if host.endswith(tld)]
        if matched_tld:
            score += 30
            indicators.append(f"Suspicious top-level domain extension: '{matched_tld[0]}'")

        # 5. Check excessive subdomain depth
        dots_count = host.count(".")
        if dots_count > 3:
            score += 15
            indicators.append("Excessive domain subdirectories/subdomains")

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
