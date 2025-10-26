"""
Authentication configuration and backends
"""
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from app.config import settings

# Secret key for JWT (from settings)
SECRET = settings.SECRET_KEY

# Bearer token transport (Authorization: Bearer <token>)
bearer_transport = BearerTransport(tokenUrl="api/v1/auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    """
    JWT strategy for token generation and validation.
    
    Tokens expire after 1 hour (3600 seconds) by default.
    You can adjust the lifetime_seconds parameter as needed.
    """
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)


# Authentication backend
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)
