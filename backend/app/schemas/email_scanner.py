"""
PhishGuard AI — Email Scanner Schemas

Defines request/response contracts for email parsing and threat analysis scans.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class EmailScanRequest(BaseModel):
    """
    Payload containing the raw MIME email text or plain text to scan.
    """
    raw_email: str = Field(..., description="The raw email text or MIME content.")


class EmailScanResponse(BaseModel):
    """
    Aggregated email analysis report returned to the client.
    """
    score: int = Field(..., ge=0, le=100, description="Email risk score from 0 (Safe) to 100 (Critical).")
    status: str = Field(..., description="Risk evaluation status: 'SAFE', 'SUSPICIOUS', or 'CRITICAL'.")
    explanation: str = Field(..., description="Descriptive summary explaining the risk level.")
    sender: Optional[str] = Field(None, description="Extracted sender email address or header.")
    subject: Optional[str] = Field(None, description="Extracted email subject header.")
    links: List[str] = Field(default=[], description="List of hyperlinks found inside the email body.")
    keywords: List[str] = Field(default=[], description="Matched phishing/urgency keywords.")
    attachments: List[str] = Field(default=[], description="List of file attachments found.")
    indicators: List[str] = Field(default=[], description="Individual threat indicator findings.")
