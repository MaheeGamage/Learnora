import re
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4
from langchain_core.messages import HumanMessage, AIMessage
from rdflib import RDF, Graph as RDFGraph, URIRef
from typing import List, Dict, Any, Tuple, Optional
from app.features.learning_path import crud
from app.features.learning_path.schemas import (
    LearningPathCreate, 
    LearningPathUpdate,
    GraphResponse
)
from app.features.learning_path.models import LearningPath
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
from app.features.users.models import User

logger = logging.getLogger(__name__)


class LearningPathService:
    """Service layer for learning path operations with business logic."""
    
    def __init__(self):
        """Initialize learning path service with KG layer."""
        self.concept_service = ConceptService()
        self._graph = None  # Lazy load the LangGraph
        self.kg_base = KGBase()
        self.storage = KGStorage()
    
    @property
    def graph(self):
        """Lazy load the LangGraph to avoid initialization during testing."""
        if self._graph is None:
            from features.agent.graph import graph
            self._graph = graph
        return self._graph
    
    # ===== CRUD Operations =====
    
    async def create_learning_path(
        self, 
        db: AsyncSession, 
        learning_path: LearningPathCreate, 
        current_user: User
    ) -> LearningPath:
        """Create a new learning path with authorization check."""
        # Ensure user_id matches current user
        if learning_path.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to create learning path for another user")
        
        return await crud.create_learning_path(db, learning_path)
    
    async def get_learning_path(
        self, 
        db: AsyncSession, 
        learning_path_id: int, 
        current_user: User
    ) -> Optional[LearningPath]:
        """Get a learning path by ID with authorization check."""
        learning_path = await crud.get_learning_path_by_id(db, learning_path_id)
        
        if learning_path and learning_path.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to access this learning path")
        
        return learning_path
    
    async def get_all_learning_paths(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[LearningPath]:
        """Get all learning paths with pagination."""
        return await crud.get_all_learning_paths(db, skip, limit)
    
    async def update_learning_path(
        self, 
        db: AsyncSession, 
        learning_path_id: int, 
        update_data: LearningPathUpdate, 
        current_user: User
    ) -> Optional[LearningPath]:
        """Update a learning path with authorization check."""
        learning_path = await crud.get_learning_path_by_id(db, learning_path_id)
        
        if not learning_path:
            return None
        
        if learning_path.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to update this learning path")
        
        return await crud.update_learning_path(db, learning_path_id, update_data)
    
    async def delete_learning_path(
        self, 
        db: AsyncSession, 
        learning_path_id: int, 
        current_user: User
    ) -> bool:
        """Delete a learning path with authorization check."""
        learning_path = await crud.get_learning_path_by_id(db, learning_path_id)
        
        if not learning_path:
            return False
        
        if learning_path.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this learning path")
        
        return await crud.delete_learning_path(db, learning_path_id)
    
    # ===== Knowledge Graph Operations =====
    
    
  
    # ===== Helper Methods =====
          
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

    def parse_and_save_learning_path(self, db: AsyncSession, json_data: List[Dict[str, Any]], topic: str, user: User):
        parsed_graph, learning_path_uri = self.convert_learning_path_json_to_rdf_graph(json_data, topic)
        
        # Create user triplets if not already existing
        user_uri = self.kg_base.ONT[normalize_string(f"user_{user.id}")]
        # Check if user exists by querying for any triple with user_uri as subject and type User
        if (user_uri, self.kg_base.RDF.type, self.kg_base.ONT.User) not in parsed_graph:
            parsed_graph.add((user_uri, self.kg_base.RDF.type, self.kg_base.ONT.User))
            parsed_graph.add((user_uri, self.kg_base.ONT.followsPath, learning_path_uri))

        self.storage.save_user_graph(str(user.id), parsed_graph)
        
        # Create DB record
        db_learning_path = crud.create_learning_path(
            db,
            LearningPathCreate(
                user_id=user.id,
                topic=topic,
                graph_uri=str(learning_path_uri)
            )
        )
        
        return db_learning_path
        