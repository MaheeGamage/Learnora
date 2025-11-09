from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, END, MessagesState, StateGraph
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from typing import Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import Annotated, TypedDict
from langgraph.types import Command, interrupt
from langchain_core.runnables import RunnableConfig

from app.features.agent.type import AgentMode
from app.features.agent.learning_path_graph.learning_path_graph import learning_path_graph
from app.features.agent.learning_path_graph.type import IntentionState
from langchain_core.messages import HumanMessage

class CombAgentState(IntentionState):
    pass

# Initialize the model
model = init_chat_model("gemini-2.5-flash", model_provider="google_genai")

prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are the assistant of an AI-powered casual learning platform called Learnora."
            "Answer all questions to the best of your ability"
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)
    
workflow = StateGraph(state_schema=CombAgentState)

def call_model(state: CombAgentState):
    prompt = prompt_template.invoke(state)
    response = model.invoke(prompt)
    return {"messages": [response]}

def route_mode(state: CombAgentState):
    if state['mode'] == AgentMode.LPP:
        return AgentMode.LPP
    else:
        return AgentMode.BASIC

def reset_mode(state: CombAgentState) -> dict:
    """
    Reset mode to BASIC after subgraph completes.
    
    This allows the graph to return to general chat mode
    for the next user message.
    """
    print("🔄 Resetting mode to BASIC after learning path completion")
    return {"mode": None}

workflow.add_node("basic_chat", call_model)
workflow.add_node("lpp_graph", learning_path_graph)
workflow.add_node("reset_mode", reset_mode)

# workflow.add_edge(START, "basic_chat")

workflow.add_conditional_edges(
    START,
    route_mode,
    {
        AgentMode.BASIC: "basic_chat",
        AgentMode.LPP: "lpp_graph"
    }
)

# After basic chat, go to END
workflow.add_edge("basic_chat", END)

# After LPP graph, reset mode then END
workflow.add_edge("lpp_graph", "reset_mode")
workflow.add_edge("reset_mode", END)

memory = MemorySaver()
graph = workflow.compile(checkpointer=memory)

# --- Exports ---
__all__ = ["graph", "CombAgentState"]