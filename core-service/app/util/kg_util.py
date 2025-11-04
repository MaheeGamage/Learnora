import re
from app.features.learning_path.constant import LEARNING_PATH_GRAPH_LOCAL_IDENTIFIER_PREFIX
from app.features.users.constant import USER_GRAPH_LOCAL_IDENTIFIER_PREFIX

def get_user_kg_local_name(user_db_id: str) -> str:
    """
    Generate a KG URI local name for a user by appending 'user' to the beginning of the user DB ID.

    Args:
        user_db_id (int): The user's database ID.

    Returns:
        str: The KG URI local name (e.g., 'user123').
    """
    return f"{USER_GRAPH_LOCAL_IDENTIFIER_PREFIX}{user_db_id}"

def get_learning_path_kg_local_name(learning_path_db_id: int) -> str:
    """
    Generate a KG URI local name for a learning path by appending 'learningpath' to the beginning of the learning path DB ID.

    Args:
        learning_path_db_id (int): The learning path's database ID.

    Returns:
        str: The KG URI local name (e.g., 'learningpath123').
    """
    return f"{LEARNING_PATH_GRAPH_LOCAL_IDENTIFIER_PREFIX}{learning_path_db_id}"