"""
PhishGuard AI — Scan Endpoints

Routes for submitting URL/email scans and retrieving scan history.
"""

from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.scan import ScanCreate, ScanResponse
from app.services.scan_service import ScanService

router = APIRouter()


@router.post(
    "/",
    response_model=ScanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Analyze a URL for phishing threats",
)
async def create_scan(
    scan_in: ScanCreate,
    db: AsyncSession = Depends(get_db),
) -> ScanResponse:
    """
    Submit a URL for heuristic analysis.

    Runs simulated detection checks and returns a threat score,
    risk classification, verdict, and list of risk indicators.
    No authentication required to allow guest scanning.
    """
    scan = await ScanService.create_scan(db, scan_in)
    return scan


@router.get(
    "/",
    response_model=List[ScanResponse],
    status_code=status.HTTP_200_OK,
    summary="List all scan history records",
)
async def list_scans(
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(50, ge=1, le=100, description="Max records to return"),
    db: AsyncSession = Depends(get_db),
) -> List[ScanResponse]:
    """Retrieve paginated list of past scans ordered by most recent first."""
    scans = await ScanService.get_multi(db, skip=skip, limit=limit)
    return scans


@router.get(
    "/{scan_id}",
    response_model=ScanResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a specific scan by ID",
)
async def get_scan(
    scan_id: int,
    db: AsyncSession = Depends(get_db),
) -> ScanResponse:
    """Retrieve a single scan record by its ID."""
    from fastapi import HTTPException
    scan = await ScanService.get_by_id(db, scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan
