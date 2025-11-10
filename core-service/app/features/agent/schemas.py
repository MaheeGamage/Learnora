from pydantic import BaseModel
from typing import Optional, Any, List, Literal

from app.features.learning_path.schemas import LearningPathResponse
from app.features.agent.type import AgentMode

class BaseChatRequest(BaseModel):
    """Base schema for chat requests."""
    message: str

class ChatRequest(BaseChatRequest):
    """Request schema for chat interactions."""
    message: str
    topic: Optional[str] = None  # Required only for new conversations
    
class InitChatRequest(BaseChatRequest):
    # make all inputs optional by overriding type + default
    message: Optional[str] = None
    mode: Optional[AgentMode] = AgentMode.BASIC

class ChatMessage(BaseModel):
    """Individual message in a conversation."""
    role: Literal["human", "ai", "system"]
    content: str


class ChatResponse(BaseModel):
    """Response schema for chat interactions."""
    thread_id: str
    # status: Literal["in_progress", "awaiting_generation", "completed"]
    messages: List[ChatMessage]
    topic: Optional[str] = None
    learning_path_json: Optional[Any] = None  # Raw JSON learning path when completed
    learning_path: Optional[Any] = None  # DB model instance when completed