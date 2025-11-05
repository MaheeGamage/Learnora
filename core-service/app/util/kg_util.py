from rdflib import Graph, URIRef
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

def extract_subgraph(graph, start_node, max_depth=2):
    """Extract a subgraph around ``start_node`` up to ``max_depth`` hops.

    Traverses outgoing and incoming triples breadth-first, following only
    URIRef nodes. Returns a new rdflib.Graph containing discovered triples.

    Args:
        graph: Source RDF graph.
        start_node: Node to start traversal from.
        max_depth: Maximum hops to traverse (default: 2).

    Returns:
        rdflib.Graph with collected triples.
    """
    sub = Graph()
    seen = set()
    frontier = {start_node}
    for depth in range(max_depth):
        next_frontier = set()
        for node in frontier:
            # outgoing triples
            for s, p, o in graph.triples((node, None, None)):
                sub.add((s, p, o))
                if isinstance(o, URIRef) and o not in seen:
                    next_frontier.add(o)
            # incoming triples
            for s, p, o in graph.triples((None, None, node)):
                sub.add((s, p, o))
                if isinstance(s, URIRef) and s not in seen:
                    next_frontier.add(s)
            seen.add(node)
        frontier = next_frontier
    return sub