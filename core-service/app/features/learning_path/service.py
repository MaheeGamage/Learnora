import re
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4
from langchain_core.messages import HumanMessage, AIMessage
from rdflib import RDF, Graph as RDFGraph, Namespace, URIRef
from typing import List, Dict, Any, Tuple, Optional
from app.features.learning_path import crud
from app.features.learning_path.schemas import (
    LearningPathCreate,
    LearningPathUpdate,
)
from app.features.learning_path.models import LearningPath
from app.features.concept.service import ConceptService
import logging
from rdflib import Literal
import json
from app.kg.storage import KGStorage
from app.util.string_util import normalize_string
from app.kg.base import KGBase
from app.features.users.models import User
from app.util.kg_util import extract_subgraph, get_learning_path_kg_local_name

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
            raise HTTPException(
                status_code=403, detail="Not authorized to create learning path for another user")

        return await crud.create_learning_path(db, learning_path)

    async def get_learning_path(
        self,
        db: AsyncSession,
        learning_path_id: int,
        current_user: User,
        include_kg: bool = False
    ) -> Optional[LearningPath]:
        """Get a learning path by ID with authorization check."""
        learning_path = await crud.get_learning_path_by_id(db, learning_path_id)

        if learning_path and learning_path.user_id != current_user.id:
            raise HTTPException(
                status_code=403, detail="Not authorized to access this learning path")

        if learning_path and include_kg and learning_path.graph_uri:
            try:
                user_graph = self.storage.load_user_graph(str(current_user.id))
                # Serialize graph to JSON-LD format
                lp_uri = URIRef(learning_path.graph_uri)
                kg_jsonld = self.extract_learning_path_graph(user_graph, lp_uri) #learning_path.graph_uri
                # kg_jsonld = self._graph_to_jsonld(user_graph)
                # Attach KG data to the response object
                learning_path.kg_data = kg_jsonld
            except Exception as e:
                logger.error(f"Error retrieving KG data: {str(e)}")
                # Don't fail the request if KG data retrieval fails
                learning_path.kg_data = None

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
            raise HTTPException(
                status_code=403, detail="Not authorized to update this learning path")

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
            raise HTTPException(
                status_code=403, detail="Not authorized to delete this learning path")

        return await crud.delete_learning_path(db, learning_path_id)

    # ===== Knowledge Graph Operations =====

    def extract_learning_path_graph(self, user_graph: RDFGraph, learning_path_uri: URIRef) -> Any:
        """Extract a subgraph for the learning path and return parsed JSON-LD as Python objects.

        Returns a Python structure (usually a list/dict) suitable for returning from FastAPI without
        requiring the client to re-parse a serialized JSON string.
        """
        try:
            subgraph = extract_subgraph(user_graph, learning_path_uri, max_depth=2)
            jsonld_str = subgraph.serialize(format="json-ld", indent=4)
            # Parse the JSON-LD string into Python objects so the API returns JSON types
            parsed = json.loads(jsonld_str)
            return parsed
        except Exception as e:
            logger.error("JSON-LD serialization or parsing failed: %s", str(e))
            raise

    # ===== Helper Methods =====

    def convert_learning_path_json_to_rdf_graph(self, json_data: List[Dict[str, Any]], topic: str, goal: str, db_learning_path: LearningPath) -> Tuple[RDFGraph, URIRef]:
        """
        Convert JSON-based learning graph to RDF graph and save it.

        Args:
            json_data: List of dicts with 'concept' and 'prerequisites' keys
            topic: Topic of the learning path
            goal: Goal of the learning path
            db_learning_path: Database learning path object

        Example:
            json_data = [
                {"concept": "ConceptName1", "prerequisites": []},
                {"concept": "ConceptName2", "prerequisites": ["ConceptName1"]},
                {"concept": "ConceptName3", "prerequisites": ["ConceptName1", "ConceptName2"]}
            ]
        """
        # Create a new graph
        graph = self.kg_base.create_graph()
        learning_path_uri = self.kg_base.ONT[get_learning_path_kg_local_name(
            db_learning_path.id)]

        graph.add((learning_path_uri, self.kg_base.RDF.type,
                  self.kg_base.ONT.LearningPath))
        graph.add((learning_path_uri, self.kg_base.ONT.topic, Literal(topic)))
        
        # Create and link Goal
        goal_uri = self.kg_base.ONT[normalize_string(f"goal_{db_learning_path.id}")]
        graph.add((goal_uri, self.kg_base.RDF.type, self.kg_base.ONT.Goal))
        graph.add((goal_uri, self.kg_base.ONT.label, Literal(goal)))
        graph.add((learning_path_uri, self.kg_base.ONT.hasGoal, goal_uri))

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
            graph.add((concept_uri, self.kg_base.ONT.label,
                      Literal(concept_name)))

            # Add concept to learning path
            graph.add(
                (learning_path_uri, self.kg_base.ONT.includesConcept, concept_uri))

            # Add prerequisites
            for prereq_name in prerequisites:
                normalized_prereq = normalize_string(prereq_name)
                prereq_uri = self.kg_base.ONT[normalized_prereq]
                graph.add(
                    (concept_uri, self.kg_base.ONT.hasPrerequisite, prereq_uri))

        return graph, learning_path_uri

    async def parse_and_save_learning_path(self, db: AsyncSession, json_data: List[Dict[str, Any]], topic: str, goal: str, user: User) -> LearningPath:

        learning_path_create_obj = LearningPathCreate(
            user_id=user.id,
            topic=topic
        )

        # Create DB record
        db_learning_path = await crud.create_learning_path(
            db,
            learning_path_create_obj
        )

        parsed_graph, learning_path_uri = self.convert_learning_path_json_to_rdf_graph(
            json_data, topic, goal, db_learning_path=db_learning_path)

        # update learning path with graph URI
        updated_db_learning_path = await crud.update_learning_path(
            db,
            db_learning_path.id,
            LearningPathUpdate(graph_uri=str(learning_path_uri))
        )

        # Create user triplets if not already existing
        user_uri = self.kg_base.ONT[normalize_string(f"user_{user.id}")]
        # Check if user exists by querying for any triple with user_uri as subject and type User
        if (user_uri, self.kg_base.RDF.type, self.kg_base.ONT.User) not in parsed_graph:
            parsed_graph.add(
                (user_uri, self.kg_base.RDF.type, self.kg_base.ONT.User))
            parsed_graph.add(
                (user_uri, self.kg_base.ONT.followsPath, learning_path_uri))

        self.storage.save_user_graph(str(user.id), parsed_graph)

        return updated_db_learning_path
