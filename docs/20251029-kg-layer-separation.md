# Knowledge Graph Layer Separation

**Date**: October 29, 2025  
**Status**: Completed  
**Tests**: 50 passing

## Overview

Separated Knowledge Graph (KG) operations from service layer business logic by introducing dedicated `kg.py` files in each feature folder. This creates proper layer separation where:

- **KG Layer** (`kg.py`): Low-level RDF graph operations, storage I/O
- **Service Layer** (`service.py`): Business logic, validation, orchestration

## Architecture

### Before (Mixed Responsibilities)
```
app/features/concept/
  └── service.py         # Mixed: business logic + KG operations
```

### After (Layer Separation)
```
app/features/concept/
  ├── kg.py              # KG operations only
  └── service.py         # Business logic only
```

## Layer Responsibilities

### KG Layer (`kg.py`)
**Purpose:** Direct interaction with RDF graphs and storage

**Responsibilities:**
- Load/save RDF graphs from storage
- Execute SPARQL queries via ontology helpers
- Manage graph-level operations (create, read, update)
- Handle RDF-specific concerns (URIRefs, triples, namespaces)

**Does NOT:**
- Validate business rules
- Orchestrate multiple operations
- Handle application-level concerns

### Service Layer (`service.py`)
**Purpose:** Application business logic

**Responsibilities:**
- Validate business rules (e.g., prerequisites must exist)
- Orchestrate multiple KG operations
- Handle application-level concerns (logging, notifications)
- Provide clean API for routers/controllers
- Future: integrate with other services (database, external APIs)

**Does NOT:**
- Directly manipulate RDF graphs
- Call storage methods
- Know about RDFLib implementation details

## Implementation

### ConceptKG (`app/features/concept/kg.py`)
```python
class ConceptKG:
    """Knowledge Graph layer for concept operations."""
    
    def __init__(self):
        self.storage = KGStorage()
        self.ontology = ConceptOntology()
    
    def create_concept(...) -> URIRef:
        # Loads graph, adds concept, saves graph
        
    def get_concept(...) -> URIRef:
        # Loads graph, queries for concept
        
    def concept_exists(...) -> bool:
        # Checks if concept present in graph
```

**Key Methods:**
- `create_concept()` - Add concept to RDF graph
- `get_concept()` - Retrieve concept URI
- `get_all_concepts()` - List all concepts
- `get_concept_prerequisites()` - Query prerequisites
- `concept_exists()` - Check existence in graph

### ConceptService (`app/features/concept/service.py`)
```python
class ConceptService:
    """Service layer for managing concepts with business logic."""
    
    def __init__(self):
        self.kg = ConceptKG()  # Delegates to KG layer
    
    def add_concept(...) -> URIRef:
        # 1. Validates prerequisites exist (business rule)
        # 2. Delegates to kg.create_concept()
        # 3. Logs operation
```

**Business Logic Examples:**
- Validates prerequisites exist before adding concept
- Allows adding concept that already exists (idempotent)
- Could add future logic: notifications, achievement tracking, etc.

### UserKnowledgeKG (`app/features/user_knowledge/kg.py`)
```python
class UserKnowledgeKG:
    """Knowledge Graph layer for user knowledge operations."""
    
    def __init__(self):
        self.storage = KGStorage()
        self.user_ontology = UserKnowledgeOntology()
        self.concept_ontology = ConceptOntology()
        self.learning_path_ontology = LearningPathOntology()
    
    def mark_known(...) -> None:
        # Manages user's known concepts in RDF
        
    def check_knows_concept(...) -> bool:
        # Queries user's knowledge from RDF
```

**Key Methods:**
- `mark_known()` - Add concept to user's known list
- `mark_learning()` - Add concept to user's learning list
- `assign_path()` - Link learning path to user
- `get_known_concepts()` - Query user's knowledge
- `get_learning_concepts()` - Query current learning
- `check_knows_concept()` - Verify user knowledge

### UserKnowledgeService (`app/features/user_knowledge/service.py`)
```python
class UserKnowledgeService:
    """Service layer for user knowledge with business logic."""
    
    def __init__(self):
        self.kg = UserKnowledgeKG()
    
    def mark_concept_as_known(...) -> None:
        # Future: Check if was learning first, trigger achievements
        # Delegates to kg.mark_known()
```

**Future Business Logic:**
- Check if user was learning concept before marking known
- Trigger achievement/notification system
- Limit number of concurrent learning concepts
- Validate prerequisites are met before learning

### LearningPathKG (`app/features/learning_path_planner/kg.py`)
```python
class LearningPathKG:
    """Knowledge Graph layer for learning path operations."""
    
    def __init__(self):
        self.storage = KGStorage()
        self.learning_path_ontology = LearningPathOntology()
        self.concept_ontology = ConceptOntology()
    
    def create_path(...) -> URIRef:
        # Creates learning path with concepts in RDF
```

**Key Methods:**
- `create_path()` - Create learning path in RDF
- `get_path()` - Retrieve path graph
- `get_path_concepts()` - List concepts in path
- `path_exists()` - Check if path exists

### LearningPathService (`app/features/learning_path_planner/service.py`)
```python
class LearningPathService:
    """Service layer for learning paths with business logic."""
    
    def __init__(self):
        self.kg = LearningPathKG()
        self._graph = None  # LangGraph (lazy loaded)
    
    def create_learning_path_kg(...) -> URIRef:
        # Validates path doesn't exist
        # Delegates to kg.create_path()
```

**Business Logic:**
- Validates learning path doesn't already exist
- Could add: validate concept order, check user permissions, etc.
- Maintains separate LangGraph operations for AI-driven planning

## Benefits

### 1. **Clear Separation of Concerns**
- KG layer: "How to store/retrieve data in RDF"
- Service layer: "What business rules apply"

### 2. **Easier Testing**
- Can test KG operations independently
- Can mock KG layer when testing business logic
- Service tests focus on validation, not storage

### 3. **Easier Maintenance**
- RDF changes isolated to `kg.py`
- Business logic changes isolated to `service.py`
- No need to understand RDF when modifying business rules

### 4. **Better Scalability**
- Service layer can grow with business features
- KG layer remains focused on data operations
- Can add caching, optimization to KG layer without affecting services

### 5. **Reusability**
- KG operations can be reused by multiple services
- Clear interface between layers via method signatures

## Design Patterns

### Delegation Pattern
Service layer delegates to KG layer:
```python
# Service
def add_concept(self, ...):
    # Business validation
    if prerequisites:
        for prereq in prerequisites:
            if not self.kg.concept_exists(prereq):
                raise ValueError(...)
    
    # Delegate to KG
    return self.kg.create_concept(...)
```

### Single Responsibility Principle
- Each class has one reason to change:
  - `ConceptKG` changes if RDF storage changes
  - `ConceptService` changes if business rules change

### Dependency Injection
Services receive KG layer via composition:
```python
class ConceptService:
    def __init__(self):
        self.kg = ConceptKG()  # Could be injected for testing
```

## File Organization

```
app/features/
├── concept/
│   ├── kg.py               # ConceptKG
│   └── service.py          # ConceptService
├── user_knowledge/
│   ├── kg.py               # UserKnowledgeKG
│   └── service.py          # UserKnowledgeService
└── learning_path_planner/
    ├── kg.py               # LearningPathKG
    └── service.py          # LearningPathService
```

## Future Enhancements

### 1. **KG Layer**
- Add caching for frequently accessed graphs
- Optimize SPARQL queries
- Add batch operations for performance
- Implement graph versioning

### 2. **Service Layer**
- Add transaction support across multiple KG operations
- Implement event-driven notifications
- Add permission/authorization checks
- Integrate with external services (recommendation engine, etc.)

### 3. **Testing**
- Add integration tests between layers
- Mock KG layer for faster service tests
- Add performance benchmarks

## Migration Notes

### Changed Imports
**Before:**
```python
from app.kg.storage import KGStorage
from app.kg.ontologies import ConceptOntology

class ConceptService:
    def __init__(self):
        self.storage = KGStorage()
        self.concept_helper = ConceptOntology()
```

**After:**
```python
from app.features.concept.kg import ConceptKG

class ConceptService:
    def __init__(self):
        self.kg = ConceptKG()
```

### No API Changes
- Service layer public methods unchanged
- Tests continue to work without modification
- Routers (when added) will call same service methods

## References

- **Previous Architecture**: `docs/20250131-kg-feature-architecture.md`
- **Layer Count**: 3 layers now
  1. Infrastructure: `app/kg/` (config, storage, ontologies)
  2. KG Layer: `app/features/*/kg.py` (RDF operations)
  3. Service Layer: `app/features/*/service.py` (business logic)
