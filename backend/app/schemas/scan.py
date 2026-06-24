"""
PhishGuard AI — Scan Pydantic Schemas

Defines validation and serialization schemas for email and URL scanning.
"""

import datetime
import json
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ScanCreate(BaseModel):
    """Schema for incoming scan requests."""

    target: str = Field(
        ...,
        min_length=4,
        max_length=2048,
        description="URL to analyze for phishing markers",
    )
    type: str = Field(
        "URL",
        description="The classification channel of the ingest vector",
    )


class ScanResponse(BaseModel):
    """Schema for scan response serialization."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    target: str
    type: str
    score: int
    status: str
    verdict: str
    indicators: List[str]
    created_at: datetime.datetime

    @field_validator("indicators", mode="before")
    @classmethod
    def parse_indicators(cls, v):
        """Parse JSON array string from database to a list of strings."""
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
                return []
            except Exception:
                return []
        return v
