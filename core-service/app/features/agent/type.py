from enum import Enum
from click import Option
from typing_extensions import Annotated, TypedDict
from langgraph.graph import START, END, MessagesState, StateGraph
from langchain_core.messages import BaseMessage
from typing import Optional, Sequence
from langgraph.graph.message import add_messages

class AgentMode(Enum):
    """Enum to represent different stages of graph invocation."""
    BASIC = "basic"  # Starting a new conversation
    LPP = "lpp"  # Planning a learning path

class AgentState(MessagesState):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    mode: Optional["AgentMode"] = None
