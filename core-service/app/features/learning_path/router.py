from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.features.learning_path.schemas import (
    LearningPathCreate,
    LearningPathUpdate,
    LearningPathResponse,
)
from app.features.learning_path.service import LearningPathService
from typing import List
from app.features.users.models import User
from app.features.users.users import current_active_user

router = APIRouter()
service = LearningPathService()

LEARNING_PATH_NOT_FOUND = "Learning path not found"


# ===== CRUD Endpoints =====

@router.post("/", response_model=LearningPathResponse, status_code=201)
async def create_learning_path(
    learning_path: LearningPathCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(current_active_user)
):
    """Create a new learning path."""
    return await service.create_learning_path(db, learning_path, current_user)


@router.get("/{learning_path_id}", response_model=LearningPathResponse)
async def get_learning_path(
    learning_path_id: int,
    include_kg: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(current_active_user)
):
    """Get a learning path by ID with optional knowledge graph data.
    
    Query Parameters:
        include_kg: If true, includes the knowledge graph data as jsonld in the response
    """
    learning_path = await service.get_learning_path(db, learning_path_id, current_user, include_kg)
    if not learning_path:
        raise HTTPException(status_code=404, detail=LEARNING_PATH_NOT_FOUND)
    return learning_path


@router.get("/", response_model=List[LearningPathResponse])
async def get_all_learning_paths(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(current_active_user)
):
    """Get all learning paths with pagination."""
    return await service.get_all_learning_paths(db, current_user, skip, limit)


@router.put("/{learning_path_id}", response_model=LearningPathResponse)
async def update_learning_path(
    learning_path_id: int,
    update_data: LearningPathUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(current_active_user)
):
    """Update a learning path.
    
    You can update:
    - topic: Learning path topic/title
    - graph_uri: Graph URI reference
    - kg_data: Knowledge graph data in JSON-LD format (triggers RDF update)
    - goal: Learning path goal (used with kg_data)
    
    Note: When kg_data is provided, the knowledge graph will be updated in RDF storage.
    """
    learning_path = await service.update_learning_path(db, learning_path_id, update_data, current_user)
    if not learning_path:
        raise HTTPException(status_code=404, detail=LEARNING_PATH_NOT_FOUND)
    return learning_path


@router.delete("/{learning_path_id}", status_code=204)
async def delete_learning_path(
    learning_path_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(current_active_user)
):
    """Delete a learning path."""
    deleted = await service.delete_learning_path(db, learning_path_id, current_user)
    if not deleted:
        raise HTTPException(status_code=404, detail=LEARNING_PATH_NOT_FOUND)
    return None
