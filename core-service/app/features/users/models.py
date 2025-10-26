"""
User models for authentication using fastapi-users
"""
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import String, Column, Integer, DateTime
from sqlalchemy.sql import func
from app.database.base import Base


class User(SQLAlchemyBaseUserTable[int], Base):
    """
    User model with fastapi-users integration.
    
    Inherits from SQLAlchemyBaseUserTable which provides:
    - id: int (primary key)
    - email: str (unique, indexed)
    - hashed_password: str
    - is_active: bool (default True)
    - is_superuser: bool (default False)
    - is_verified: bool (default False)
    """
    __tablename__ = "users"
    
    # Override id to ensure it's defined properly
    id = Column(Integer, primary_key=True, index=True)
    
    # Add custom fields
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    
    # Add timestamp fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"
    
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.email
