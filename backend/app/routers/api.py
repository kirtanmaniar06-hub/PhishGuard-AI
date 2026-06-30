"""
PhishGuard AI — API Router Registry

Combines endpoint sub-routers (auth, users, scans) and registers them
under the v1 API prefix.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, scans, users, threat_intel, ml, explanation, email_scanner

api_router = APIRouter()

# Register sub-routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(scans.router, prefix="/scans", tags=["Scans"])
api_router.include_router(threat_intel.router, prefix="/threat-intel", tags=["Threat Intelligence"])
api_router.include_router(ml.router, prefix="/ml", tags=["Machine Learning"])
api_router.include_router(explanation.router, prefix="/explanation", tags=["AI Explanation"])
api_router.include_router(email_scanner.router, prefix="/email-scanner", tags=["Email Scanner"])

