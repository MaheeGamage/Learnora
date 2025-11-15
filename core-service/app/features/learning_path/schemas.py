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
    user_id: int

class LearningPathCreate(LearningPathBase):
    graph_uri: Optional[str] = None

class LearningPathUpdate(BaseModel):
    topic: Optional[str] = None
    graph_uri: Optional[str] = None
    kg_data: Optional[List[Any]] = None  # JSON-LD format array for KG updates
    goal: Optional[str] = None  # Optional goal update


class LearningPathResponse(LearningPathBase):
    id: int
    graph_uri: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    topic: Optional[str] = None
    user_id: int
    # kg_data now returns parsed JSON-LD (as Python objects) instead of a raw JSON string
    kg_data: Optional[Any] = None
    
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
    graph: str 