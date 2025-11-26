"""
FastAPI Users instance and current user dependencies
"""
from fastapi_users import FastAPIUsers
from app.features.users.models import User
from app.features.users.manager import get_user_manager
from app.features.users.auth import auth_backend

# Create FastAPI Users instance (SYNC mode)
fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

# Dependencies for getting current user
current_active_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)
current_verified_user = fastapi_users.current_user(active=True, verified=True)

# Optional dependency (returns None if not authenticated)
optional_current_user = fastapi_users.current_user(optional=True)
