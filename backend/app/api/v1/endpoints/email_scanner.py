"""
PhishGuard AI — Email Scanner Endpoints

API routes for parsing and assessing email phishing threat profiles.
"""

from fastapi import APIRouter, HTTPException, status
from app.schemas.email_scanner import EmailScanRequest, EmailScanResponse
from app.services.email_scanner.manager import EmailScannerManager

router = APIRouter()
manager = EmailScannerManager()


@router.post(
    "/scan",
    response_model=EmailScanResponse,
    status_code=status.HTTP_200_OK,
    summary="Scan pasted email MIME or text content for threats"
)
async def scan_email(payload: EmailScanRequest):
    """
    Parses headers, sender, attachments, and links of a pasted email to calculate a risk score.
    """
    try:
        report = manager.scan_email(payload.raw_email)
        return report
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Email scanning failed: {str(e)}"
        )
