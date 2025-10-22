from fastapi import FastAPI
from dotenv import load_dotenv

# Load environment variables from .env file BEFORE importing modules that need them
load_dotenv()

from app.learning_path_planner.learning_path_router import router as learning_path_router

app = FastAPI()
# add_cors_middleware(app)

# Register lesson routers
app.include_router(learning_path_router)