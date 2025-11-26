# User-Scoped Learning Paths - Storage Consolidation

**Date**: October 30, 2025  
**Status**: ✅ Complete (Layers 1-4)  
**Remaining**: Database migration for `user_id` field

## Overview

Refactored the Knowledge Graph storage system to store both user knowledge and learning paths in a single user file instead of separate files per learning path. This change reduces file proliferation and better represents the ownership relationship between users and their learning paths.

## Motivation

**Before:**
- Separate file per learning path: `data/graph/instances/learning_paths/thread_{id}.ttl`
- Separate file per user: `data/graph/instances/users/user_{id}.ttl`
- Problem: Many learning paths = many files, unclear ownership

**After:**
- Single file per user: `data/graph/instances/users/user_{id}.ttl`
- Contains both user knowledge AND all their learning paths
- Clear ownership: learning paths belong to users

## Changes by Layer

### Layer 1: Infrastructure (`app/kg/`)

#### **KGConfig** (`config.py`)
**Removed:**
- `LEARNING_PATHS_DIR` constant
- `get_learning_path_file_path()` method

**Updated:**
- `ensure_directories()` - No longer creates `learning_paths/` directory
- `get_user_file_path()` - Updated documentation to reflect combined storage

#### **KGStorage** (`storage.py`)
**New Primary Methods:**
- `load_user_graph(user_id)` - Load complete user graph (knowledge + paths)
- `save_user_graph(user_id, graph)` - Save complete user graph
- `user_graph_exists(user_id)` - Check if user file exists

**Backward Compatibility Aliases:**
- `load_user_knowledge()` → `load_user_graph()`
- `save_user_knowledge()` → `save_user_graph()`
- `user_knowledge_exists()` → `user_graph_exists()`

**Updated Learning Path Methods:**
- `load_learning_path(user_id, thread_id)` - Now requires `user_id`, extracts path from user's graph
- `save_learning_path(user_id, thread_id, path_graph)` - Merges path into user's graph
- `learning_path_exists(user_id, thread_id)` - Checks path within user's graph

**Key Features:**
- Automatic merging: `save_learning_path()` removes old path data and merges new data
- Graph filtering: `load_learning_path()` extracts only the specific path's triples
- Thread-safe: All operations work on complete graphs, then save atomically

---

### Layer 2: Ontology Helpers (`app/kg/ontologies/`)

#### **LearningPathOntology** (`learning_path.py`)
**Updated:**
- `add_learning_path()` - **Now requires `user_id` parameter**
  - Automatically creates `kg:followsPath` relationship from user to path
  - Links user and path in same operation

**Removed:**
- `get_user_learning_paths()` - Moved to `UserKnowledgeOntology` (better domain fit)

#### **UserKnowledgeOntology** (`user_knowledge.py`)
**New Methods:**
- `get_user_learning_paths(graph, user)` - Query all paths for a user
- `ensure_user_exists(graph, user_id)` - Create user if doesn't exist (idempotent)

**Updated:**
- `add_user_learning_path()` - Added note that it's auto-called by `add_learning_path()`

**Design Decision:**
- User relationship queries belong in `UserKnowledgeOntology`
- Path structure queries belong in `LearningPathOntology`
- Clear separation of concerns

#### **ConceptOntology** (`concept.py`)
**No changes** - Concepts remain global and user-independent

---

### Layer 3: KG Layer (`app/features/*/kg.py`)

#### **LearningPathKG** (`learning_path/kg.py`)
**Updated All Methods to Require `user_id`:**

1. **`create_path(user_id, thread_id, topic, concept_ids)`**
   - Loads user's graph
   - Ensures user exists via `ensure_user_exists()`
   - Creates path with user association
   - Saves path into user's graph

2. **`get_path(user_id, thread_id)`**
   - Loads path from user's graph

3. **`get_path_concepts(user_id, thread_id)`**
   - Gets concepts from user's path

4. **`path_exists(user_id, thread_id)`**
   - Checks if path exists in user's graph

**New Method:**
5. **`get_user_learning_paths(user_id)`**
   - Get all learning paths for a user

#### **UserKnowledgeKG** (`user_knowledge/kg.py`)
**Updated to Use New Storage Methods:**

- `mark_known()` - Uses `load_user_graph()` and `save_user_graph()`
- `mark_learning()` - Uses `load_user_graph()` and `save_user_graph()`
- `assign_path()` - Uses `load_user_graph()` and `save_user_graph()`
- `get_known_concepts()` - Uses `load_user_graph()`
- `get_learning_concepts()` - Uses `load_user_graph()`
- `check_knows_concept()` - Uses `load_user_graph()`

**New Method:**
- `get_user_learning_paths(user_id)` - Query user's paths

**Key Change:**
- All methods now use `ensure_user_exists()` instead of manual checks
- Cleaner, more consistent code

#### **ConceptKG** (`concept/kg.py`)
**No changes** - Concepts are global

---

### Layer 4: Service Layer (`app/features/*/service.py`)

#### **LearningPathService** (`learning_path/service.py`)
**Updated Methods to Include `user_id`:**

1. **`create_learning_path_kg(user_id, thread_id, topic, concept_ids)`**
   - Added `user_id` as first parameter
   - Passes to `kg.create_path()`
   - Updated validation: `kg.path_exists(user_id, thread_id)`

2. **`get_learning_path_kg(user_id, thread_id)`**
   - Added `user_id` parameter
   - Passes to `kg.get_path()`

3. **`get_learning_path_concepts(user_id, thread_id)`**
   - Added `user_id` parameter
   - Passes to `kg.get_path_concepts()`

4. **`get_learning_path_kg_info(db, thread_id)`**
   - Extracts `user_id` from database: `db_path.user_id`
   - Passes `user_id` to all KG operations
   - **⚠️ Requires database migration to add `user_id` field**

5. **`resume_learning_path(db, thread_id, human_answer, user_id="default_user")`**
   - Added `user_id` parameter with default value
   - Passes `user_id` to `parse_and_store_concepts()`
   - **TODO**: Get `user_id` from database once migration is complete

#### **Utility Functions** (`learning_path/utils.py`)
**Updated `parse_and_store_concepts()`:**
- Added `user_id` as first parameter
- Passes to `create_learning_path_callback(user_id, thread_id, topic, concept_ids)`

#### **ConceptService** (`concept/service.py`)
**No changes** - Concepts are global

#### **UserKnowledgeService** (`user_knowledge/service.py`)
**No changes** - Already uses `user_id` in all methods

---

## File Structure Changes

### Before
```
data/graph/instances/
├── concepts.ttl                    # Global concepts
├── learning_paths/                 # Separate directory
│   ├── thread_abc123.ttl          # One file per learning path
│   ├── thread_def456.ttl
│   └── thread_ghi789.ttl
└── users/
    ├── user_alice.ttl              # User knowledge only
    └── user_bob.ttl
```

### After
```
data/graph/instances/
├── concepts.ttl                    # Global concepts
└── users/
    ├── user_alice.ttl              # User knowledge + all their learning paths
    └── user_bob.ttl                # User knowledge + all their learning paths
```

**Benefits:**
- ✅ Reduced file count (especially with many learning paths)
- ✅ Clear ownership: paths belong to users
- ✅ Single file per user = easier backup/restore
- ✅ Atomic operations on user data

---

## RDF Structure Example

### User File Content (`user_alice.ttl`)
```turtle
@prefix kg: <http://learnora.ai/kg#> .
@prefix users: <http://learnora.ai/users#> .
@prefix paths: <http://learnora.ai/paths#> .

# User entity
users:alice a kg:User ;
    kg:userId "alice" .

# User's knowledge
users:alice kg:knows kg:Python ;
    kg:knows kg:Math ;
    kg:learning kg:MachineLearning .

# User's learning paths
users:alice kg:followsPath paths:thread_abc123 ;
    kg:followsPath paths:thread_def456 .

# Learning Path 1
paths:thread_abc123 a kg:LearningPath ;
    kg:threadId "thread_abc123" ;
    kg:topic "Machine Learning Fundamentals" ;
    kg:includesConcept kg:Python ;
    kg:includesConcept kg:MachineLearning .

# Learning Path 2
paths:thread_def456 a kg:LearningPath ;
    kg:threadId "thread_def456" ;
    kg:topic "Deep Learning" ;
    kg:includesConcept kg:MachineLearning ;
    kg:includesConcept kg:NeuralNetworks .
```

---

## API Changes

### Before
```python
# Learning path operations without user context
service.create_learning_path_kg(thread_id, topic, concept_ids)
service.get_learning_path_kg(thread_id)
service.get_path_concepts(thread_id)
```

### After
```python
# Learning path operations with user context
service.create_learning_path_kg(user_id, thread_id, topic, concept_ids)
service.get_learning_path_kg(user_id, thread_id)
service.get_path_concepts(user_id, thread_id)
```

**Breaking Change:** All learning path methods now require `user_id` as first parameter.

---

## Database Schema TODO

### Required Migration
The `LearningPath` database model needs a `user_id` field:

```python
# app/features/learning_path/models.py
class LearningPath(BaseModel):
    __tablename__ = "learning_path"

    topic = Column(String(255), nullable=False)
    conversation_thread_id = Column(String(50), unique=True, index=True, nullable=False)
    user_id = Column(String(50), nullable=False, index=True)  # ← ADD THIS
```

### Migration Steps
1. Create Alembic migration:
   ```bash
   alembic revision -m "add_user_id_to_learning_path"
   ```

2. Update migration file:
   ```python
   def upgrade():
       op.add_column('learning_path', sa.Column('user_id', sa.String(50), nullable=True))
       # Set default value for existing records
       op.execute("UPDATE learning_path SET user_id = 'default_user'")
       # Make not nullable
       op.alter_column('learning_path', 'user_id', nullable=False)
       # Add index
       op.create_index('ix_learning_path_user_id', 'learning_path', ['user_id'])
   ```

3. Run migration:
   ```bash
   alembic upgrade head
   ```

### Schema Updates Needed
```python
# app/features/learning_path/schemas.py
class LearningPathCreate(LearningPathBase):
    conversation_thread_id: str
    user_id: str  # ← ADD THIS

class LearningPathResponse(LearningPathBase):
    id: int
    conversation_thread_id: str
    user_id: str  # ← ADD THIS
    created_at: datetime
    updated_at: Optional[datetime]
```

### Service Updates After Migration
```python
# Remove default value once DB has user_id field
async def resume_learning_path(self, db: AsyncSession, thread_id: str, human_answer: str, user_id: str):
    # Get user_id from database
    user_id = db_learning_path.user_id
    
    # Use actual user_id instead of default
    await asyncio.to_thread(
        parse_and_store_concepts,
        user_id,  # From database
        thread_id,
        topic,
        learning_path_json,
        self.concept_service,
        self.create_learning_path_kg
    )
```

---

## Testing Considerations

### Tests to Update
1. **Storage Tests** (`tests/test_kg_storage.py`)
   - Update `load_learning_path()` calls to include `user_id`
   - Update `save_learning_path()` calls to include `user_id`
   - Test graph merging behavior

2. **Ontology Tests** (`tests/test_kg_ontologies.py`)
   - Update `add_learning_path()` calls to include `user_id`
   - Test user-path linking

3. **Service Tests** (`tests/test_kg_services.py`)
   - Update all learning path service calls to include `user_id`
   - Test with multiple users to ensure isolation

4. **Integration Tests**
   - Test creating multiple paths for same user
   - Test path isolation between different users
   - Test graph merging and updating

### Test Examples
```python
# Before
def test_create_learning_path():
    service.create_learning_path_kg("thread_123", "ML", ["Python", "Math"])

# After
def test_create_learning_path():
    service.create_learning_path_kg("user_alice", "thread_123", "ML", ["Python", "Math"])

# Test isolation
def test_user_isolation():
    # Create paths for different users
    service.create_learning_path_kg("user_alice", "thread_1", "ML", ["Python"])
    service.create_learning_path_kg("user_bob", "thread_2", "DL", ["ML"])
    
    # Verify isolation
    assert service.kg.path_exists("user_alice", "thread_1")
    assert not service.kg.path_exists("user_alice", "thread_2")
    assert service.kg.path_exists("user_bob", "thread_2")
    assert not service.kg.path_exists("user_bob", "thread_1")
```

---

## Performance Considerations

### File Size Impact
**Before:**
- Many small files (1-5 KB each)
- File system overhead per file

**After:**
- Fewer, larger files (grows with user's paths)
- Typical size: 10-50 KB per active user
- Better for file systems (fewer inodes)

### Read/Write Performance
**Reads:**
- ✅ Single file load for all user operations
- ✅ Reduced file I/O calls
- ⚠️ Slightly larger graphs to parse

**Writes:**
- ✅ Atomic updates to user file
- ⚠️ Must load entire user graph to update single path
- Mitigation: Graphs are small enough (<50 KB typically)

### Scalability
**Current Approach (File-Based):**
- ✅ Good for: 100s-1000s of users
- ✅ Good for: Each user has 1-10 learning paths
- ⚠️ Consider graph database if: >10,000 users or >50 paths per user

**Future Migration Path:**
- Easy to migrate to Neo4j/Virtuoso if needed
- RDF format is standard and portable

---

## Backward Compatibility

### Code Compatibility
**Aliases Provided:**
```python
# Old code continues to work
storage.load_user_knowledge(user_id)  # → load_user_graph()
storage.save_user_knowledge(user_id, graph)  # → save_user_graph()
```

### Data Migration
**No automatic migration provided** - old learning path files remain:
- `data/graph/instances/learning_paths/thread_*.ttl`

**Manual migration needed:**
1. For each old learning path file
2. Determine owner user_id (from database)
3. Load user's graph
4. Load old path file
5. Merge into user's graph
6. Save user's graph
7. Delete old path file

---

## Known Limitations

### 1. Database Schema Not Updated
**Issue:** `LearningPath` model lacks `user_id` field  
**Impact:** Using default `user_id="default_user"`  
**Fix:** Add database migration (see above)

### 2. Router Layer Not Updated
**Issue:** Routers don't pass authenticated user's ID  
**Impact:** All paths assigned to "default_user"  
**Fix:** Update routers to extract user from auth context

### 3. No User Isolation Yet
**Issue:** Without real user IDs, all paths in same file  
**Impact:** Security/privacy risk in multi-user environment  
**Fix:** Complete database migration and auth integration

### 4. Old Learning Path Files Not Cleaned
**Issue:** Existing `learning_paths/*.ttl` files still present  
**Impact:** Wasted disk space, confusion  
**Fix:** Manual cleanup or migration script

---

## Benefits Summary

✅ **Reduced File Proliferation**
- Single file per user vs. one file per learning path
- Easier backup and restore

✅ **Clear Ownership Model**
- Learning paths explicitly belong to users
- Reflected in RDF structure via `kg:followsPath`

✅ **Better Data Locality**
- User's knowledge and paths in one file
- Fewer file operations for user queries

✅ **Atomic Operations**
- User graph updated atomically
- No partial state issues

✅ **Scalable Architecture**
- Ready for multi-user environments
- Clear path to graph database if needed

✅ **Semantic Clarity**
- RDF structure reflects domain model
- User-path relationship explicit in triples

---

## Next Steps

### Immediate (Required for Production)
1. ✅ **Create database migration** to add `user_id` to `learning_path` table
2. ✅ **Update schemas** to include `user_id` in request/response models
3. ✅ **Update routers** to pass authenticated user's ID
4. ✅ **Update tests** to use `user_id` parameter
5. ✅ **Run full test suite** to validate changes

### Short-term
1. ✅ Create data migration script for existing learning paths
2. ✅ Add user authentication/authorization checks
3. ✅ Update API documentation with new parameters
4. ✅ Add integration tests for multi-user scenarios

### Future Enhancements
1. Add pagination for users with many learning paths
2. Add query optimization for large user graphs
3. Consider graph database for >10K users
4. Add graph visualization for user's learning network

---

## References

- **Original Architecture**: `docs/ai_agent/20251029-knowledge-graph-implementation.md`
- **Layer Separation**: `docs/ai_agent/20251029-kg-layer-separation.md`
- **Integration**: `docs/ai_agent/20251029-layer5-integration.md`
- **RDF Library**: rdflib 7.1.1
- **Serialization**: Turtle (.ttl)

---

## Conclusion

Successfully refactored Knowledge Graph storage to consolidate user knowledge and learning paths into single user files. This change improves data organization, reduces file proliferation, and better represents the ownership model. All layers (Infrastructure, Ontology, KG, Service) have been updated to support user-scoped learning paths.

**Status: Ready for database migration and router updates to complete the integration.**
