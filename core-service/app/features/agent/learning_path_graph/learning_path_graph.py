from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, END, MessagesState, StateGraph
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from typing import Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field
from typing_extensions import Annotated, TypedDict
from langgraph.types import Command, interrupt
from typing import Literal
import json

from app.features.agent.learning_path_graph.prompt import evaluator_prompt, followup_prompt, formatter_prompt, goal_definition_prompt, concept_graph_prompt
from app.features.agent.learning_path_graph.type import ConceptGraphState, GoalDefinitionState, IntentionAnalysis, IntentionOutput, IntentionState, LearningGoalDefinition, LearningGoalDefinition
from app.features.agent.type import AgentMode, AgentState

# Initialize the model
model = init_chat_model("gemini-2.5-flash-lite", model_provider="google_genai")

basic_prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are the assistant of an AI-powered casual learning platform called Learnora."
            "Answer all questions to the best of your ability"
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

MAX_FOLLOW_UPS = 1

def basic_call_model(state: IntentionState):
    prompt = basic_prompt_template.invoke(state)
    response = model.invoke(prompt)
    return {"messages": [response]}

def route_mode(state: IntentionState):
    if state['mode'] == AgentMode.LPP:
        return AgentMode.LPP
    else:
        return AgentMode.BASIC

def reset_mode(state: IntentionState) -> dict:
    """
    Reset mode to BASIC after subgraph completes.
    
    This allows the graph to return to general chat mode
    for the next user message.
    """
    print("🔄 Resetting mode to BASIC after learning path completion")
    return {"mode": None}

###############################
# Node 1: Initial Asker
###############################

def initial_asker(state: IntentionState) -> dict:
    """
    Node 1: Ask the opening question.
    
    This is a simple node that returns a fixed, predefined question.
    No LLM needed - saves cost and latency.
    
    Returns:
        dict: Updated state with the initial question as an AI message
    """
    # Fixed opening question - action-oriented
    opening_question = (
        "Hi! I'm here to help you learn something new. "
        "To get started, could you tell me: **What would you like to be able to do?**\n\n"
        "For example:\n"
        "- Build a web application\n"
        "- Analyze data from spreadsheets\n"
        "- Create automated scripts\n"
        "- Develop a mobile app"
    )
    
    # Return as AI message
    return {
        "messages": [AIMessage(content=opening_question)]
    }

###############################
# Node 2: Intention Evaluator
###############################

# Create structured output LLM
evaluator_llm = model.with_structured_output(IntentionAnalysis)

def intention_evaluator(state: IntentionState) -> dict:
    """
    Node 2: Evaluate if u   ser's intention is clear.
    
    Uses LLM with structured output to:
    1. Extract desired_outcome and context from conversation
    2. Determine if intention is clear and actionable
    3. Update state with extracted information
    
    Returns:
        dict: Updated state with desired_outcome, context, is_intention_clear
    """
    # Prepare context for the prompt
    context_dict = {
        "desired_outcome": state.get("desired_outcome") or "Not yet identified",
        "context": str(state.get("context") or "None provided"),
        "messages": state.get("messages", [])
    }
    
    # Invoke evaluator with structured output
    prompt = evaluator_prompt.invoke(context_dict)
    analysis: IntentionAnalysis = evaluator_llm.invoke(prompt)
    
    # Prepare updates
    updates = {}
    
    # Update desired_outcome (merge with existing if present)
    if analysis.desired_outcome:
        updates["desired_outcome"] = analysis.desired_outcome
    
    # Update context (merge with existing if present)
    if analysis.context:
        existing_context = state.get("context") or {}
        merged_context = {**existing_context, **analysis.context}
        updates["context"] = merged_context
    
    # Update clarity flag
    updates["is_intention_clear"] = analysis.is_clear
    
    # Log reasoning for debugging
    print(f"🔍 Evaluation: {analysis.reasoning}")
    print(f"   Clear: {analysis.is_clear}")
    print(f"   Outcome: {analysis.desired_outcome or 'Not identified'}")
    
    return updates

def route_after_evaluation(state: IntentionState) -> Literal["format_output", "ask_followup"]:
    """
    Decision function: Determine next step after evaluating intention.
    
    Routes to:
    - "format_output": If intention is clear OR max follow-ups reached
    - "ask_followup": If intention unclear AND follow-ups < MAX_FOLLOW_UPS
    
    Args:
        state: Current IntentionState
        
    Returns:
        str: Next node to visit
    """
    is_clear = state.get("is_intention_clear", False)
    follow_up_count = state.get("follow_up_count", 0)
    
    # If clear, proceed to output formatting
    if is_clear:
        print("✅ Intention is clear → Formatting output")
        return "format_output"
    
    # If reached max follow-ups, force proceed to output
    if follow_up_count >= MAX_FOLLOW_UPS:
        print("⚠️  Max follow-ups reached (MAX_FOLLOW_UPS/MAX_FOLLOW_UPS) → Forcing output")
        return "format_output"
    
    # Otherwise, ask follow-up question
    print(f"❓ Intention unclear → Asking follow-up ({follow_up_count + 1}/MAX_FOLLOW_UPS)")
    return "ask_followup"

###############################
# Node 3: Follow-up Question Generator
###############################

def followup_generator(state: IntentionState) -> dict:
    """
    Node 3: Generate a follow-up clarifying question.
    
    Called when intention is unclear and we haven't reached max follow-ups.
    Generates a contextual question based on what information is vague.
    
    Returns:
        dict: Updated state with follow-up question and incremented counter
    """
    # Prepare context for the prompt
    context_dict = {
        "desired_outcome": state.get("desired_outcome") or "Not yet identified",
        "context": str(state.get("context") or "None provided"),
        "follow_up_count": state.get("follow_up_count", 0) + 1,  # Increment for prompt
        "messages": state.get("messages", [])
    }
    
    # Generate follow-up question
    prompt = followup_prompt.invoke(context_dict)
    response = model.invoke(prompt)
    
    # Increment follow-up counter
    new_count = state.get("follow_up_count", 0) + 1
    
    print(f"❓ Follow-up {new_count}/MAX_FOLLOW_UPS: Asking clarifying question")
    
    return {
        "messages": [response],
        "follow_up_count": new_count
    }

###############################
# Node 4: Output Formatter
###############################

# Create formatter LLM with structured output
formatter_llm = model.with_structured_output(IntentionOutput)

def output_formatter(state: IntentionState) -> dict:
    """
    Node 4: Format the final intention output.
    
    Creates a clean summary with:
    - Topic: Concise subject area (2-4 words)
    - Desired outcome: What user wants to achieve
    - Context: Optional background/timeline/constraints
    - Summary: Brief 1-2 sentence overview
    
    Returns:
        dict: Updated state with topic and a completion message
    """
    # Prepare context for formatting
    context_dict = {
        "desired_outcome": state.get("desired_outcome") or "Not specified",
        "context": str(state.get("context") or "None provided"),
        "messages": state.get("messages", [])
    }
    
    # Generate formatted output
    prompt = formatter_prompt.invoke(context_dict)
    output: IntentionOutput = formatter_llm.invoke(prompt)
    
    # Create completion message
    completion_msg = (
        f"✅ **Got it!** Here's what I understand:\n\n"
        f"**Topic:** {output.topic}\n\n"
        f"**Your Goal:** {output.desired_outcome}\n\n"
    )
    
    if output.context:
        completion_msg += f"**Context:** {output.context}\n\n"
    
    completion_msg += (
        f"**Summary:** {output.summary}\n\n"
        f"Now let's create a personalized learning path for you!"
    )
    
    print(f"✅ Intention clarified!")
    print(f"   Topic: {output.topic}")
    print(f"   Outcome: {output.desired_outcome}")
    
    return {
        "topic": output.topic,
        "messages": [AIMessage(content=completion_msg)]
    }
    
###############################
# Node 5: Goal Definition
###############################    
    
# Create LLM with structured output
goal_definition_llm = model.with_structured_output(LearningGoalDefinition)

def define_learning_goal(state: GoalDefinitionState) -> dict:
    """
    Define formal learning goal from user's intention.
    
    Takes the intention (topic, desired_outcome, context) and generates:
    - Formal learning goal statement
    - 4-7 key competencies
    - 3-5 success criteria
    
    Returns:
        dict: Updated state with learning_goal, competencies, success_criteria
    """
    # Prepare context for the prompt
    context_dict = {
        "topic": state.get("topic") or "Not specified",
        "desired_outcome": state.get("desired_outcome") or "Not specified",
        "context": str(state.get("context") or "None provided")
    }
    
    # Format and invoke the LLM with structured output
    # Use the chain: prompt | llm
    chain = goal_definition_prompt | goal_definition_llm
    goal_def: LearningGoalDefinition = chain.invoke(context_dict)
    
    # Create user-facing message
    message_content = (
        f"🎯 **Learning Goal Defined!**\n\n"
        f"**Goal:**\n{goal_def.learning_goal}\n\n"
        f"**Key Competencies You'll Develop:**\n"
    )
    
    for i, comp in enumerate(goal_def.competencies, 1):
        message_content += f"{i}. {comp}\n"
    
    message_content += f"\n**Success Criteria:**\n"
    for i, criteria in enumerate(goal_def.success_criteria, 1):
        message_content += f"✓ {criteria}\n"
    
    message_content += "\nGreat! Now let's map out the concepts you'll need to learn..."
    
    print(f"🎯 Learning goal defined!")
    print(f"   Competencies: {len(goal_def.competencies)}")
    print(f"   Success criteria: {len(goal_def.success_criteria)}")
    
    return {
        "learning_goal": goal_def.learning_goal,
        "competencies": goal_def.competencies,
        "success_criteria": goal_def.success_criteria,
        "messages": [AIMessage(content=message_content)]
    }
    
###############################
# Node 6: Concept Graph Generation
################################
    
def generate_concept_graph(state: ConceptGraphState) -> dict:
    """
    Generate prerequisite graph of learning concepts.
    
    Takes competencies and breaks them down into:
    - 8-15 learnable concepts
    - Prerequisite relationships between concepts
    - Logical learning sequence
    
    Returns:
        dict: Updated state with concept_graph (JSON array)
    """
    # Format competencies as numbered list
    competencies = state.get("competencies") or []
    competencies_text = "\n".join([f"{i}. {comp}" for i, comp in enumerate(competencies, 1)])
    
    # Prepare context for the prompt
    context_dict = {
        "topic": state.get("topic") or "Not specified",
        "learning_goal": state.get("learning_goal") or "Not specified",
        "competencies_text": competencies_text
    }
    
    # Generate concept graph
    chain = concept_graph_prompt | model
    response = chain.invoke(context_dict)
    
    # Parse JSON from response
    try:
        # Clean the response - remove markdown code blocks if present
        content = response.content.strip()
        if content.startswith("```"):
            # Remove markdown code block formatting
            lines = content.split("\n")
            content = "\n".join([l for l in lines if not l.strip().startswith("```")])
        
        # Parse JSON
        concept_graph = json.loads(content)
        
        # Validate structure
        if not isinstance(concept_graph, list):
            raise ValueError("Concept graph must be a list")
        
        for item in concept_graph:
            if not isinstance(item, dict) or "concept" not in item or "prerequisites" not in item:
                raise ValueError("Each concept must have 'concept' and 'prerequisites' fields")
        
        print(f"📊 Concept graph generated!")
        print(f"   Total concepts: {len(concept_graph)}")
        print(f"   Foundational (no prereqs): {sum(1 for c in concept_graph if not c['prerequisites'])}")
        
        # Create user-facing message
        message_content = (
            f"📊 **Learning Path Concepts Mapped!**\n\n"
            f"I've broken down your learning journey into **{len(concept_graph)} key concepts**:\n\n"
        )
        
        # Group by prerequisite count for display
        foundational = [c for c in concept_graph if not c["prerequisites"]]
        intermediate = [c for c in concept_graph if len(c["prerequisites"]) in [1, 2]]
        advanced = [c for c in concept_graph if len(c["prerequisites"]) > 2]
        
        if foundational:
            message_content += "**🌱 Foundational Concepts:**\n"
            for c in foundational[:5]:  # Show first 5
                message_content += f"• {c['concept']}\n"
            if len(foundational) > 5:
                message_content += f"  ...and {len(foundational) - 5} more\n"
            message_content += "\n"
        
        if intermediate:
            message_content += f"**🔨 Intermediate Concepts:** {len(intermediate)} concepts\n\n"
        
        if advanced:
            message_content += f"**🚀 Advanced Concepts:** {len(advanced)} concepts\n\n"
        
        message_content += "The concepts are organized with clear prerequisites to guide your learning sequence!"
        
        return {
            "concept_graph": concept_graph,
            "messages": [AIMessage(content=message_content)]
        }
        
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON: {e}")
        print(f"Response content: {response.content[:200]}...")
        raise
    except Exception as e:
        print(f"❌ Error processing concept graph: {e}")
        raise


###############################
# Build the Learning Path Graph
###############################

# Build the complete learning path generation graph
learning_path_builder = StateGraph(ConceptGraphState)

learning_path_builder.add_node("basic_chat", basic_call_model)
learning_path_builder.add_node("reset_mode", reset_mode)

# Add all nodes from Steps 1-3
# Step 1: Intention Clarification
learning_path_builder.add_node("ask_initial", initial_asker)
learning_path_builder.add_node("evaluate_intention", intention_evaluator)
learning_path_builder.add_node("ask_followup", followup_generator)
learning_path_builder.add_node("format_intention", output_formatter)

# Step 2: Goal Definition
learning_path_builder.add_node("define_goal", define_learning_goal)

# Step 3: Concept Graph Construction
learning_path_builder.add_node("generate_concepts", generate_concept_graph)

# Define the complete flow
# Step 1 flow
learning_path_builder.add_conditional_edges(
    START,
    route_mode,
    {
        AgentMode.BASIC: "basic_chat",
        AgentMode.LPP: "ask_initial"
    }
)

# learning_path_builder.add_edge(START, "ask_initial")
learning_path_builder.add_edge("ask_initial", "evaluate_intention")

learning_path_builder.add_conditional_edges(
    "evaluate_intention",
    route_after_evaluation,
    {
        "format_output": "format_intention",
        "ask_followup": "ask_followup"
    }
)

learning_path_builder.add_edge("ask_followup", "evaluate_intention")

# Step 1 → Step 2
learning_path_builder.add_edge("format_intention", "define_goal")

# Step 2 → Step 3
learning_path_builder.add_edge("define_goal", "generate_concepts")

# Step 3 → END
# learning_path_builder.add_edge("generate_concepts", END)

# After basic chat, go to END
learning_path_builder.add_edge("basic_chat", END)

# After LPP graph, reset mode then END
learning_path_builder.add_edge("generate_concepts", "reset_mode")
learning_path_builder.add_edge("reset_mode", END)

# Compile the complete pipeline
learning_path_memory = MemorySaver()
learning_path_graph = learning_path_builder.compile(
    checkpointer=learning_path_memory,
    interrupt_before=["evaluate_intention"]  # Wait for user input in Step 1
)

# --- Exports ---
__all__ = ["learning_path_graph", "IntentionState"]