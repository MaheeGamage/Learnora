from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.features.learning_path_planner.schemas import (
    LearningPathCreate,
    StartRequest,
    ResumeRequest,
    GraphResponse,
    LearningPathResponse
)
from app.features.learning_path_planner.service import LearningPathService
from app.features.learning_path_planner import crud
from typing import List

router = APIRouter()


@router.post("/start", response_model=GraphResponse)
async def start_graph(request: StartRequest, db: AsyncSession = Depends(get_db)):
    """Start a new learning path"""
    return await LearningPathService.start_learning_path(db, request.learning_topic)


@router.post("/resume", response_model=GraphResponse)
async def resume_graph(request: ResumeRequest, db: AsyncSession = Depends(get_db)):
    """Resume an existing learning path"""
    try:
        return await LearningPathService.resume_learning_path(
            db, request.thread_id, request.human_answer
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{thread_id}", response_model=LearningPathResponse)
async def get_learning_path(thread_id: str, db: AsyncSession = Depends(get_db)):
    """Get learning path details"""
    db_learning_path = await crud.get_learning_path(db, thread_id)
    if not db_learning_path:
        raise HTTPException(status_code=404, detail="Learning path not found")
    return db_learning_path


@router.get("/", response_model=List[LearningPathResponse])
async def list_learning_paths(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """List all learning paths"""
    return await crud.get_all_learning_paths(db, skip=skip, limit=limit)

@router.post("/", response_model=LearningPathResponse)
async def create_learning_path(request: LearningPathCreate, db: AsyncSession = Depends(get_db)):
    """Create a new learning path"""
    return await crud.create_learning_path(db, request)