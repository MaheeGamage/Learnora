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

# Initialize the model
model = init_chat_model("gemini-2.5-flash", model_provider="google_genai")

class LearningPathState(MessagesState):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    topic: str | None = None
    
# JSON-LD structure description for the AI
JSONLD_STRUCTURE = """
The output must be a valid JSON-LD knowledge graph with the following structure:
- "@context": Defines the schema with "name", "requires" (prerequisite relationships), and namespace prefix
- "@graph": Array of concept objects, where each object has:
  - "@id": Unique identifier using the namespace prefix (e.g., "kg:concept-name")
  - "@type": Always "Concept"
  - "name": Human-readable name of the concept
  - "requires": (optional) Array of "@id" references to prerequisite concepts

The graph should represent a learning path with concepts ordered by dependencies, where foundational concepts have no prerequisites and advanced concepts build upon them.
"""

# Define the initial assessment prompt
assessment_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a personalized AI tutor. The learner wants to learn about {topic}. "
            "Ask 3-5 clarifying questions to understand their current knowledge level, background, and specific learning goals. "
            "Be concise and focused."
        ),
        (
            "human",
            "hello"
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

# Define the learning path generation prompt
generation_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert learning path designer. Based on the learner's profile, create a comprehensive learning path for {topic}. "
            + JSONLD_STRUCTURE +
            "\n\nIMPORTANT: Output ONLY the JSON-LD knowledge graph, no additional text or explanation. "
            "Ensure the JSON is valid and properly formatted."
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

def assess_knowledge(state: LearningPathState) -> LearningPathState:
    topic = state.get("topic")
    
    if topic is None:
        responed_topic = interrupt("Please provide a topic you want to learn about.")
        topic = responed_topic
        
    state["topic"] = topic
    
    prompt = assessment_prompt.invoke(state)
    response = model.invoke(prompt)
    return {"messages": [response], "topic": topic}

def generate_learning_path(state: LearningPathState) -> LearningPathState:
    prompt = generation_prompt.invoke(state)
    response = model.invoke(prompt)
    return {"messages": [response]}

# --- Graph Construction ---
builder = StateGraph(LearningPathState)

builder.add_node("assess_knowledge", assess_knowledge)
builder.add_node("generate_learning_path", generate_learning_path)

builder.add_edge(START, "assess_knowledge")
builder.add_edge("assess_knowledge", "generate_learning_path")
builder.add_edge("generate_learning_path", END)

memory = MemorySaver()
graph = builder.compile(checkpointer=memory, interrupt_before=["generate_learning_path"])

# --- Exports ---
__all__ = ["graph", "LearningPathState"]