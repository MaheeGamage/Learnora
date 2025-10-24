from sqlalchemy.orm import Session
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

logger = logging.getLogger(__name__)


class LearningPathService:
    """Business logic for learning path operations"""
    
    @staticmethod
    def start_learning_path(db: Session, topic: str) -> GraphResponse:
        """Start a new learning path"""
        # Generate unique thread ID
        thread_id = str(uuid4())
        config = {"configurable": {"thread_id": thread_id}}
        initial_state = {"topic": topic}
        
        # Save to database
        learning_path_create = LearningPathCreate(
            thread_id=thread_id,
            topic=topic
        )
        crud.create_learning_path(db, learning_path_create)
        
        # Run graph
        result = graph.invoke(initial_state, config)
        message_threads = result.get("messages", {})
        
        logger.info(f"Started learning path with thread_id: {thread_id}")
        
        return GraphResponse(
            thread_id=thread_id,
            messages=message_threads
        )
    
    @staticmethod
    def resume_learning_path(db: Session, thread_id: str, human_answer: str) -> GraphResponse:
        """Resume an existing learning path"""
        # Check if learning path exists
        db_learning_path = crud.get_learning_path(db, thread_id)
        if not db_learning_path:
            raise ValueError(f"Learning path with thread_id {thread_id} not found")
        
        config = {"configurable": {"thread_id": thread_id}}
        state = {"messages": [HumanMessage(content=human_answer)]}
        
        # Update graph state
        graph.update_state(config, state)
        
        # Run graph
        result = graph.invoke(None, config)
        message_threads = result.get("messages", {})
        
        # Update database with new state
        update_data = LearningPathUpdate(graph_state=result)
        crud.update_learning_path(db, thread_id, update_data)
        
        logger.info(f"Resumed learning path with thread_id: {thread_id}")
        
        return GraphResponse(
            thread_id=thread_id,
            messages=message_threads
        )