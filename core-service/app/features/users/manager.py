"""
User manager for handling user-related operations
"""
from typing import Optional
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, IntegerIDMixin
from app.features.users.models import User
from app.features.users.database import get_user_db
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Secret key for JWT tokens
SECRET = settings.SECRET_KEY


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    """
    User manager class.
    Handles user registration, verification, password reset, etc.
    """
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        """Called after successful user registration"""
        logger.info(f"User {user.id} ({user.email}) has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        """Called after user requests password reset"""
        logger.info(f"User {user.id} ({user.email}) has requested password reset.")
        logger.debug(f"Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        """Called after user requests email verification"""
        logger.info(f"Verification requested for user {user.id} ({user.email}).")
        logger.debug(f"Verification token: {token}")


async def get_user_manager(user_db=Depends(get_user_db)):
    """Dependency to get user manager instance"""
    yield UserManager(user_db)
