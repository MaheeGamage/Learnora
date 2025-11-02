from fastapi import APIRouter, HTTPException, status
from app.features.agent.schemas import ChatRequest, ChatResponse
from app.features.agent.service import AgentService
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
service = AgentService()


@router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
async def start_chat(request: ChatRequest):
    """
    Start a new chat conversation with the learning path agent.
    
    Requires topic to be provided in the request.
    Returns a new thread_id and initial AI response.
    """
    if not request.topic:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Topic is required for starting a new conversation"
        )
    
    try:
        response = service.invoke_graph(
            message=request.message,
            thread_id=None,
            topic=request.topic
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
async def continue_chat(thread_id: str, request: ChatRequest):
    """
    Continue an existing chat conversation.
    
    Uses the thread_id from the URL to continue the conversation.
    Topic is optional as it's already set in the conversation state.
    """
    try:
        response = service.invoke_graph(
            message=request.message,
            thread_id=thread_id,
            topic=request.topic  # Optional, usually None for continuation
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
async def get_chat(thread_id: str):
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
