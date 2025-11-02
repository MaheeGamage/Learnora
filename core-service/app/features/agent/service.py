import uuid
import json
import re
from enum import Enum
from typing import Optional, List, Any
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from app.features.agent.graph import graph, LearningPathState
from app.features.agent.schemas import ChatResponse, ChatMessage
import logging
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.learning_path.service import LearningPathService
from app.features.learning_path.schemas import LearningPathResponse
from app.features.users.models import User

logger = logging.getLogger(__name__)


class GraphStage(Enum):
    """Enum to represent different stages of graph invocation."""
    NEW_CONVERSATION = "new"  # Starting a new conversation
    RESUME_CONVERSATION = "resume"  # Resuming an existing conversation


class AgentService:
    """Service layer for agent graph interactions."""
    
    def __init__(self):
        self.learning_path_service = LearningPathService()

    def _determine_graph_stage(
        self, thread_id: Optional[str], topic: Optional[str]
    ) -> tuple[GraphStage, str]:
        """
        Determine the graph stage based on thread_id and topic.
        
        Args:
            thread_id: Existing thread ID or None
            topic: Learning topic or None
            
        Returns:
            Tuple of (GraphStage, thread_id)
            
        Raises:
            ValueError: If parameters are invalid
        """
        if thread_id is None:
            # Starting a new conversation
            if not topic:
                raise ValueError("Topic is required for new conversations")
            return GraphStage.NEW_CONVERSATION, str(uuid.uuid4())
        else:
            # Resuming an existing conversation
            return GraphStage.RESUME_CONVERSATION, thread_id

    def invoke_graph(
        self,
        db: AsyncSession,
        user: User,
        message: str,
        thread_id: Optional[str] = None,
        topic: Optional[str] = None,
    ) -> ChatResponse:
        """
        Unified method to handle all graph interactions.
        
        Args:
            message: User's message input
            thread_id: Optional thread ID for continuing conversation
            topic: Required for new conversations (when thread_id is None)
            
        Returns:
            ChatResponse with updated conversation state
            
        Raises:
            ValueError: If topic is missing for new conversation or thread_id is invalid
        """
        # Determine graph stage and get/generate thread_id
        stage, resolved_thread_id = self._determine_graph_stage(thread_id, topic)
        
        # Log the stage
        if stage == GraphStage.NEW_CONVERSATION:
            logger.info(f"Starting new conversation with thread_id: {resolved_thread_id}")
        else:
            logger.info(f"Resuming conversation with thread_id: {resolved_thread_id}")

        # Configure graph with thread_id
        config = {"configurable": {"thread_id": resolved_thread_id}}
        
        state = {}

        try:
            # Build state based on graph stage
            if stage == GraphStage.NEW_CONVERSATION:
                # For new conversations, set topic
                state = {"topic": topic}
            
            # Add message to state if provided
            if message:
                if "messages" in state:
                    state["messages"].append(HumanMessage(content=message))
                else:
                    state["messages"] = [HumanMessage(content=message)]

            # Invoke graph based on stage
            if stage == GraphStage.RESUME_CONVERSATION:
                # For existing conversations, update state then invoke
                graph.update_state(config, state)
                result = graph.invoke(None, config)
            else:
                # For new conversations, invoke with full state
                result = graph.invoke(state, config)
            
            # Get the final state
            state = graph.get_state(config)
            
            # Determine conversation status
            status = self._determine_status(state)
            
            # Extract topic from state
            current_topic = result.get("topic") if result else None
            
            # Format messages
            formatted_messages = self._format_messages(result.get("messages", []))
            
            # Parse and save learning path if completed
            learning_path_response = None
            if status == "completed":
                learning_path_json = self._parse_learning_path(result.get("messages", []))
                
                if learning_path_json:
                    # Saving learning path to DB and storage if completed
                    db_learning_path = self.learning_path_service.parse_and_save_learning_path(
                        db=db,
                        json_data=learning_path_json,
                        topic=current_topic,
                        user=user
                    )
                    # Convert SQLAlchemy model to Pydantic schema
                    learning_path_response = LearningPathResponse.model_validate(db_learning_path)
            
            return ChatResponse(
                thread_id=resolved_thread_id,
                status=status,
                messages=formatted_messages,
                topic=current_topic,
                learning_path=learning_path_response
            )

        except Exception as e:
            logger.error(f"Error invoking graph for thread {resolved_thread_id}: {str(e)}")
            raise

    def get_conversation(self, thread_id: str) -> ChatResponse:
        """
        Retrieve conversation state without invoking the graph.
        
        Args:
            thread_id: The conversation thread ID
            
        Returns:
            ChatResponse with current conversation state
            
        Raises:
            ValueError: If thread_id doesn't exist
        """
        config = {"configurable": {"thread_id": thread_id}}
        
        try:
            state = graph.get_state(config)
            
            if not state or not state.values:
                raise ValueError(f"Thread {thread_id} not found")
            
            # Determine status
            status = self._determine_status(state)
            
            # Extract values from state
            messages = state.values.get("messages", [])
            topic = state.values.get("topic")
            
            # Parse learning path if completed
            learning_path = None
            if status == "completed":
                learning_path = self._parse_learning_path(messages)
            
            # Format messages
            formatted_messages = self._format_messages(messages)
            
            return ChatResponse(
                thread_id=thread_id,
                status=status,
                messages=formatted_messages,
                topic=topic,
                learning_path=learning_path
            )
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error retrieving conversation {thread_id}: {str(e)}")
            raise

    def _determine_status(self, state) -> str:
        """
        Determine conversation status from graph state.
        
        Args:
            state: Graph state object
            
        Returns:
            Status string: "in_progress", "awaiting_generation", or "completed"
        """
        if not state or not state.next:
            # No next node means graph reached END
            return "completed"
        
        # Check if we're at the interrupt point (before generate_learning_path)
        if "generate_learning_path" in state.next:
            return "awaiting_generation"
        
        # Otherwise, still in progress
        return "in_progress"

    def _format_messages(self, messages: List[BaseMessage]) -> List[ChatMessage]:
        """
        Convert LangChain messages to API schema format.
        
        Args:
            messages: List of LangChain BaseMessage objects
            
        Returns:
            List of ChatMessage objects
        """
        formatted = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                role = "human"
            elif isinstance(msg, AIMessage):
                role = "ai"
            elif isinstance(msg, SystemMessage):
                role = "system"
            else:
                role = "system"  # Default fallback
            
            formatted.append(ChatMessage(
                role=role,
                content=msg.content
            ))
        
        return formatted

    def _parse_learning_path(self, messages: List[BaseMessage]) -> Optional[Any]:
        """
        Extract and parse learning path JSON from AI messages.
        
        Args:
            messages: List of conversation messages
            
        Returns:
            Parsed JSON learning path or None if not found/invalid
        """
        # Get the last AI message (should contain the learning path)
        for msg in reversed(messages):
            if isinstance(msg, AIMessage):
                content = msg.content
                
                try:
                    # Try to parse as direct JSON
                    learning_path = json.loads(content)
                    logger.info("Successfully parsed learning path JSON")
                    return learning_path
                except json.JSONDecodeError:
                    # Try to extract JSON from markdown code blocks or mixed content
                    # Look for JSON array pattern
                    json_pattern = r'\[[\s\S]*?\]'
                    matches = re.findall(json_pattern, content)
                    
                    for match in matches:
                        try:
                            learning_path = json.loads(match)
                            logger.info("Successfully extracted and parsed learning path JSON")
                            return learning_path
                        except json.JSONDecodeError:
                            continue
                    
                    logger.warning("Could not parse learning path from AI response")
                    return None
        
        return None
