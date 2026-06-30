import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

class ThreatReport(Base):
    __tablename__ = "threat_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    scan_id: Mapped[int] = mapped_column(Integer, ForeignKey("scans.id", ondelete="SET NULL"), nullable=True, index=True)
    domain: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    classification: Mapped[str] = mapped_column(String(100), nullable=False)
    risk_level: Mapped[str] = mapped_column(String(50), nullable=False)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    details: Mapped[str] = mapped_column(String(2048), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    scan = relationship("Scan", backref="threat_reports")
