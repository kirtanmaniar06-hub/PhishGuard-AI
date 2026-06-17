"""
PhishGuard AI — Authentication Service

Coordinates token creation, rotation, validation, and session revocation.
Implements a secure refresh token rotation strategy to prevent reuse.
"""

import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from jose import JWTError

from app.core.config import settings
from app.core.logging import logger
from app.models.user import User
from app.models.token import RefreshToken
from app.security.jwt import create_access_token, create_refresh_token, decode_token
from app.schemas.token import TokenResponse


class AuthService:
    """Security actions and token lifecycle coordination."""

    @staticmethod
    async def create_session(db: AsyncSession, user: User) -> TokenResponse:
        """
        Create a new login session: issue access + refresh token pair
        and store the refresh token hash/value in the database.
        """
        access_token = create_access_token(subject=user.id, role=user.role.value)
        refresh_token_str = create_refresh_token(subject=user.id)

        # Store refresh token details in database
        expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
        
        db_refresh = RefreshToken(
            token=refresh_token_str,
            user_id=user.id,
            expires_at=expires_at,
            is_revoked=False,
        )
        
        db.add(db_refresh)
        await db.commit()
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token_str,
            token_type="bearer",
        )

    @staticmethod
    async def refresh_session(db: AsyncSession, refresh_token_str: str) -> TokenResponse:
        """
        Validate the provided refresh token, rotate it (revoke/delete old,
        issue new pair), and return a new session.
        """
        try:
            # 1. Decode JWT to verify signature and expiry
            payload = decode_token(refresh_token_str)
            token_type = payload.get("type")
            if token_type != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type",
                )
            user_id_str = payload.get("sub")
            if not user_id_str:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token claims",
                )
            user_id = int(user_id_str)
        except (JWTError, ValueError) as e:
            logger.warning(f"Failed to decode refresh token: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        # 2. Check the database for the refresh token
        result = await db.execute(
            select(RefreshToken)
            .where(RefreshToken.token == refresh_token_str)
            .execution_options(populate_existing=True)
        )
        db_token = result.scalar_one_or_none()

        if not db_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token not found",
            )

        if db_token.is_revoked:
            # Reuse attack detection: revoke all tokens for this user
            logger.error(f"Revoked refresh token reuse detected for user {db_token.user_id}!")
            await db.execute(
                select(RefreshToken)
                .where(RefreshToken.user_id == db_token.user_id)
            )
            # Revoke all tokens for this user
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
            )

        if db_token.is_expired:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expired",
            )

        # 3. Retrieve user
        user_result = await db.execute(select(User).where(User.id == db_token.user_id))
        user = user_result.scalar_one_or_none()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is deactivated or not found",
            )

        # 4. Revoke the old token (or delete it to clean up the DB)
        # We will delete the old one to keep the DB size minimal
        await db.delete(db_token)
        await db.commit()

        # 5. Issue new session (creates new access + refresh token)
        return await AuthService.create_session(db, user)

    @staticmethod
    async def revoke_session(db: AsyncSession, refresh_token_str: str) -> None:
        """Revoke a refresh token by deleting it from the database."""
        result = await db.execute(
            select(RefreshToken).where(RefreshToken.token == refresh_token_str)
        )
        db_token = result.scalar_one_or_none()
        if db_token:
            await db.delete(db_token)
            await db.commit()
            logger.info(f"Session revoked for user {db_token.user_id}")
        else:
            logger.warning("Revocation requested for non-existent token")
