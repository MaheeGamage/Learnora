from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import logging

# Load environment variables from .env file BEFORE importing modules that need them
load_dotenv()

from app.config import settings
from app.features.learning_path_planner.router import router as learning_path_router
from app.features.concept.router import router as concept_router
from app.features.user_knowledge.router import router as user_knowledge_router
from app.features.users.router import router as users_router
from app.database import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Async lifespan context manager for startup/shutdown"""
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.VERSION}")
    logger.info(f"Environment: {settings.APP_ENV}")
    await init_db()
    yield
    # Shutdown
    logger.info("Shutting down application")


# Initialize FastAPI app with async lifespan
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered learning path planner",
    version=settings.VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan
)

# TODO: Make sure to configure CORS origins properly in production
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(
    learning_path_router,
    prefix=f"{settings.API_V1_PREFIX}/learning-paths",
    tags=["learning-paths"]
)

app.include_router(
    concept_router,
    prefix=f"{settings.API_V1_PREFIX}/concepts",
    tags=["concepts"]
)

app.include_router(
    user_knowledge_router,
    prefix=f"{settings.API_V1_PREFIX}/user-knowledge",
    tags=["user-knowledge"]
)

# Register user/auth router
app.include_router(
    users_router,
    prefix=settings.API_V1_PREFIX,
)


@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.VERSION,
        "environment": settings.APP_ENV
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "environment": settings.APP_ENV,
        "version": settings.VERSION
    }