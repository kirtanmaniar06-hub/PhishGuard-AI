"""
PhishGuard AI — Scan Model

Defines the database schema for storing email and URL scans, threat scores,
and detection indicators.
"""

import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Scan(Base):
    """Database representation of an analyzed security vector (URL/Email)."""

    __tablename__ = "scans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    target: Mapped[str] = mapped_column(String(2048), nullable=False)
    type: Mapped[str] = mapped_column(String(50), default="URL", nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)  # SAFE | SUSPICIOUS | CRITICAL
    verdict: Mapped[str] = mapped_column(String(1024), nullable=False)
    indicators: Mapped[str] = mapped_column(String(1024), default="[]", nullable=False)  # JSON list

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<Scan id={self.id} target={self.target[:30]} score={self.score}>"
