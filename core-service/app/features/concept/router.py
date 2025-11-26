"""API router for concept operations."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.features.concept.service import ConceptService

router = APIRouter()
service = ConceptService()


class ConceptCreate(BaseModel):
    """Request model for creating a concept."""
    concept_id: str
    label: str
    description: Optional[str] = None
    prerequisites: Optional[List[str]] = None


class ConceptResponse(BaseModel):
    """Response model for concept information."""
    id: str
    label: str
    prerequisites: List[str] = []


@router.post("/", response_model=ConceptResponse)
def create_concept(concept: ConceptCreate):
    """
    Create a new concept in the knowledge graph.
    
    - **concept_id**: Unique identifier (e.g., "Python", "MachineLearning")
    - **label**: Human-readable name
    - **description**: Optional detailed description
    - **prerequisites**: List of prerequisite concept IDs
    """
    try:
        concept_uri = service.add_concept(
            concept_id=concept.concept_id,
            label=concept.label,
            description=concept.description,
            prerequisites=concept.prerequisites
        )
        
        # Get prerequisites for response
        prereq_uris = service.get_concept_prerequisites(concept.concept_id)
        prereq_ids = [str(p).split("#")[-1] for p in prereq_uris]
        
        return ConceptResponse(
            id=concept.concept_id,
            label=concept.label,
            prerequisites=prereq_ids
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[str])
def list_concepts():
    """
    List all concepts in the knowledge graph.
    
    Returns a list of concept IDs.
    """
    concept_uris = service.get_all_concepts()
    return [str(uri).split("#")[-1] for uri in concept_uris]


@router.get("/{concept_id}", response_model=ConceptResponse)
def get_concept(concept_id: str):
    """
    Get information about a specific concept.
    
    - **concept_id**: The unique identifier of the concept
    """
    concept_uri = service.get_concept(concept_id)
    if not concept_uri:
        raise HTTPException(status_code=404, detail="Concept not found")
    
    # Get prerequisites
    prereq_uris = service.get_concept_prerequisites(concept_id)
    prereq_ids = [str(p).split("#")[-1] for p in prereq_uris]
    
    return ConceptResponse(
        id=concept_id,
        label=concept_id.replace("_", " ").title(),
        prerequisites=prereq_ids
    )


@router.get("/{concept_id}/prerequisites", response_model=List[str])
def get_concept_prerequisites(concept_id: str):
    """
    Get prerequisites for a specific concept.
    
    - **concept_id**: The unique identifier of the concept
    """
    concept_uri = service.get_concept(concept_id)
    if not concept_uri:
        raise HTTPException(status_code=404, detail="Concept not found")
    
    prereq_uris = service.get_concept_prerequisites(concept_id)
    return [str(uri).split("#")[-1] for uri in prereq_uris]
