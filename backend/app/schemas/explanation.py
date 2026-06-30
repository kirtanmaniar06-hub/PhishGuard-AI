"""
PhishGuard AI — Explanation API Schemas

Defines request/response contracts for generating natural language explanations.
"""

from typing import Dict, Any
from pydantic import BaseModel, Field


class ExplanationRequest(BaseModel):
    """
    Request model containing telemetry data to explain.
    """
    url: str = Field(..., description="The analyzed URL.")
    verdict: str = Field(..., description="The overall classification or status.")
    heuristics: Dict[str, Any] = Field(..., description="Heuristic features dictionary.")
    threat_intel: Dict[str, Any] = Field(..., description="Aggregated Threat Intelligence report data.")


class ExplanationResponse(BaseModel):
    """
    Response model containing the generated explanation.
    """
    explanation: str = Field(..., description="Human-readable reason for the prediction.")
    provider: str = Field(..., description="Explanation engine provider ('ai' or 'rules').")
