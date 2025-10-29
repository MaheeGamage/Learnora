from pydantic import BaseModel
from typing import Optional, Any, List
from typing import Literal
from datetime import datetime

# --- Start Graph Run ---
class StartRequest(BaseModel):
    learning_topic: str

# --- Resume Paused Graph Run ---
class ResumeRequest(BaseModel):
    thread_id: str
    human_answer: str

# --- Minimal API Response ---
class GraphResponse(BaseModel):
    thread_id: str
    # run_status: Literal["finished", "user_feedback", "pending"]
    messages: Optional[Any] = None

# Database schemas
class LearningPathBase(BaseModel):
    topic: str


class LearningPathCreate(LearningPathBase):
    thread_id: str
    status: str = "active"


class LearningPathUpdate(BaseModel):
    graph_state: Optional[dict] = None
    status: Optional[str] = None


class LearningPathResponse(LearningPathBase):
    id: int
    thread_id: str
    status: str
    graph_state: Optional[dict]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Knowledge Graph schemas
class ConceptInfo(BaseModel):
    """Information about a concept in the knowledge graph."""
    id: str
    label: str
    prerequisites: List[str] = []


class LearningPathKGResponse(BaseModel):
    """Knowledge graph information for a learning path."""
    thread_id: str
    topic: str
    concepts: List[ConceptInfo]
    concept_count: int