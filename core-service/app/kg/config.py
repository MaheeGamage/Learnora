"""Knowledge Graph configuration and constants."""

from pathlib import Path
from app.config import settings


class KGConfig:
    """Configuration for Knowledge Graph storage and operations."""
    
    # Base paths
    BASE_PATH = Path(settings.KG_STORAGE_PATH)
    INSTANCES_PATH = BASE_PATH / "instances"
    
    # Instance data paths
    USERS_DIR = INSTANCES_PATH / "users"
    
    # Ontology file
    ONTOLOGY = BASE_PATH / "ontology.ttl"
    
    # RDF format
    RDF_FORMAT = settings.KG_FORMAT
    
    # Namespaces
    BASE_NAMESPACE = "http://learnora.ai"
    ONTOLOGY_NAMESPACE = BASE_NAMESPACE + "/ont#"

    @classmethod
    def ensure_directories(cls):
        """Ensure all necessary directories exist."""
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
