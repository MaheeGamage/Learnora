from fastapi import FastAPI
from dotenv import load_dotenv

# Load environment variables from .env file BEFORE importing modules that need them
load_dotenv()

from app.features.learning_path_planner.router import router as learning_path_router
from app.database.connection import engine
from app.database.base import BaseModel

# Create database tables
BaseModel.metadata.create_all(bind=engine)

app = FastAPI()
# add_cors_middleware(app)

# Register lesson routers
app.include_router(learning_path_router)