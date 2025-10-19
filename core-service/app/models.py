from pydantic import BaseModel
from typing import Optional, Any
from typing import Literal

# --- Start Graph Run ---
class StartRequest(BaseModel):
    learning_topic: str

# --- Resume Paused Graph Run ---
class ResumeRequest(BaseModel):
    thread_id: str
    review_action: Literal["approved", "feedback"]
    human_comment: Optional[str] = None

# --- Minimal API Response ---
class GraphResponse(BaseModel):
    thread_id: str
    # run_status: Literal["finished", "user_feedback", "pending"]
    messages: Optional[Any] = None
