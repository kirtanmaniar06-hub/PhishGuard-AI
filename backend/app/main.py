"""
PhishGuard AI — Application Factory Entrypoint

Configures the FastAPI application instance, registers CORS policies,
attaches versioned routers, defines the startup lifespan sequence
(including superadmin seeding), and configures structured logging.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import logger, setup_logging
from app.database.session import SessionLocal
from app.models.user import UserRole
from app.middleware.logging import RequestLoggingMiddleware
from app.routers.api import api_router
from app.schemas.user import UserCreate
from app.services.user_service import UserService



@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup initialization and shutdown cleanup tasks."""
    # 1. Initialize Loguru logging configuration
    setup_logging()
    logger.info("Starting up PhishGuard AI Application Server...")

    # 2. Seed default superadmin if configured and not present in DB
    async with SessionLocal() as db:
        try:
            admin_email = settings.FIRST_ADMIN_EMAIL
            existing_admin = await UserService.get_by_email(db, admin_email)
            if not existing_admin:
                logger.info(f"Superadmin not found. Seeding admin: {admin_email}")
                admin_data = UserCreate(
                    email=admin_email,
                    username=settings.FIRST_ADMIN_USERNAME,
                    password=settings.FIRST_ADMIN_PASSWORD,
                )
                await UserService.create(db, admin_data, role=UserRole.ADMIN)
                logger.info("Default Superadmin successfully seeded.")
            else:
                logger.info("Default Superadmin already present. Seeding skipped.")
        except Exception as err:
            logger.error(f"Failed to seed superadmin on startup: {err}")

    yield

    logger.info("Shutting down PhishGuard AI Application Server...")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Enterprise-grade security scanning & authentication APIs.",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register custom request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Register Versioned API Router
app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["System Health"], summary="Check service status")
async def health_check() -> dict:
    """Return application server status."""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
    }
