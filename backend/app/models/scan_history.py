import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

class ScanHistory(Base):
    __tablename__ = "scan_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    scan_id: Mapped[int] = mapped_column(Integer, ForeignKey("scans.id", ondelete="CASCADE"), nullable=False, index=True)
    notes: Mapped[str] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships using backref to avoid modifying original User/Scan models
    user = relationship("User", backref="scan_histories")
    scan = relationship("Scan")
