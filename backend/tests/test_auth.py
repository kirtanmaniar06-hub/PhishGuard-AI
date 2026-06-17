"""
PhishGuard AI — Authentication Tests

Verifies user registration, login, refresh token, and logout logic.
All tests execute asynchronously using isolated SQLite database contexts.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import UserRole
from app.services.user_service import UserService


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient) -> None:
    """Test standard user registration."""
    payload = {
        "email": "test@phishguard.ai",
        "username": "testuser",
        "password": "SecurePassword123!",
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    
    data = response.json()
    assert data["email"] == payload["email"]
    assert data["username"] == payload["username"]
    assert "id" in data
    assert data["role"] == UserRole.USER.value
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test registration with an email that is already registered."""
    # Seed user first
    payload = {
        "email": "duplicate@phishguard.ai",
        "username": "user1",
        "password": "SecurePassword123!",
    }
    await client.post("/api/v1/auth/register", json=payload)

    # Register duplicate
    payload_dup = {
        "email": "duplicate@phishguard.ai",
        "username": "user2",
        "password": "SecurePassword123!",
    }
    response = await client.post("/api/v1/auth/register", json=payload_dup)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient) -> None:
    """Test login with valid credentials."""
    # Register user
    register_payload = {
        "email": "login@phishguard.ai",
        "username": "loginuser",
        "password": "SecurePassword123!",
    }
    await client.post("/api/v1/auth/register", json=register_payload)

    # Login
    login_payload = {
        "username": "loginuser",
        "password": "SecurePassword123!",
    }
    response = await client.post("/api/v1/auth/login", data=login_payload)
    assert response.status_code == 200
    
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient) -> None:
    """Test login fails with incorrect password."""
    # Register user
    register_payload = {
        "email": "wrongpass@phishguard.ai",
        "username": "wrongpassuser",
        "password": "SecurePassword123!",
    }
    await client.post("/api/v1/auth/register", json=register_payload)

    # Login
    login_payload = {
        "username": "wrongpassuser",
        "password": "IncorrectPassword!",
    }
    response = await client.post("/api/v1/auth/login", data=login_payload)
    assert response.status_code == 401
    assert "Incorrect" in response.json()["detail"]


@pytest.mark.asyncio
async def test_token_refresh(client: AsyncClient) -> None:
    """Test rotating the token using a valid refresh token."""
    # Register and login
    register_payload = {
        "email": "refresh@phishguard.ai",
        "username": "refreshuser",
        "password": "SecurePassword123!",
    }
    await client.post("/api/v1/auth/register", json=register_payload)

    login_payload = {
        "username": "refreshuser",
        "password": "SecurePassword123!",
    }
    login_res = await client.post("/api/v1/auth/login", data=login_payload)
    tokens = login_res.json()
    refresh_token = tokens["refresh_token"]

    # Refresh
    refresh_res = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
    )
    assert refresh_res.status_code == 200
    
    new_tokens = refresh_res.json()
    assert "access_token" in new_tokens
    assert "refresh_token" in new_tokens
    assert new_tokens["refresh_token"] != refresh_token  # Ensure rotation


@pytest.mark.asyncio
async def test_logout_revocation(client: AsyncClient) -> None:
    """Test that logout deletes/revokes the refresh token."""
    register_payload = {
        "email": "logout@phishguard.ai",
        "username": "logoutuser",
        "password": "SecurePassword123!",
    }
    await client.post("/api/v1/auth/register", json=register_payload)

    login_payload = {
        "username": "logoutuser",
        "password": "SecurePassword123!",
    }
    login_res = await client.post("/api/v1/auth/login", data=login_payload)
    tokens = login_res.json()
    refresh_token = tokens["refresh_token"]

    # Logout
    logout_res = await client.post(
        "/api/v1/auth/logout", json={"refresh_token": refresh_token}
    )
    assert logout_res.status_code == 200
    assert "Successfully logged out" in logout_res.json()["detail"]

    # Try refreshing again — should fail
    refresh_res = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
    )
    assert refresh_res.status_code == 401
