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
    
# JSON structure description for the AI
JSON_OUTPUT_FORMAT = """
You must output ONLY a valid JSON array with NO additional text, explanation, or commentary.
Your response must be a single JSON code block containing an array of concept objects.

REQUIRED FORMAT:
[
  {"concept": "ConceptName1", "prerequisites": []},
  {"concept": "ConceptName2", "prerequisites": ["ConceptName1"]},
  {"concept": "ConceptName3", "prerequisites": ["ConceptName1", "ConceptName2"]}
]

RULES:
1. Each object must have exactly two fields: "concept" (string) and "prerequisites" (array of strings)
2. The "concept" field contains the name of a learning concept
3. The "prerequisites" array lists concept names that must be learned first (empty array if none)
4. Foundational concepts have empty prerequisites arrays
5. Advanced concepts list all direct prerequisites by their exact concept names
6. Order concepts from foundational to advanced based on dependency chains
7. Return ONLY the JSON array - no markdown formatting, no backticks, no explanation text

EXAMPLE:
[{"concept":"Variables","prerequisites":[]},{"concept":"Data Types","prerequisites":["Variables"]},{"concept":"Functions","prerequisites":["Variables","Data Types"]}]
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
            "You are an expert learning path designer. Based on the learner's profile and responses, create a comprehensive, well-structured learning path for {topic}. "
            "\n\n" + JSON_OUTPUT_FORMAT +
            "\n\nIMPORTANT INSTRUCTIONS:"
            "\n1. Analyze the learner's knowledge level from the conversation"
            "\n2. Design a learning path appropriate for their background"
            "\n3. Break down {topic} into clear, logical concepts"
            "\n4. Establish prerequisite relationships carefully - each concept should list ALL direct prerequisites"
            "\n5. Ensure foundational concepts come first (empty prerequisites)"
            "\n6. Create a progressive learning sequence from basics to advanced topics"
            "\n7. Output ONLY the JSON array as specified above, with no extra text"
            "\n\nYour response must contain ONLY the JSON array. Do not include any explanation, markdown formatting, or additional commentary."
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