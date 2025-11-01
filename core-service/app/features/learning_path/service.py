import re
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4
from langchain_core.messages import HumanMessage, AIMessage
from rdflib import RDF, Graph as RDFGraph, URIRef
from typing import List, Dict, Any, Tuple
from app.features.learning_path import crud
from app.features.learning_path.schemas import (
    LearningPathCreate, 
    LearningPathUpdate,
    GraphResponse
)
# from app.features.learning_path.kg import LearningPathKG
from app.features.concept.service import ConceptService
from app.features.learning_path.utils import (
    extract_json_array_from_message,
    extract_json_from_message,
    parse_and_store_concepts
)
import logging
import asyncio
from rdflib import Literal
from app.features import learning_path
from app.kg.storage import KGStorage
from app.util.string_util import normalize_string
from app.kg.base import KGBase

logger = logging.getLogger(__name__)


class LearningPathService:
    """Service layer for learning path operations with business logic."""
    
    def __init__(self):
        """Initialize learning path service with KG layer."""
        # self.kg = LearningPathKG()
        self.concept_service = ConceptService()
        self._graph = None  # Lazy load the LangGraph
        self.kg_base = KGBase()
        self.storage = KGStorage()
    
    @property
    def graph(self):
        """Lazy load the LangGraph to avoid initialization during testing."""
        if self._graph is None:
            from app.features.learning_path.graph import graph
            self._graph = graph
        return self._graph
    
    # ===== Knowledge Graph Operations =====
    
    # def create_learning_path_kg(
    #     self,
    #     user_id: str,
    #     thread_id: str,
    #     topic: str,
    #     concept_ids: list[str]
    # ) -> URIRef:
    #     """
    #     Create a new learning path in the Knowledge Graph.
        
    #     Business logic: Validates path doesn't exist, validates concepts exist.
        
    #     Args:
    #         user_id: User identifier who owns this learning path
    #         thread_id: Unique thread identifier
    #         topic: The learning topic/goal
    #         concept_ids: List of concept IDs to include in the path
            
    #     Returns:
    #         URIRef of the created learning path
    #     """
    #     # Business validation: check if path already exists
    #     if self.kg.path_exists(user_id, thread_id):
    #         logger.warning(f"Learning path {thread_id} already exists for user {user_id}")
    #         # Could raise an exception or return existing path depending on requirements
        
    #     # Delegate to KG layer
    #     path = self.kg.create_path(user_id, thread_id, topic, concept_ids)
    #     logger.info(f"Created learning path: {thread_id} for user {user_id} with {len(concept_ids)} concepts")
    #     return path
    
    # def get_learning_path_kg(self, user_id: str, thread_id: str) -> Optional[RDFGraph]:
    #     """
    #     Get a learning path graph from KG.
        
    #     Args:
    #         user_id: User identifier who owns the path
    #         thread_id: The thread identifier
            
    #     Returns:
    #         RDFGraph containing the learning path, or empty graph if not found
    #     """
    #     return self.kg.get_path(user_id, thread_id)
    
    # def get_learning_path_concepts(self, user_id: str, thread_id: str) -> list[URIRef]:
    #     """
    #     Get all concepts in a learning path from KG.
        
    #     Args:
    #         user_id: User identifier who owns the path
    #         thread_id: The thread identifier
            
    #     Returns:
    #         List of concept URIRefs in the learning path
    #     """
    #     return self.kg.get_path_concepts(user_id, thread_id)
    
    # async def get_learning_path_kg_info(self, db: AsyncSession, thread_id: str) -> Optional[dict]:
    #     """
    #     Get knowledge graph information for a learning path in API-friendly format.
        
    #     Args:
    #         db: Database session
    #         thread_id: The conversation thread identifier
            
    #     Returns:
    #         Dictionary with learning path KG info or None if not found
    #     """
    #     # Get from database
    #     db_path = await crud.get_learning_path_by_thread_id(db, thread_id)
    #     if not db_path:
    #         return None
        
    #     # Get user_id from database record
    #     user_id = str(db_path.user_id)
        
    #     # Check if KG data exists
    #     if not self.kg.path_exists(user_id, thread_id):
    #         return {
    #             "thread_id": thread_id,
    #             "topic": db_path.topic,
    #             "concepts": [],
    #             "concept_count": 0
    #         }
        
    #     # Get concepts from KG
    #     concept_uris = await asyncio.to_thread(self.get_learning_path_concepts, user_id, thread_id)
        
    #     # Format concept information
    #     concepts_info = []
    #     for concept_uri in concept_uris:
    #         concept_id = str(concept_uri).split("#")[-1]
            
    #         # Get prerequisites
    #         prereq_uris = await asyncio.to_thread(
    #             self.concept_service.get_concept_prerequisites,
    #             concept_id
    #         )
    #         prereq_ids = [str(p).split("#")[-1] for p in prereq_uris]
            
    #         concepts_info.append({
    #             "id": concept_id,
    #             "label": concept_id.replace("_", " ").title(),
    #             "prerequisites": prereq_ids
    #         })
        
    #     return {
    #         "thread_id": thread_id,
    #         "topic": db_path.topic,
    #         "concepts": concepts_info,
    #         "concept_count": len(concepts_info)
    #     }
    
    # ===== LangGraph Operations =====
    
    async def start_learning_path(self, topic: str) -> GraphResponse:
        """Start a new learning path"""
        # Generate unique thread ID for the conversation
        conversation_thread_id = str(uuid4())
        config = {"configurable": {"thread_id": conversation_thread_id}}
        initial_state = {"topic": topic}
        
        # Run graph (sync code - run in thread pool to avoid blocking)
        result = await asyncio.to_thread(self.graph.invoke, initial_state, config)
        message_threads = result.get("messages", {})
        
        logger.info(f"Started learning path with conversation_thread_id: {conversation_thread_id}")
        
        return GraphResponse(
            thread_id=conversation_thread_id,
            messages=message_threads
        )
    
    async def resume_learning_path(self, db: AsyncSession, thread_id: str, human_answer: str, user_id: str = "default_user") -> GraphResponse:
        """Resume an existing learning path
        
        Args:
            db: Database session
            thread_id: The conversation thread identifier
            human_answer: Human's answer to the previous question
            user_id: User identifier (default: "default_user" until DB migration adds user_id field)
        
        Returns:
            GraphResponse with updated conversation
        """
        
        config = {"configurable": {"thread_id": thread_id}}
        state = {"messages": [HumanMessage(content=human_answer)]}
        
        # Update graph state (sync code - run in thread pool)
        await asyncio.to_thread(self.graph.update_state, config, state)
        
        # Run graph (sync code - run in thread pool)
        result = await asyncio.to_thread(self.graph.invoke, None, config)
        message_threads = result.get("messages", {})
        
        # Check if this was the final step (learning path generation)
        # The last message should contain the JSON array of concepts
        if message_threads and len(message_threads) > 0:
            last_message = message_threads[-1]
            if isinstance(last_message, AIMessage):
                # Extract the JSON output and save to variable
                learning_path_json = extract_json_array_from_message(last_message.content)

                if learning_path_json:
                    # Store the extracted concepts in KG using the conversation thread ID
                    topic = "sample topic"  # TODO: Retrieve actual topic from conversation state

                    graph, learning_path_uri = self.convert_learning_path_json_to_rdf_graph(learning_path_json, topic)
                    self.storage.save_user_graph(user_id, graph)
                    
                    logger.info(f"Extracted and stored {len(learning_path_json)} concepts for thread {thread_id}, user {user_id}")
                else:
                    raise HTTPException(
                            status_code=500, 
                            detail="Learning path generation failed. Could not extract valid JSON from AI response."
                        )
        
        logger.info(f"Resumed learning path with conversation_thread_id: {thread_id}")
        
        return GraphResponse(
            thread_id=thread_id,
            messages=message_threads
        )
        
    def convert_learning_path_json_to_rdf_graph(self, json_data: List[Dict[str, Any]], topic: str) -> Tuple[RDFGraph, URIRef]:
        """
        Convert JSON-based learning graph to RDF graph and save it.
        
        Args:
            json_data: List of dicts with 'concept' and 'prerequisites' keys
            user_id: User identifier for saving the graph
        
        Example:
            json_data = [
                {"concept": "ConceptName1", "prerequisites": []},
                {"concept": "ConceptName2", "prerequisites": ["ConceptName1"]},
                {"concept": "ConceptName3", "prerequisites": ["ConceptName1", "ConceptName2"]}
            ]
        """
        # Create a new graph
        graph = self.kg_base.create_graph()
        learning_path_uri = self.kg_base.ONT[normalize_string(topic)]

        graph.add((learning_path_uri, self.kg_base.RDF.type, self.kg_base.ONT.LearningPath))
        graph.add((learning_path_uri, self.kg_base.ONT.topic, Literal(topic)))

        # Process each concept in the JSON data
        for item in json_data:
            concept_name = item["concept"]
            prerequisites = item.get("prerequisites", [])
            
            # Create concept URI with normalized name (remove spaces and special chars)
            normalized_name = normalize_string(concept_name)
            concept_uri = self.kg_base.ONT[normalized_name]
            
            # Add concept as instance of Concept class
            graph.add((concept_uri, RDF.type, self.kg_base.ONT.Concept))
            
            # Add label for the concept (keep original name for display)
            graph.add((concept_uri, self.kg_base.ONT.label, Literal(concept_name)))
            
            # Add concept to learning path
            graph.add((learning_path_uri, self.kg_base.ONT.includesConcept, concept_uri))
            
            # Add prerequisites
            for prereq_name in prerequisites:
                normalized_prereq = normalize_string(prereq_name)
                prereq_uri = self.kg_base.ONT[normalized_prereq]
                graph.add((concept_uri, self.kg_base.ONT.hasPrerequisite, prereq_uri))
        
        return graph, learning_path_uri

