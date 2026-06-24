"""
PhishGuard AI — API Dependencies

Defines reusable dependencies for FastAPI route handlers, including
database injection, current user fetching, and role authorization.
"""

from typing import List

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.user import User, UserRole
from app.security.jwt import decode_token
from app.services.user_service import UserService

# OAuth2 standard bearer token extraction.
# Points to the login endpoint for Swagger UI "Authorize" integration.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    """
    Validate the JWT access token and return the associated User.

    Raises 401 UNAUTHORIZED if the token is invalid, expired,
    or the user does not exist.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token)
        user_id_str: str = payload.get("sub")
        token_type: str = payload.get("type")

        if not user_id_str or token_type != "access":
            raise credentials_exception

        user_id = int(user_id_str)
    except (JWTError, ValueError):
        raise credentials_exception

    user = await UserService.get_by_id(db, user_id)
    if not user:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Ensure the authenticated user account is active."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return current_user


class RoleChecker:
    """Dependency helper to enforce specific user roles."""

    def __init__(self, allowed_roles: List[UserRole]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_active_user)) -> User:
        """Verify the user's role belongs to the allowed list."""
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to access this resource",
            )
        return current_user


# Role dependency instances for route handlers
get_current_admin = RoleChecker([UserRole.ADMIN])
get_current_active_standard_user = RoleChecker([UserRole.USER, UserRole.ADMIN])
