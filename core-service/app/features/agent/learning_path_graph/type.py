from pydantic import BaseModel, Field, Json
from langgraph.graph import START, END, MessagesState, StateGraph
from typing_extensions import Annotated, TypedDict
from typing import Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

from app.features.agent.type import AgentState, AgentMode

# State definition for Intention Clarification phase
class IntentionState(AgentState):
    """
    State tracking the intention clarification conversation.
    
    Focus: Understanding what the user wants to ACHIEVE (not their knowledge level)
    """
    # Conversation history (inherited from MessagesState)
    # messages: Annotated[Sequence[BaseMessage], add_messages] - This gets inherited from AgentState
    
    # Extracted information
    desired_outcome: str | None = None  # What the user wants to achieve/do/create
    context: dict | None = None  # Optional: background, timeline, constraints
    topic: str | None = None  # Summarized topic/subject of the learning path
    
    # learning path
    concept_graph: Json  # List of {concept, prerequisites}
    
    # Flow control
    is_intention_clear: bool = False  # Boolean flag: is the intention clear enough?
    follow_up_count: int = 0  # Number of follow-up questions asked (max 3)

# Pydantic model for structured extraction
class IntentionAnalysis(BaseModel):
    """Structured output from intention evaluator."""
    desired_outcome: str | None = Field(
        None, 
        description="What the user wants to achieve, do, or create. Must be action-oriented (e.g., 'build X', 'analyze Y', 'create Z')"
    )
    context: dict | None = Field(
        None,
        description="Optional context: background, timeline, constraints. Only include if user mentions them."
    )
    is_clear: bool = Field(
        description="Is the intention clear and actionable? True if it specifies WHAT they want to do/create, False if vague (e.g., 'learn X')"
    )
    reasoning: str = Field(
        description="Brief explanation of why the intention is clear or not clear"
    )
    
# Pydantic model for output formatting
class IntentionOutput(BaseModel):
    """Final formatted output from intention clarification."""
    topic: str = Field(
        description="A concise topic/subject for this learning path (2-4 words). Examples: 'Web Development', 'Data Analysis', 'Machine Learning'"
    )
    desired_outcome: str = Field(
        description="Clear statement of what the user wants to achieve/do/create"
    )
    context: dict | None = Field(
        None,
        description="Optional context including background, timeline, constraints"
    )
    summary: str = Field(
        description="A brief 1-2 sentence summary of the user's learning intention"
    )
    
# State for Goal Definition phase
class GoalDefinitionState(IntentionState):
    """
    Extends IntentionState with goal-related fields.
    
    Inherits from Step 1:
    - topic, desired_outcome, context
    
    Adds for Step 2:
    - learning_goal, competencies, success_criteria
    """
    # Goal definition fields
    learning_goal: str | None = None  # Formal statement of the learning objective
    competencies: list[str] | None = None  # Key skills/abilities needed
    success_criteria: list[str] | None = None  # How to measure achievement
    
# Pydantic model for goal definition output
class LearningGoalDefinition(BaseModel):
    """Structured learning goal with competencies and success criteria."""
    
    learning_goal: str = Field(
        description="A clear, formal statement of what the learner will be able to do. Should start with 'By the end of this learning path, you will be able to...'"
    )
    
    competencies: list[str] = Field(
        description="List of 4-7 specific skills or abilities needed to achieve the goal. Each should be concrete and measurable.",
        min_length=4,
        max_length=7
    )
    
    success_criteria: list[str] = Field(
        description="List of 3-5 observable indicators that the goal has been achieved. Focus on what the learner can demonstrate or produce.",
        min_length=3,
        max_length=5
    )
    
# State for Concept Graph Construction phase
class ConceptGraphState(GoalDefinitionState):
    """
    Extends GoalDefinitionState with concept graph.
    
    Inherits from Steps 1 & 2:
    - topic, desired_outcome, context
    - learning_goal, competencies, success_criteria
    
    Adds for Step 3:
    - concept_graph
    """
    # Concept graph field
    concept_graph: list[dict] | None = None  # List of {concept, prerequisites}