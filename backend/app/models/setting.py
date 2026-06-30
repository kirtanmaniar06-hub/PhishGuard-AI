import datetime
from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base

class SystemSetting(Base):
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    key: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    value: Mapped[str] = mapped_column(String(1024), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
