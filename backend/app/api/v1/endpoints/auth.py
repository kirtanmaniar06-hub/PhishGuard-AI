"""
PhishGuard AI — Authentication Endpoints

Provides routes for user registration, login, token refresh, and logout.
Supports standard OAuth2 Form parameters for Swagger UI integration.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.token import RefreshTokenRequest, TokenResponse
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import AuthService
from app.services.user_service import UserService

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(
    user_in: UserCreate, db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """Create a new user account with unique email and username."""
    # Check if email is already taken
    existing_email = await UserService.get_by_email(db, user_in.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists",
        )

    # Check if username is already taken
    existing_username = await UserService.get_by_username(db, user_in.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this username already exists",
        )

    user = await UserService.create(db, user_in)
    return user


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate and get tokens",
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Log in using username/email and password.
    
    Returns access and refresh tokens. Fits OAuth2 standards.
    """
    user = await UserService.authenticate(
        db, username_or_email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return await AuthService.create_session(db, user)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Renew access token using refresh token",
)
async def refresh(
    refresh_in: RefreshTokenRequest, db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """Rotate the refresh token and obtain a new access token."""
    return await AuthService.refresh_session(db, refresh_in.refresh_token)


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Revoke session and log out",
)
async def logout(
    refresh_in: RefreshTokenRequest, db: AsyncSession = Depends(get_db)
) -> dict:
    """Invalidate a refresh token, logging the user out."""
    await AuthService.revoke_session(db, refresh_in.refresh_token)
    return {"detail": "Successfully logged out and session revoked"}
