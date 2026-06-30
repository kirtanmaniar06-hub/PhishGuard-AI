"""
PhishGuard AI — Explanation Endpoints

API router to request descriptive natural language explanations for scans.
"""

from fastapi import APIRouter, HTTPException, status
from app.schemas.explanation import ExplanationRequest, ExplanationResponse
from app.services.explanation.manager import ExplanationManager

router = APIRouter()
manager = ExplanationManager()


@router.post(
    "/explain",
    response_model=ExplanationResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate a natural language explanation for a scan prediction"
)
async def explain_threat(payload: ExplanationRequest):
    """
    Generate a natural language explanation for the given scan prediction heuristics
    and threat intelligence outputs.
    """
    try:
        explanation = await manager.explain(
            payload.url,
            payload.verdict,
            payload.heuristics,
            payload.threat_intel
        )
        # Determine provider dynamically based on OpenAI config
        provider = "ai" if manager.openai_service.is_configured() else "rules"
        return {
            "explanation": explanation,
            "provider": provider
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Explanation generation failed: {str(e)}"
        )
