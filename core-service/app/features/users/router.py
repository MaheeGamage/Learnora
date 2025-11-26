"""
User authentication and management routes
"""
from fastapi import APIRouter
from app.features.users.users import fastapi_users
from app.features.users.auth import auth_backend
from app.features.users.schemas import UserRead, UserCreate, UserUpdate

router = APIRouter()

# Authentication routes (login, logout)
router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

# User registration
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

# User management (get current user, update, delete)
router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

# Password reset routes
router.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)

# Email verification routes
router.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
