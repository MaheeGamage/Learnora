from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4
from langchain_core.messages import HumanMessage, AIMessage
from rdflib import Graph as RDFGraph, URIRef
from typing import Optional
from app.features.learning_path_planner import crud
from app.features.learning_path_planner.schemas import (
    LearningPathCreate, 
    LearningPathUpdate,
    GraphResponse
)
from app.features.learning_path_planner.kg import LearningPathKG
from app.features.concept.service import ConceptService
import logging
import asyncio
import json
import re

logger = logging.getLogger(__name__)


class LearningPathService:
    """Service layer for learning path operations with business logic."""
    
    def __init__(self):
        """Initialize learning path service with KG layer."""
        self.kg = LearningPathKG()
        self.concept_service = ConceptService()
        self._graph = None  # Lazy load the LangGraph
    
    @property
    def graph(self):
        """Lazy load the LangGraph to avoid initialization during testing."""
        if self._graph is None:
            from app.features.learning_path_planner.graph import graph
            self._graph = graph
        return self._graph
    
    # ===== Knowledge Graph Operations =====
    
    def create_learning_path_kg(
        self,
        thread_id: str,
        topic: str,
        concept_ids: list[str]
    ) -> URIRef:
        """
        Create a new learning path in the Knowledge Graph.
        
        Business logic: Validates path doesn't exist, validates concepts exist.
        
        Args:
            thread_id: Unique thread identifier
            topic: The learning topic/goal
            concept_ids: List of concept IDs to include in the path
            
        Returns:
            URIRef of the created learning path
        """
        # Business validation: check if path already exists
        if self.kg.path_exists(thread_id):
            logger.warning(f"Learning path {thread_id} already exists")
            # Could raise an exception or return existing path depending on requirements
        
        # Delegate to KG layer
        path = self.kg.create_path(thread_id, topic, concept_ids)
        logger.info(f"Created learning path: {thread_id} with {len(concept_ids)} concepts")
        return path
    
    def get_learning_path_kg(self, thread_id: str) -> Optional[RDFGraph]:
        """
        Get a learning path graph from KG.
        
        Args:
            thread_id: The thread identifier
            
        Returns:
            RDFGraph containing the learning path, or empty graph if not found
        """
        return self.kg.get_path(thread_id)
    
    def get_learning_path_concepts(self, thread_id: str) -> list[URIRef]:
        """
        Get all concepts in a learning path from KG.
        
        Args:
            thread_id: The thread identifier
            
        Returns:
            List of concept URIRefs in the learning path
        """
        return self.kg.get_path_concepts(thread_id)
    
    async def get_learning_path_kg_info(self, db: AsyncSession, thread_id: str) -> Optional[dict]:
        """
        Get knowledge graph information for a learning path in API-friendly format.
        
        Args:
            db: Database session
            thread_id: The thread identifier
            
        Returns:
            Dictionary with learning path KG info or None if not found
        """
        # Get from database
        db_path = await crud.get_learning_path(db, thread_id)
        if not db_path:
            return None
        
        # Check if KG data exists
        if not self.kg.path_exists(thread_id):
            return {
                "thread_id": thread_id,
                "topic": db_path.topic,
                "concepts": [],
                "concept_count": 0
            }
        
        # Get concepts from KG
        concept_uris = await asyncio.to_thread(self.get_learning_path_concepts, thread_id)
        
        # Format concept information
        concepts_info = []
        for concept_uri in concept_uris:
            concept_id = str(concept_uri).split("#")[-1]
            
            # Get prerequisites
            prereq_uris = await asyncio.to_thread(
                self.concept_service.get_concept_prerequisites,
                concept_id
            )
            prereq_ids = [str(p).split("#")[-1] for p in prereq_uris]
            
            concepts_info.append({
                "id": concept_id,
                "label": concept_id.replace("_", " ").title(),
                "prerequisites": prereq_ids
            })
        
        return {
            "thread_id": thread_id,
            "topic": db_path.topic,
            "concepts": concepts_info,
            "concept_count": len(concepts_info)
        }
    
    def _extract_json_from_message(self, content: str) -> Optional[dict]:
        """
        Extract JSON-LD from AI message content.
        
        The AI sometimes wraps JSON in markdown code blocks or adds extra text.
        This method tries to extract valid JSON.
        
        Args:
            content: The message content
            
        Returns:
            Parsed JSON dict or None if parsing fails
        """
        # Try to find JSON in markdown code blocks
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find raw JSON
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                return None
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            return None
    
    def _parse_and_store_jsonld(self, thread_id: str, topic: str, jsonld_data: dict) -> None:
        """
        Parse JSON-LD knowledge graph and store concepts in KG.
        
        Args:
            thread_id: The thread identifier
            topic: The learning topic
            jsonld_data: The JSON-LD data from the AI
        """
        try:
            graph_data = jsonld_data.get("@graph", [])
            if not graph_data:
                logger.warning(f"No @graph found in JSON-LD for thread {thread_id}")
                return
            
            concept_ids = []
            
            # First pass: Create all concepts
            for concept_data in graph_data:
                concept_id = concept_data.get("@id", "").split(":")[-1]  # Remove namespace prefix
                concept_name = concept_data.get("name", concept_id)
                
                if not concept_id:
                    continue
                
                # Add concept (service handles duplicates)
                self.concept_service.add_concept(
                    concept_id=concept_id,
                    label=concept_name,
                    description=f"Concept for learning path: {topic}"
                )
                concept_ids.append(concept_id)
            
            # Second pass: Add prerequisites
            for concept_data in graph_data:
                concept_id = concept_data.get("@id", "").split(":")[-1]
                requires = concept_data.get("requires", [])
                
                if not concept_id or not requires:
                    continue
                
                # Extract prerequisite IDs
                prereq_ids = []
                if isinstance(requires, list):
                    for req in requires:
                        if isinstance(req, dict):
                            prereq_id = req.get("@id", "").split(":")[-1]
                        else:
                            prereq_id = str(req).split(":")[-1]
                        if prereq_id:
                            prereq_ids.append(prereq_id)
                
                # Re-add concept with prerequisites (KG layer handles this)
                if prereq_ids:
                    self.concept_service.add_concept(
                        concept_id=concept_id,
                        label=concept_data.get("name", concept_id),
                        prerequisites=prereq_ids
                    )
            
            # Create learning path in KG
            if concept_ids:
                self.create_learning_path_kg(thread_id, topic, concept_ids)
                logger.info(f"Stored {len(concept_ids)} concepts in KG for thread {thread_id}")
            
        except Exception as e:
            logger.error(f"Error parsing and storing JSON-LD: {e}", exc_info=True)
    
    # ===== LangGraph Operations =====
    
    async def start_learning_path(self, db: AsyncSession, topic: str) -> GraphResponse:
        """Start a new learning path"""
        # Generate unique thread ID
        thread_id = str(uuid4())
        config = {"configurable": {"thread_id": thread_id}}
        initial_state = {"topic": topic}
        
        # Save to database (async)
        learning_path_create = LearningPathCreate(
            thread_id=thread_id,
            topic=topic
        )
        await crud.create_learning_path(db, learning_path_create)
        
        # Run graph (sync code - run in thread pool to avoid blocking)
        result = await asyncio.to_thread(self.graph.invoke, initial_state, config)
        message_threads = result.get("messages", {})
        
        logger.info(f"Started learning path with thread_id: {thread_id}")
        
        return GraphResponse(
            thread_id=thread_id,
            messages=message_threads
        )
    
    async def resume_learning_path(self, db: AsyncSession, thread_id: str, human_answer: str) -> GraphResponse:
        """Resume an existing learning path"""
        # Check if learning path exists (async)
        db_learning_path = await crud.get_learning_path(db, thread_id)
        if not db_learning_path:
            raise ValueError(f"Learning path with thread_id {thread_id} not found")
        
        config = {"configurable": {"thread_id": thread_id}}
        state = {"messages": [HumanMessage(content=human_answer)]}
        
        # Update graph state (sync code - run in thread pool)
        await asyncio.to_thread(self.graph.update_state, config, state)
        
        # Run graph (sync code - run in thread pool)
        result = await asyncio.to_thread(self.graph.invoke, None, config)
        message_threads = result.get("messages", {})
        
        # Update database with new state (async)
        update_data = LearningPathUpdate(graph_state=result)
        await crud.update_learning_path(db, thread_id, update_data)
        
        # Check if this was the final step (learning path generation)
        # The last message should contain the JSON-LD knowledge graph
        if message_threads and len(message_threads) > 0:
            last_message = message_threads[-1]
            if isinstance(last_message, AIMessage):
                # Try to extract and store JSON-LD
                jsonld_data = self._extract_json_from_message(last_message.content)
                if jsonld_data and "@graph" in jsonld_data:
                    topic = db_learning_path.topic
                    await asyncio.to_thread(
                        self._parse_and_store_jsonld,
                        thread_id,
                        topic,
                        jsonld_data
                    )
                    logger.info(f"Extracted and stored knowledge graph for thread {thread_id}")
        
        logger.info(f"Resumed learning path with thread_id: {thread_id}")
        
        return GraphResponse(
            thread_id=thread_id,
            messages=message_threads
        )