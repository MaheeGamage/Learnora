"""FastAPI router for MCQ generation endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

from app.features.agent.mcq_generator.schemas import (
    MCQGenerationRequest,
    MCQGenerationResponse,
)
from app.features.agent.mcq_generator.service import get_mcq_agent
from app.features.users.users import current_active_user
from app.features.users.models import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mcq", tags=["MCQ Generation"])


@router.post(
    "/generate",
    response_model=MCQGenerationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate MCQ questions",
    description="""
    Generate multiple-choice questions for a given concept using AI.
    
    The agent will create questions based on:
    - The concept name and description
    - Difficulty level (Beginner/Intermediate/Advanced)
    - Learning path context (prerequisites)
    
    Questions are automatically validated to ensure:
    - Exactly 4 options (A-D)
    - One correct answer
    - Appropriate difficulty level
    - Clear explanations
    """
)
async def generate_mcq_questions(
    request: MCQGenerationRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user)
) -> MCQGenerationResponse:
    """
    Generate MCQ questions for knowledge evaluation.
    
    Args:
        request: MCQ generation request with concept details
        user: Authenticated user (from dependency)
        
    Returns:
        MCQGenerationResponse with generated questions
        
    Raises:
        HTTPException: If generation fails
    """
    try:
        logger.info(
            f"User {user.email} requesting {request.question_count} MCQs "
            f"for concept: {request.concept_name} (Level: {request.difficulty_level.value})"
        )
        
        # Get the MCQ agent
        agent = get_mcq_agent()
        
        # Generate MCQs
        response = await agent.generate_mcqs(
            db=db,
            current_user=user,
            concept_name=request.concept_name,
            difficulty_level=request.difficulty_level,
            question_count=request.question_count,
            concept_description=request.concept_description,
            learning_path_db_id=request.learning_path_db_id,
            learning_path=request.learning_path,
            concept_id=request.concept_id
        )
        
        logger.info(
            f"Successfully generated {len(response.questions)} MCQs "
            f"for concept: {request.concept_name}"
        )
        
        return response
        
    except ValueError as e:
        logger.error(f"Validation error in MCQ generation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error generating MCQs: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate MCQ questions. Please try again."
        )


# TODO: Delete on 21 Nov 2025 if this no used till this date
# @router.post(
#     "/generate/sync",
#     response_model=MCQGenerationResponse,
#     status_code=status.HTTP_201_CREATED,
#     summary="Generate MCQ questions (synchronous)",
#     description="Synchronous version of MCQ generation endpoint"
# )
# def generate_mcq_questions_sync(
#     request: MCQGenerationRequest,
#     user: User = Depends(current_active_user)
# ) -> MCQGenerationResponse:
#     """
#     Synchronous MCQ generation endpoint.
    
#     Use this if you need synchronous processing (e.g., in non-async contexts).
#     """
#     try:
#         logger.info(
#             f"User {user.email} requesting {request.question_count} MCQs (sync) "
#             f"for concept: {request.concept_name}"
#         )
        
#         # Get the MCQ agent
#         agent = get_mcq_agent()
        
#         # Generate MCQs synchronously
#         response = agent.generate_mcqs_sync(
#             concept_name=request.concept_name,
#             difficulty_level=request.difficulty_level,
#             question_count=request.question_count,
#             concept_description=request.concept_description,
#             learning_path=request.learning_path,
#             concept_id=request.concept_id
#         )
        
#         logger.info(
#             f"Successfully generated {len(response.questions)} MCQs (sync) "
#             f"for concept: {request.concept_name}"
#         )
        
#         return response
        
#     except ValueError as e:
#         logger.error(f"Validation error in MCQ generation: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=str(e)
#         )
#     except Exception as e:
#         logger.error(f"Error generating MCQs: {str(e)}", exc_info=True)
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Failed to generate MCQ questions. Please try again."
#         )
