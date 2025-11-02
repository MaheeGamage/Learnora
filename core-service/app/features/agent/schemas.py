from pydantic import BaseModel
from typing import Optional, Any, List, Literal


class ChatRequest(BaseModel):
    """Request schema for chat interactions."""
    message: str
    topic: Optional[str] = None  # Required only for new conversations


class ChatMessage(BaseModel):
    """Individual message in a conversation."""
    role: Literal["human", "ai", "system"]
    content: str


class ChatResponse(BaseModel):
    """Response schema for chat interactions."""
    thread_id: str
    status: Literal["in_progress", "awaiting_generation", "completed"]
    messages: List[ChatMessage]
    topic: Optional[str] = None
    learning_path: Optional[Any] = None  # Raw JSON learning path when completed
