"""
Database access for user operations
"""
from typing import AsyncGenerator
from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession
from app.features.users.models import User
from app.database import get_db


async def get_user_db(session: AsyncSession = Depends(get_db)) -> AsyncGenerator[SQLAlchemyUserDatabase, None]:
    """
    Dependency to get user database access.
    
    This is ASYNC - required by fastapi-users.
    Provides SQLAlchemy database adapter for fastapi-users.
    
    Usage:
        user_db = Depends(get_user_db)
    """
    yield SQLAlchemyUserDatabase(session, User)
