from rdflib import URIRef
from app.kg.ontologies.user_knowledge import UserKnowledgeOntology
from app.kg.storage import KGStorage
import logging

logger = logging.getLogger(__name__)

USER_LOCAL_IDENTIFIER_PREFIX = "user_"

class UserKG:
    def __init__(self):
        """Initialize with KG storage and ontology helper."""
        self.storage = KGStorage()
        self.ontology = UserKnowledgeOntology()
        
    def create_user(
        self,
        user_db_id: str
    ) -> URIRef:
        """
        Create a new user in the knowledge graph.
        
        Args:
            user_db_id: User database identifier
    
        Returns:
            kg object of user
        """
        
        user_kg_local_identifier = USER_LOCAL_IDENTIFIER_PREFIX + str(user_db_id)
        
        user_graph = self.storage.load_user_graph(user_kg_local_identifier)
        
        user_uri = self.ontology.get_user_by_id(user_graph, user_kg_local_identifier)
        user_exists = (user_uri, None, None) in user_graph
        
        if user_exists:
            logger.error(f"User KG already exists for user ID: {user_db_id}")
            raise ValueError("User KG already exists.")

        user = self.ontology.add_user(user_graph, user_kg_local_identifier)
        self.storage.save_user_graph(graph=user_graph, user_id=user_kg_local_identifier)
        return user