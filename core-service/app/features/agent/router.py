from fastapi import APIRouter, Depends, HTTPException, status
from app.features.agent.schemas import ChatRequest, ChatResponse, InitChatRequest
from app.features.agent.service import AgentService
from typing import Optional
import logging
from app.features.users.users import current_active_user
from app.database import get_db
from app.features.users.models import User
from sqlalchemy.ext.asyncio import AsyncSession

# Import MCQ router
from app.features.agent.mcq_generator.router import router as mcq_router

logger = logging.getLogger(__name__)

router = APIRouter()

# Include MCQ generation routes
router.include_router(mcq_router)
service = AgentService()


@router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
async def start_chat(request: InitChatRequest,  db: AsyncSession = Depends(get_db), user: User = Depends(current_active_user)):
    """
    Start a new chat conversation with the learning path agent.
    
    Requires topic to be provided in the request.
    Returns a new thread_id and initial AI response.
    """
    
    try:
        response = await service.invoke_graph(
            db=db,
            message=request.message,
            thread_id=None,
            user=user,
            mode=request.mode
        )
        return response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error starting chat: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start conversation"
        )


@router.post("/chat/{thread_id}", response_model=ChatResponse)
async def continue_chat(thread_id: str, request: ChatRequest, db: AsyncSession = Depends(get_db), user: User = Depends(current_active_user)):
    """
    Continue an existing chat conversation.
    
    Uses the thread_id from the URL to continue the conversation.
    Topic is optional as it's already set in the conversation state.
    """
    try:
        response = await service.invoke_graph(
            db=db,
            user=user,
            message=request.message,
            thread_id=thread_id
        )
        return response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error continuing chat {thread_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to continue conversation"
        )


@router.get("/chat/{thread_id}", response_model=ChatResponse)
async def get_chat(thread_id: str, db: AsyncSession = Depends(get_db),user: User = Depends(current_active_user)):
    """
    Retrieve the current state and history of a chat conversation.
    
    Returns all messages, current status, and learning path (if completed).
    """
    try:
        response = service.get_conversation(thread_id)
        return response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error retrieving chat {thread_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversation"
        )
