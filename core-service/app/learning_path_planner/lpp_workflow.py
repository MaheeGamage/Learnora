import os, json, re
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, BaseMessage
from langgraph.graph import START, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langchain.globals import set_verbose, set_debug
from typing import Sequence
from typing_extensions import Annotated, TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import SystemMessage, trim_messages

# Initialize model
model = init_chat_model("gemini-2.5-flash", model_provider="google_genai")

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
assessment_prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are a personalized AI tutor. The learner wants to learn about {topic}. "
            "Ask 3-5 clarifying questions to understand their current knowledge level, background, and specific learning goals. "
            "Be concise and focused."
        ),
        MessagesPlaceholder(variable_name="messages"),
    ])

# Define the learning path generation prompt
generation_prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are an expert learning path designer. Based on the learner's profile, create a comprehensive learning path for {topic}. "
            + JSONLD_STRUCTURE +
            "\n\nIMPORTANT: Output ONLY the JSON-LD knowledge graph, no additional text or explanation. "
            "Ensure the JSON is valid and properly formatted."
        ),
        MessagesPlaceholder(variable_name="messages"),
    ])

# Define the state
class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    topic: str


def run_graph(prompt_template: ChatPromptTemplate, topic: str, messages: list[BaseMessage]):
    """Generic reusable LangGraph runner for a given prompt."""
    workflow = StateGraph(state_schema=State)

    def call_model(state: State):
        prompt = prompt_template.invoke(state)
        response = model.invoke(prompt)
        return {"messages": response}

    workflow.add_edge(START, "model")
    workflow.add_node("model", call_model)
    app = workflow.compile(checkpointer=MemorySaver())

    config = {"configurable": {"thread_id": "abc123"}}

    output = app.invoke({"messages": messages, "topic": topic}, config)
    return output["messages"][-1].content, output["messages"]

def ask_clarifying_questions(topic: str):
    """Ask clarifying questions"""
    content, messages = run_graph(
        prompt_template=assessment_prompt,
        topic=topic,
        messages=[HumanMessage("Let's start")],
    )
    return messages, content


def generate_learning_path(topic: str, conversation_history, user_answers: str):
    """Generate learning path as JSON-LD"""
    user_input = HumanMessage(user_answers)
    messages = conversation_history + [user_input]

    content, _ = run_graph(
        prompt_template=generation_prompt,
        topic=topic,
        messages=messages,
    )
    return content

def extract_json(content: str):
    """Extract JSON object from text"""
    content = re.sub(r'```json\s*', '', content)
    content = re.sub(r'```\s*', '', content)
    match = re.search(r'\{.*\}', content, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None
    return None