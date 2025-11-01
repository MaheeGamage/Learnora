import re
from features.users.constant import USER_GRAPH_LOCAL_IDENTIFIER_PREFIX

def get_user_kg_local_name(user_db_id: str) -> str:
    """
    Generate a KG URI local name for a user by appending 'user' to the beginning of the user DB ID.

    Args:
        user_db_id (int): The user's database ID.

    Returns:
        str: The KG URI local name (e.g., 'user123').
    """
    return f"{USER_GRAPH_LOCAL_IDENTIFIER_PREFIX}{user_db_id}"