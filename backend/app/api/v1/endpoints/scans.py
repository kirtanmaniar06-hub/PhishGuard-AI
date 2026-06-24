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


@router.post(
    "/features",
    status_code=status.HTTP_200_OK,
    summary="Extract security features from a URL",
)
async def extract_url_features(
    scan_in: ScanCreate,
) -> dict:
    """
    Extract heuristic features from a target URL on-demand.

    Returns detailed structural signals such as length, subdomain depth,
    special characters, HTTPS status, raw IP indicator, percent-encoding details,
    and matching threat keywords.
    """
    from app.services.feature_extraction import FeatureExtractionPipeline
    pipeline = FeatureExtractionPipeline()
    return pipeline.extract_features(scan_in.target)


@router.post(
    "/whois",
    status_code=status.HTTP_200_OK,
    summary="Perform normalized WHOIS query on a domain",
)
async def get_whois_info(
    scan_in: ScanCreate,
) -> dict:
    """
    Perform a WHOIS query on the target URL's domain.

    Returns registrar, domain age in days, creation and expiration date,
    owner if publicly available, and country code. Utilizes 24h caching.
    """
    from app.services.whois_service import WhoisService
    return WhoisService.get_whois_data(scan_in.target)


