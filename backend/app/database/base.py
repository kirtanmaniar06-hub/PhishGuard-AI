"""
PhishGuard AI — Declarative Base

Defines the SQLAlchemy declarative base metadata class.
All database models must inherit from this Base.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Declarative base class for all database models."""

    pass
