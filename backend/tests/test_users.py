"""
PhishGuard AI — User & RBAC Tests

Verifies profile endpoints and enforces role-based access control (RBAC).
Checks that standard users are forbidden from accessing admin-only routes.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import UserRole
from app.schemas.user import UserCreate
from app.services.user_service import UserService


@pytest.mark.asyncio
async def test_get_profile_authenticated(client: AsyncClient) -> None:
    """Test retrieving current user's profile with a valid access token."""
    # Register user
    email = "profile@phishguard.ai"
    username = "profileuser"
    register_payload = {
        "email": email,
        "username": username,
        "password": "SecurePassword123!",
    }
    await client.post("/api/v1/auth/register", json=register_payload)

    # Login
    login_payload = {
        "username": username,
        "password": "SecurePassword123!",
    }
    login_res = await client.post("/api/v1/auth/login", data=login_payload)
    token = login_res.json()["access_token"]

    # Get profile
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("/api/v1/users/me", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert data["email"] == email
    assert data["username"] == username
    assert data["role"] == UserRole.USER.value


@pytest.mark.asyncio
async def test_get_profile_unauthenticated(client: AsyncClient) -> None:
    """Test fetching profile without credentials fails."""
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_users_denied_to_standard_user(client: AsyncClient) -> None:
    """Test that a regular user cannot list all users (RBAC check)."""
    # Register and login standard user
    register_payload = {
        "email": "user@phishguard.ai",
        "username": "standarduser",
        "password": "SecurePassword123!",
    }
    await client.post("/api/v1/auth/register", json=register_payload)

    login_payload = {
        "username": "standarduser",
        "password": "SecurePassword123!",
    }
    login_res = await client.post("/api/v1/auth/login", data=login_payload)
    token = login_res.json()["access_token"]

    # Attempt to access user listing
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("/api/v1/users/", headers=headers)
    assert response.status_code == 403
    assert "Not enough permissions" in response.json()["detail"]


@pytest.mark.asyncio
async def test_list_users_allowed_to_admin(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Test that an admin user can successfully list all users (RBAC check)."""
    # Create an admin user directly in the database session
    admin_in = UserCreate(
        email="admin-rbac@phishguard.ai",
        username="rbacadmin",
        password="SecureAdminPassword123!",
    )
    await UserService.create(db_session, admin_in, role=UserRole.ADMIN)

    # Login admin user
    login_payload = {
        "username": "rbacadmin",
        "password": "SecureAdminPassword123!",
    }
    login_res = await client.post("/api/v1/auth/login", data=login_payload)
    token = login_res.json()["access_token"]

    # Access user listing
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("/api/v1/users/", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert len(data) >= 1
    # Check that the admin user is in the list
    usernames = [u["username"] for u in data]
    assert "rbacadmin" in usernames
