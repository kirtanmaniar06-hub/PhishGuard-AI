"""
PhishGuard AI — Token Pydantic Schemas

Defines schemas for JWT structure, payloads, and request validation.
"""

from typing import Optional

from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    """Schema returned upon successful authentication containing
    access and refresh tokens.
    """

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="Secure refresh token")
    token_type: str = Field("bearer", description="Token type, typically 'bearer'")


class TokenPayload(BaseModel):
    """Claims contained within a decoded JWT access token."""

    sub: Optional[str] = None  # user ID
    role: Optional[str] = None  # user role
    exp: Optional[int] = None  # expiration timestamp


class RefreshTokenRequest(BaseModel):
    """Schema for requesting a new access token using a refresh token."""

    refresh_token: str = Field(..., description="Valid refresh token")
