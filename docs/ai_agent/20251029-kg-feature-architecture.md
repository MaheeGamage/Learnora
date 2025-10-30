# Knowledge Graph Feature-Based Architecture

**Date**: 2025-01-31  
**Status**: Completed  
**Tests**: 50 passing

## Overview

Refactored Knowledge Graph (KG) integration from centralized manager pattern to feature-based architecture. This distributes KG operations into domain-specific feature services to prevent code bloat and align with existing codebase patterns.

## Architecture

### Previous Structure (Centralized)
```
app/kg/
  ├── manager.py          # Single class with all KG operations (REMOVED)
  ├── config.py           # Configuration
  ├── base.py             # Base RDF operations
  ├── storage.py          # File I/O for RDF
  └── ontologies/         # Python helpers for ontologies
```

### New Structure (Feature-Based)
```
app/kg/                   # Infrastructure layer only
  ├── config.py           # Configuration
  ├── base.py             # Base RDF operations
  ├── storage.py          # File I/O for RDF
  └── ontologies/         # Python helpers for ontologies

app/features/
  ├── concept/            # NEW: Concept management
  │   └── service.py      # ConceptService
  ├── user_knowledge/     # NEW: User knowledge tracking
  │   └── service.py      # UserKnowledgeService
  └── learning_path/
      └── service.py      # Extended with KG operations
```

## Services

### ConceptService (`app/features/concept/service.py`)
Manages concept definitions and prerequisites.

**Methods:**
- `add_concept(concept_id, label, description, prerequisites)` - Add new concept with optional prerequisites
- `get_all_concepts()` - Retrieve all concepts from KG
- `get_concept_prerequisites(concept_id)` - Get prerequisites for a concept

**Storage:** `data/graph/instances/concepts.ttl`

### UserKnowledgeService (`app/features/user_knowledge/service.py`)
Tracks user knowledge and learning progress.

**Methods:**
- `mark_concept_as_known(user_id, concept_id)` - Mark concept as known
- `mark_concept_as_learning(user_id, concept_id)` - Mark concept as currently learning
- `get_user_known_concepts(user_id)` - Get all concepts user knows
- `get_user_learning_concepts(user_id)` - Get concepts user is learning
- `user_knows_concept(user_id, concept_id)` - Check if user knows concept
- `assign_learning_path_to_user(user_id, thread_id)` - Assign learning path to user

**Storage:** `data/graph/instances/user_{user_id}.ttl`

### LearningPathService (`app/features/learning_path/service.py`)
Extended existing service with KG operations for learning paths.

**New KG Methods:**
- `create_learning_path_kg(thread_id, topic, concept_ids)` - Create learning path in KG
- `get_learning_path_concepts(thread_id)` - Get concepts from learning path

**Storage:** `data/graph/instances/thread_{thread_id}.ttl`

**Existing Methods:** `start_learning_path()`, `resume_learning_path()` (unchanged)

## Data Storage

### Ontologies (Schema Definitions)
Located in `data/graph/ontologies/`:
- `concept.ttl` - Defines `kg:Concept`, `kg:hasPrerequisite`
- `learning_path.ttl` - Defines `kg:LearningPath`, `kg:includesConcept`
- `user_knowledge.ttl` - Defines `kg:User`, `kg:knows`, `kg:isLearning`

### Instance Data
Located in `data/graph/instances/` (gitignored):
- `concepts.ttl` - All concept instances
- `user_{user_id}.ttl` - User knowledge per user
- `thread_{thread_id}.ttl` - Learning path per conversation thread

## Design Decisions

### 1. Feature-Based Organization
**Rationale:** Prevents manager.py from becoming a bloated "god object". Each feature service owns its domain logic.

### 2. Singular Naming Convention
**Examples:** `concept/`, `user_knowledge/` (not `concepts/`, `user_knowledges/`)  
**Rationale:** Follows existing patterns in codebase (e.g., `learning_path/`)

### 3. Service Files vs Router/CRUD/Models
**Current:** Only `service.py` files created for KG features  
**Future:** Will add `router.py`, `schemas.py` as needed for API endpoints

### 4. Lazy Graph Initialization
**Implementation:** `LearningPathService.graph` property uses lazy loading  
**Rationale:** Prevents Google GenAI initialization during test imports

## Testing

### Test Structure
- `tests/test_kg_services.py` - Feature service integration tests (12 tests)
- `tests/test_kg_ontologies.py` - Ontology helper tests (14 tests)
- `tests/test_kg_storage.py` - Storage layer tests (11 tests)
- `tests/test_kg_config.py` - Configuration tests (6 tests)
- `tests/test_kg_base.py` - Base operations tests (7 tests)

**Total:** 50 tests passing

### Test Fixtures
```python
@pytest.fixture
def concept_service():
    return ConceptService()

@pytest.fixture
def learning_path_service():
    return LearningPathService()

@pytest.fixture
def user_knowledge_service():
    return UserKnowledgeService()
```

## Ontology Refinements

### Removed Opinionated Properties
- ❌ `kg:difficulty` - Removed from concept.ttl (too opinionated)
- ❌ `kg:conceptOrder` - Removed from learning_path.ttl (order derived from prerequisites)

### Renamed for Clarity
- ✅ `kg:requires` → `kg:hasPrerequisite` (more descriptive)

### Backward-Pointing Prerequisites
Concepts point to their prerequisites (not forward to dependents):
```turtle
:AI kg:hasPrerequisite :Math .
:AI kg:hasPrerequisite :Python .
```

This allows flexible topological ordering at query time.

## Migration Notes

### Removed Files
- `app/kg/manager.py` - Logic distributed to feature services
- `tests/test_kg_manager.py` - Replaced with `tests/test_kg_services.py`

### Code Changes
**Before:**
```python
from app.kg.manager import KnowledgeGraphManager
kg = KnowledgeGraphManager()
kg.add_concept("Python", "Python Programming")
```

**After:**
```python
from app.features.concept.service import ConceptService
concept_service = ConceptService()
concept_service.add_concept("Python", "Python Programming")
```

## Future Work

1. **Router Implementation**
   - Create `app/features/concept/router.py` for concept CRUD endpoints
   - Create `app/features/user_knowledge/router.py` for user knowledge endpoints

2. **Schema Validation**
   - Add `app/features/concept/schemas.py` with Pydantic models
   - Add `app/features/user_knowledge/schemas.py` with Pydantic models

3. **Query Optimization**
   - Add SPARQL query caching for frequently accessed data
   - Optimize prerequisite graph traversals

## References

- **Ontology Files:** `data/graph/ontologies/*.ttl`
- **RDF Library:** rdflib 7.1.1
- **Serialization Format:** Turtle (`.ttl`)
- **Namespaces:**
  - Concepts: `http://learnora.ai/kg#`
  - Users: `http://learnora.ai/users#`
  - Paths: `http://learnora.ai/paths#`
