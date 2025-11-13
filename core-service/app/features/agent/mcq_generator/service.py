"""MCQ Generation Agent Service using LangChain."""

from typing import Optional, List, Dict
from xml.etree.ElementInclude import include
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.agent.mcq_generator.schemas import (
    MCQGenerationResponse,
    MCQGenerationRequest,
    DifficultyLevel,
)
from app.features.agent.mcq_generator.utils import build_learning_path_context
from app.features.learning_path.service import LearningPathService
from app.features.users.models import User


class MCQGeneratorAgent:
    """
    Agent for generating multiple-choice questions using LangChain.
    
    Uses create_agent with structured output to ensure reliable MCQ generation.
    """
    
    def __init__(
        self, 
        model_name: str = "gemini-2.5-flash-lite",
        model_provider: str = "google_genai",
        temperature: float = 0.7
    ):
        """
        Initialize the MCQ generator agent.
        
        Args:
            model_name: Model to use (default: gemini-2.5-flash-lite)
            model_provider: Model provider (default: google_genai)
            temperature: Temperature for generation (0.0-1.0, default: 0.7)
        """
        # Initialize the LLM using init_chat_model (same as learning_path_graph)
        self.llm = init_chat_model(
            model_name,
            model_provider=model_provider,
            temperature=temperature
        )
        
        # System prompt for the MCQ generation agent
        self.system_prompt = """You are an expert educational AI tutor specializing in creating high-quality multiple-choice questions for learning assessment.

Your role is to generate MCQ questions that:
1. Test CONCEPTUAL UNDERSTANDING, not rote memorization
2. Are clear, unambiguous, and appropriate for the specified difficulty level
3. Have exactly 4 options (A, B, C, D) with only ONE correct answer
4. Include explanations that help learners understand WHY the answer is correct
5. Consider the learner's background and prerequisite knowledge
6. Are challenging but fair for the given difficulty level

Guidelines for difficulty levels:
- Beginner: Test basic definitions, simple concepts, and foundational understanding
- Intermediate: Test application of concepts, relationships, and practical scenarios
- Advanced: Test deep understanding, edge cases, integration of multiple concepts, and critical thinking

Always consider the learning path context to ensure questions build appropriately on prerequisite knowledge."""
        
        # Create the agent with structured output
        # Use the pre-initialized LLM to avoid auto-detection issues:
        # In some LangChain versions, passing model parameters directly to create_agent
        # can trigger auto-detection logic that may select an incorrect model type or
        # configuration, especially when multiple providers or custom models are available.
        # By explicitly initializing the LLM with init_chat_model and passing the model object,
        # we ensure consistent behavior and avoid subtle bugs related to model selection.
        self.agent = create_agent(
            model=self.llm,  # Pass the already initialized model object
            tools=[],  # No tools needed for MCQ generation
            response_format=ToolStrategy(
                schema=MCQGenerationResponse,
                tool_message_content="MCQ questions generated successfully!",
                handle_errors=True  # Auto-retry on validation errors
            ),
            system_prompt=self.system_prompt
        )
    
    def _build_user_prompt(
        self,
        concept_name: str,
        concept_description: str,
        learning_path_context: str,
        difficulty_level: str,
        question_count: int
    ) -> str:
        """
        Build the user prompt for MCQ generation.
        
        Args:
            concept_name: Name of the concept
            concept_description: Description of the concept
            learning_path_context: Context from the learning path
            difficulty_level: Difficulty level
            question_count: Number of questions to generate
            
        Returns:
            Formatted user prompt
        """
        prompt = f"""Generate {question_count} multiple-choice questions about the following concept:

**Concept**: {concept_name}

**Context**: {concept_description}

**Prerequisites & Learning Path**:
{learning_path_context}

**Difficulty Level**: {difficulty_level}

Requirements:
- Generate EXACTLY {question_count} questions
- Each question must have EXACTLY 4 options (A, B, C, D)
- Mark the correct answer clearly (A, B, C, or D)
- Provide a clear explanation for each answer
- Questions should test understanding appropriate for {difficulty_level} level learners
- Consider the prerequisite knowledge from the learning path when crafting questions

Focus on creating questions that help learners verify they truly understand the concept, not just memorized facts."""
        
        return prompt
    
    async def generate_mcqs(
        self,
        db: AsyncSession,
        current_user: User,
        concept_name: str,
        difficulty_level: DifficultyLevel,
        question_count: int,
        concept_description: Optional[str] = None,
        learning_path_db_id: Optional[int] = None,
        learning_path: Optional[List[Dict]] = None,
        concept_id: Optional[str] = None
    ) -> MCQGenerationResponse:
        """
        Generate MCQ questions for a given concept.
        
        Args:
            concept_name: The concept for which to generate questions
            difficulty_level: Difficulty level (Beginner/Intermediate/Advanced)
            question_count: Number of questions to generate (1-20)
            concept_description: Optional description of the concept
            learning_path: Optional learning path in JSON-LD format
            concept_id: Optional concept ID for prerequisite extraction
            
        Returns:
            MCQGenerationResponse with generated questions
            
        Raises:
            Exception: If agent fails to generate valid MCQs
        """
        
        # Build learning path context
        lp_context = ""
        if(learning_path_db_id):
            lp_service = LearningPathService()
            learning_path = await lp_service.get_learning_path(
                db = db, 
                learning_path_id=learning_path_db_id,
                current_user=current_user,
                include_kg=True
            )
            lp_context = build_learning_path_context(learning_path.kg_data, concept_id)
        

        # Use default description if not provided
        description = concept_description or "No additional context provided."
        
        # Build the user prompt
        user_prompt = self._build_user_prompt(
            concept_name=concept_name,
            concept_description=description,
            learning_path_context=lp_context,
            difficulty_level=difficulty_level.value,
            question_count=question_count
        )
        
        # Invoke the agent
        result = await self.agent.ainvoke({
            "messages": [{"role": "user", "content": user_prompt}]
        })
        
        # Extract structured response
        structured_response = result.get("structured_response")
        
        if not structured_response:
            raise Exception("Agent failed to generate structured MCQ response")
        
        # Validate question count
        if len(structured_response.questions) != question_count:
            # This shouldn't happen with proper prompting, but let's handle it
            print(f"Warning: Expected {question_count} questions, got {len(structured_response.questions)}")
        
        return structured_response
    
    # TODO: Delete on 21 Nov 2025 if this no used till this date
    # def generate_mcqs_sync(
    #     self,
    #     concept_name: str,
    #     difficulty_level: DifficultyLevel,
    #     question_count: int,
    #     concept_description: Optional[str] = None,
    #     learning_path: Optional[List[Dict]] = None,
    #     concept_id: Optional[str] = None
    # ) -> MCQGenerationResponse:
    #     """
    #     Synchronous version of generate_mcqs.
        
    #     Args:
    #         Same as generate_mcqs
            
    #     Returns:
    #         MCQGenerationResponse with generated questions
    #     """
    #     # Build learning path context
    #     lp_context = build_learning_path_context(learning_path, concept_id)
        
    #     # Use default description if not provided
    #     description = concept_description or "No additional context provided."
        
    #     # Build the user prompt
    #     user_prompt = self._build_user_prompt(
    #         concept_name=concept_name,
    #         concept_description=description,
    #         learning_path_context=lp_context,
    #         difficulty_level=difficulty_level.value,
    #         question_count=question_count
    #     )
        
    #     # Invoke the agent synchronously
    #     result = self.agent.invoke({
    #         "messages": [{"role": "user", "content": user_prompt}]
    #     })
        
    #     # Extract structured response
    #     structured_response = result.get("structured_response")
        
    #     if not structured_response:
    #         raise Exception("Agent failed to generate structured MCQ response")
        
    #     return structured_response


# Singleton instance
_mcq_agent: Optional[MCQGeneratorAgent] = None


def get_mcq_agent() -> MCQGeneratorAgent:
    """
    Get or create the singleton MCQ generator agent.
    
    Returns:
        MCQGeneratorAgent instance
    """
    global _mcq_agent
    if _mcq_agent is None:
        _mcq_agent = MCQGeneratorAgent()
    return _mcq_agent
