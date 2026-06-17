"""
PhishGuard AI — User Endpoints

Protected routes for user profile retrieval and administrative operations.
"""

from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_current_admin, get_db
from app.models.user import User
from app.schemas.user import UserResponse
from app.services.user_service import UserService

router = APIRouter()


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
)
async def read_user_me(
    current_user: User = Depends(get_current_active_user),
) -> UserResponse:
    """Retrieve details of the currently authenticated user."""
    return current_user


@router.get(
    "/",
    response_model=List[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="List all users",
)
async def read_users(
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(100, ge=1, le=100, description="Limit for pagination"),
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_current_admin), # Enforce Admin Role
) -> List[UserResponse]:
    """
    Retrieve all registered users.
    
    Access is restricted to Admin role only.
    """
    users = await UserService.get_multi(db, skip=skip, limit=limit)
    return users
