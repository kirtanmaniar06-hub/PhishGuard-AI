"""
PhishGuard AI — User Service

Encapsulates database operations and authentication logic for User entities.
All operations are executed asynchronously.
"""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate
from app.security.password import get_password_hash, verify_password


class UserService:
    """Business logic handler for Users."""

    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """Fetch a single user by their primary key."""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Fetch a single user by email address."""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_username(db: AsyncSession, username: str) -> Optional[User]:
        """Fetch a single user by username."""
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_multi(
        db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[User]:
        """Fetch a paginated list of users."""
        result = await db.execute(select(User).offset(skip).limit(limit))
        return list(result.scalars().all())

    @staticmethod
    async def create(
        db: AsyncSession, user_in: UserCreate, role: UserRole = UserRole.USER
    ) -> User:
        """Create and persist a new User."""
        hashed_password = get_password_hash(user_in.password)
        db_user = User(
            email=user_in.email,
            username=user_in.username,
            hashed_password=hashed_password,
            role=role,
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user

    @staticmethod
    async def update(db: AsyncSession, db_user: User, user_in: UserUpdate) -> User:
        """Update an existing User profile."""
        update_data = user_in.model_dump(exclude_unset=True)
        if "password" in update_data and update_data["password"]:
            db_user.hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]

        for field, value in update_data.items():
            setattr(db_user, field, value)

        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user

    @staticmethod
    async def authenticate(
        db: AsyncSession, username_or_email: str, password: str
    ) -> Optional[User]:
        """
        Authenticate a user by matching their username/email and password.

        Returns the User object if successful, else None.
        """
        if "@" in username_or_email:
            user = await UserService.get_by_email(db, username_or_email)
        else:
            user = await UserService.get_by_username(db, username_or_email)

        if not user or not user.is_active:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
