"""Knowledge Graph configuration and constants."""

from pathlib import Path
from app.config import settings


class KGConfig:
    """Configuration for Knowledge Graph storage and operations."""
    
    # Base paths
    BASE_PATH = Path(settings.KG_STORAGE_PATH)
    ONTOLOGIES_PATH = BASE_PATH / "ontologies"
    INSTANCES_PATH = BASE_PATH / "instances"
    
    # Instance data paths
    CONCEPTS_FILE = INSTANCES_PATH / "concepts.ttl"
    USERS_DIR = INSTANCES_PATH / "users"
    
    # Ontology files
    CONCEPT_ONTOLOGY = ONTOLOGIES_PATH / "concept.ttl"
    LEARNING_PATH_ONTOLOGY = ONTOLOGIES_PATH / "learning_path.ttl"
    USER_KNOWLEDGE_ONTOLOGY = ONTOLOGIES_PATH / "user_knowledge.ttl"
    
    # RDF format
    RDF_FORMAT = settings.KG_FORMAT
    
    # Namespaces
    KG_NAMESPACE = "http://learnora.ai/kg#"
    USERS_NAMESPACE = "http://learnora.ai/users#"
    PATHS_NAMESPACE = "http://learnora.ai/paths#"
    
    @classmethod
    def ensure_directories(cls):
        """Ensure all necessary directories exist."""
        cls.ONTOLOGIES_PATH.mkdir(parents=True, exist_ok=True)
        cls.INSTANCES_PATH.mkdir(parents=True, exist_ok=True)
        cls.USERS_DIR.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_user_file_path(cls, user_id: str) -> Path:
        """
        Get the file path for a user's knowledge graph.
        This file now contains both user knowledge and their learning paths.
        """
        return cls.USERS_DIR / f"user_{user_id}.ttl"


# Ensure directories exist on import
KGConfig.ensure_directories()
