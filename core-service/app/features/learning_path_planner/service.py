from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4
from langchain_core.messages import HumanMessage
from app.features.learning_path_planner import crud
from app.features.learning_path_planner.schemas import (
    LearningPathCreate, 
    LearningPathUpdate,
    GraphResponse
)
from app.features.learning_path_planner.graph import graph
import logging
import asyncio

logger = logging.getLogger(__name__)


class LearningPathService:
    """Business logic for learning path operations"""
    
    @staticmethod
    async def start_learning_path(db: AsyncSession, topic: str) -> GraphResponse:
        """Start a new learning path"""
        # Generate unique thread ID
        thread_id = str(uuid4())
        config = {"configurable": {"thread_id": thread_id}}
        initial_state = {"topic": topic}
        
        # Save to database (async)
        learning_path_create = LearningPathCreate(
            thread_id=thread_id,
            topic=topic
        )
        await crud.create_learning_path(db, learning_path_create)
        
        # Run graph (sync code - run in thread pool to avoid blocking)
        result = await asyncio.to_thread(graph.invoke, initial_state, config)
        message_threads = result.get("messages", {})
        
        logger.info(f"Started learning path with thread_id: {thread_id}")
        
        return GraphResponse(
            thread_id=thread_id,
            messages=message_threads
        )
    
    @staticmethod
    async def resume_learning_path(db: AsyncSession, thread_id: str, human_answer: str) -> GraphResponse:
        """Resume an existing learning path"""
        # Check if learning path exists (async)
        db_learning_path = await crud.get_learning_path(db, thread_id)
        if not db_learning_path:
            raise ValueError(f"Learning path with thread_id {thread_id} not found")
        
        config = {"configurable": {"thread_id": thread_id}}
        state = {"messages": [HumanMessage(content=human_answer)]}
        
        # Update graph state (sync code - run in thread pool)
        await asyncio.to_thread(graph.update_state, config, state)
        
        # Run graph (sync code - run in thread pool)
        result = await asyncio.to_thread(graph.invoke, None, config)
        message_threads = result.get("messages", {})
        
        # Update database with new state (async)
        update_data = LearningPathUpdate(graph_state=result)
        await crud.update_learning_path(db, thread_id, update_data)
        
        logger.info(f"Resumed learning path with thread_id: {thread_id}")
        
        return GraphResponse(
            thread_id=thread_id,
            messages=message_threads
        )