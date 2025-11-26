# Learning Path KG Integration - Implementation Summary

## Overview
Successfully implemented functionality to include Knowledge Graph (jsonld) data in learning path responses with an optional query parameter.

## Changes Made

### 1. **Schema Update** (`schemas.py`)
- Added optional `kg_data: Optional[str] = None` field to `LearningPathResponse`
- This field contains the JSON-LD string representation of the knowledge graph when requested

### 2. **Service Layer Updates** (`service.py`)

#### New Helper Method: `_graph_to_jsonld()`
- Converts RDF graph to JSON-LD format
- Handles serialization errors gracefully
- Returns empty JSON object if conversion fails

#### New Method: `read_learning_path_from_kg()`
- Reads a learning path from the user's turtle file using the learning path URI
- Extracts:
  - Learning path topic
  - All included concepts with their labels
  - Prerequisites for each concept
- Returns structured dictionary or None if not found
- Includes error logging for debugging

#### Updated Method: `get_learning_path()`
- Now accepts optional `include_kg: bool = False` parameter
- When `include_kg=True`:
  1. Fetches learning path from database
  2. Loads user's KG turtle file
  3. Serializes graph to JSON-LD format
  4. Attaches to response as `kg_data` field
- Gracefully handles KG retrieval failures without breaking the request

#### Kept Method: `get_learning_path_with_kg()` (deprecated)
- Now delegates to updated `get_learning_path()` method
- Maintained for backward compatibility

### 3. **Router Endpoint Update** (`router.py`)

#### Updated GET Endpoint: `/{learning_path_id}`
- Added query parameter: `include_kg: bool = False`
- Updated docstring to document the new parameter
- Parameter is optional - defaults to `False` for backward compatibility

## Usage

### Without KG Data (Default Behavior)
```bash
GET /learning-paths/123
```

**Response:**
```json
{
  "id": 123,
  "topic": "Machine Learning",
  "user_id": 1,
  "graph_uri": "http://example.org/ontology#learning_path_123",
  "created_at": "2025-11-05T10:30:00",
  "updated_at": "2025-11-05T10:30:00",
  "kg_data": null
}
```

### With KG Data
```bash
GET /learning-paths/123?include_kg=true
```

**Response:**
```json
{
  "id": 123,
  "topic": "Machine Learning",
  "user_id": 1,
  "graph_uri": "http://example.org/ontology#learning_path_123",
  "created_at": "2025-11-05T10:30:00",
  "updated_at": "2025-11-05T10:30:00",
  "kg_data": "{\"@context\": {...}, \"@graph\": [...], ...}"
}
```

## Technical Flow

```
1. Client Request
   GET /learning-paths/123?include_kg=true

2. Router Handler
   ↓
3. Service.get_learning_path(include_kg=True)
   ├─ Fetch from DB
   ├─ Auth check
   └─ If include_kg=True:
      ├─ Load user turtle file
      ├─ Serialize to JSON-LD
      └─ Attach to response

4. Response with kg_data field (jsonld string)
```

## Data Flow

```
User's Turtle File (TTL)
    ↓
KGStorage.load_user_graph()
    ↓
RDFLib Graph Object
    ↓
_graph_to_jsonld() - Serialize to JSON-LD
    ↓
String representation in response
```

## Error Handling

- **Learning Path Not Found**: Returns 404 with appropriate message
- **Authorization Failed**: Returns 403 if user not authorized
- **KG Data Retrieval Failed**: Logs error but doesn't break response (kg_data = null)
- **Serialization Error**: Falls back to empty JSON object

## Key Features

✅ **Backward Compatible** - include_kg defaults to false  
✅ **Efficient** - Only loads KG data when requested  
✅ **Error Resilient** - KG failures don't break the main response  
✅ **Flexible** - Uses JSON-LD standard format  
✅ **Secured** - Maintains authorization checks  
✅ **Logged** - All errors are logged for debugging  

## Testing Recommendations

1. Test without `include_kg` parameter (default behavior)
2. Test with `include_kg=true` when graph_uri exists
3. Test with `include_kg=true` when graph_uri is null
4. Test authorization with another user's learning path
5. Test with non-existent learning path ID
6. Test when turtle file doesn't exist

## Files Modified

- ✅ `core-service/app/features/learning_path/schemas.py`
- ✅ `core-service/app/features/learning_path/service.py`
- ✅ `core-service/app/features/learning_path/router.py`

## Next Steps (Optional)

1. Add integration tests for KG retrieval
2. Consider caching JSON-LD output for frequently accessed paths
3. Add metrics for KG data retrieval performance
4. Consider pagination for large concept lists
