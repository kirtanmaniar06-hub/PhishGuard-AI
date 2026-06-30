"""
PhishGuard AI — Database Schema Tests

Verifies normalization, constraints, relationships, and queries for all newly defined schemas
including ScanHistory, ThreatReport, APIKey, SystemSetting, and AuditLog.
"""

import pytest
import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.models.scan import Scan
from app.models.scan_history import ScanHistory
from app.models.threat_report import ThreatReport
from app.models.api_key import APIKey
from app.models.setting import SystemSetting
from app.models.audit_log import AuditLog


@pytest.mark.asyncio
async def test_create_and_query_new_models(db_session: AsyncSession) -> None:
    """Verifies that all new ORM models can be inserted, queried, and verified with relations."""
    db = db_session
    
    # 1. Create dummy User
    user = User(
        email="test_schema@phishguard.ai",
        username="db_schema_test",
        hashed_password="fakehashpassword",
        role=UserRole.USER,
        is_active=True
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # 2. Create dummy Scan
    scan = Scan(
        target="http://phishguard-db-test.com",
        type="URL",
        score=85,
        status="CRITICAL",
        verdict="Suspicious URL detected",
        indicators="[]"
    )
    db.add(scan)
    await db.commit()
    await db.refresh(scan)

    # 3. Create ScanHistory log
    history = ScanHistory(
        user_id=user.id,
        scan_id=scan.id,
        notes="Heuristic scanning via dashboard tool"
    )
    db.add(history)

    # 4. Create ThreatReport entry
    report = ThreatReport(
        scan_id=scan.id,
        domain="phishguard-db-test.com",
        classification="Phishing",
        risk_level="CRITICAL",
        source="AbuseIPDB",
        details="Reported by 12 independent analysts."
    )
    db.add(report)

    # 5. Create APIKey credential
    api_key = APIKey(
        user_id=user.id,
        name="Production Jenkins Agent",
        key_prefix="pk_prod_12345",
        hashed_key="hashedsecretcredentialkey",
        is_active=True,
        expires_at=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=30)
    )
    db.add(api_key)

    # 6. Create Settings value
    setting = SystemSetting(
        key="MAX_URL_SCAN_DEPTH_LIMIT",
        value="5",
        description="Limit depth of sub-page path crawl recursively"
    )
    db.add(setting)

    # 7. Create AuditLog event
    audit = AuditLog(
        user_id=user.id,
        action="API_KEY_ROTATION",
        ip_address="192.168.1.100",
        details="User rotated production deployment API token keys"
    )
    db.add(audit)

    await db.commit()

    # Query and assert relationships
    # Fetch ScanHistory log with relations
    stmt_history = select(ScanHistory).where(ScanHistory.user_id == user.id)
    history_res = (await db.execute(stmt_history)).scalars().first()
    assert history_res is not None
    assert history_res.notes == "Heuristic scanning via dashboard tool"
    assert history_res.user.email == "test_schema@phishguard.ai"
    assert history_res.scan.target == "http://phishguard-db-test.com"

    # Fetch ThreatReport entries linked to scan
    stmt_report = select(ThreatReport).where(ThreatReport.scan_id == scan.id)
    report_res = (await db.execute(stmt_report)).scalars().first()
    assert report_res is not None
    assert report_res.classification == "Phishing"

    # Fetch Settings and check constraints
    stmt_setting = select(SystemSetting).where(SystemSetting.key == "MAX_URL_SCAN_DEPTH_LIMIT")
    setting_res = (await db.execute(stmt_setting)).scalars().first()
    assert setting_res is not None
    assert setting_res.value == "5"

    # Fetch AuditLogs
    stmt_audit = select(AuditLog).where(AuditLog.user_id == user.id)
    audit_res = (await db.execute(stmt_audit)).scalars().first()
    assert audit_res is not None
    assert audit_res.action == "API_KEY_ROTATION"

    # Cleanup test insertions
    await db.delete(history_res)
    await db.delete(report_res)
    await db.delete(api_key)
    await db.delete(setting_res)
    await db.delete(audit_res)
    await db.delete(scan)
    await db.delete(user)
    await db.commit()
