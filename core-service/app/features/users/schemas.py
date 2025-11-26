"""
Pydantic schemas for user operations
"""
from fastapi_users import schemas
from typing import Optional


class UserRead(schemas.BaseUser[int]):
    """
    Schema for reading user data.
    Used when returning user information from API.
    """
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserCreate(schemas.BaseUserCreate):
    """
    Schema for creating a new user.
    Used during user registration.
    """
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserUpdate(schemas.BaseUserUpdate):
    """
    Schema for updating user data.
    Used when users update their profile.
    """
    first_name: Optional[str] = None
    last_name: Optional[str] = None
