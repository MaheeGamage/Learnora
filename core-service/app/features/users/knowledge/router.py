"""API router for user knowledge operations."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from app.features.users.knowledge.service import UserKnowledgeService

router = APIRouter()
service = UserKnowledgeService()


class MarkKnownRequest(BaseModel):
    """Request to mark a concept as known."""
    user_id: str
    concept_id: str


class MarkLearningRequest(BaseModel):
    """Request to mark a concept as currently learning."""
    user_id: str
    concept_id: str


class AssignPathRequest(BaseModel):
    """Request to assign a learning path to a user."""
    user_id: str
    thread_id: str


class UserKnowledgeResponse(BaseModel):
    """Response with user knowledge information."""
    user_id: str
    known_concepts: List[str]
    learning_concepts: List[str]


@router.post("/mark-known")
def mark_concept_known(request: MarkKnownRequest):
    """
    Mark that a user knows a concept.
    
    - **user_id**: The user identifier
    - **concept_id**: The concept identifier
    """
    try:
        service.mark_concept_as_known(request.user_id, request.concept_id)
        return {"message": f"Concept {request.concept_id} marked as known for user {request.user_id}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/mark-learning")
def mark_concept_learning(request: MarkLearningRequest):
    """
    Mark that a user is currently learning a concept.
    
    - **user_id**: The user identifier
    - **concept_id**: The concept identifier
    """
    try:
        service.mark_concept_as_learning(request.user_id, request.concept_id)
        return {"message": f"Concept {request.concept_id} marked as learning for user {request.user_id}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/assign-path")
def assign_learning_path(request: AssignPathRequest):
    """
    Assign a learning path to a user.
    
    - **user_id**: The user identifier
    - **thread_id**: The learning path thread identifier
    """
    try:
        service.assign_learning_path_to_user(request.user_id, request.thread_id)
        return {"message": f"Learning path {request.thread_id} assigned to user {request.user_id}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{user_id}", response_model=UserKnowledgeResponse)
def get_user_knowledge(user_id: str):
    """
    Get all knowledge information for a user.
    
    - **user_id**: The user identifier
    """
    # Get known concepts
    known_uris = service.get_user_known_concepts(user_id)
    known_ids = [str(uri).split("#")[-1] for uri in known_uris]
    
    # Get learning concepts
    learning_uris = service.get_user_learning_concepts(user_id)
    learning_ids = [str(uri).split("#")[-1] for uri in learning_uris]
    
    return UserKnowledgeResponse(
        user_id=user_id,
        known_concepts=known_ids,
        learning_concepts=learning_ids
    )


@router.get("/{user_id}/knows/{concept_id}")
def check_user_knows_concept(user_id: str, concept_id: str):
    """
    Check if a user knows a specific concept.
    
    - **user_id**: The user identifier
    - **concept_id**: The concept identifier
    """
    knows = service.user_knows_concept(user_id, concept_id)
    return {
        "user_id": user_id,
        "concept_id": concept_id,
        "knows": knows
    }
