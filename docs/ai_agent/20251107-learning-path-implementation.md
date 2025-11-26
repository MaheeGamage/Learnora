# Learning Path API & Integration Documentation

## Quick Overview

Complete implementation of learning path CRUD operations with React Query integration and a full-featured UI component for selecting and visualizing learning paths.

## Architecture

```
API Layer (api.ts)
    ↓
React Query Hooks (queries.ts)
    ↓
LearningPathIntegration Component
├── PathSelector (sidebar)
├── PathVisualizer (main content)
└── LearningPathVisualization (graph)
```

## Files Created

| File | Purpose |
|------|---------|
| `types.ts` | TypeScript types for all data structures |
| `api.ts` | Axios API client functions |
| `queries.ts` | React Query hooks for state management |
| `component/LearningPathIntegration.tsx` | Full-featured path selector & visualizer |

## API Endpoints

### Learning Paths
- `POST /api/v1/learning-paths/` - Create path
- `GET /api/v1/learning-paths/` - List paths (with pagination)
- `GET /api/v1/learning-paths/{id}` - Get single path (with optional `include_kg=true`)
- `PUT /api/v1/learning-paths/{id}` - Update path
- `DELETE /api/v1/learning-paths/{id}` - Delete path

### Concepts
- `GET /api/v1/concepts/` - List all concepts
- `POST /api/v1/concepts/` - Create concept
- `GET /api/v1/concepts/{id}` - Get concept
- `GET /api/v1/concepts/{id}/prerequisites` - Get prerequisites

### Test
- `POST /api/v1/learning-paths/test/parse-and-save` - Parse and save learning path

## API Functions

```typescript
// Learning Paths
createLearningPath(params: LearningPathCreate)
getAllLearningPaths(skip?: number, limit?: number)
getLearningPath(id: number, includeKg?: boolean)
updateLearningPath(id: number, params: LearningPathUpdate)
deleteLearningPath(id: number)

// Concepts
listConcepts()
createConcept(params: ConceptCreate)
getConcept(conceptId: string)
getConceptPrerequisites(conceptId: string)

// Test
testParseAndSaveLearningPath(params: TestParseRequest)
```

## React Query Hooks

### Learning Paths
```typescript
useLearningPath(id: number | null, includeKg?: boolean)
useLearningPaths(skip?: number, limit?: number)
useCreateLearningPath()
useUpdateLearningPath(id: number)
useDeleteLearningPath()
```

### Concepts
```typescript
useConcepts()
useConcept(conceptId: string | null)
useConceptPrerequisites(conceptId: string | null)
useCreateConcept()
```

### Test
```typescript
useTestParseAndSaveLearningPath()
```

## Component Usage

### Basic
```typescript
import LearningPathIntegration from '@/features/learning-path/component/LearningPathIntegration';

export default function Page() {
  return <LearningPathIntegration />;
}
```

### With Initial Selection
```typescript
<LearningPathIntegration initialPathId={23} />
```

### In Modal
```typescript
<Dialog open={open} maxWidth="lg">
  <LearningPathIntegration />
</Dialog>
```

## Component Features

✅ **Path Dropdown Selection** - MUI Select component for path selection  
✅ **Informative Menu Items** - Topic, ID, and creation date shown  
✅ **Path Details** - ID, user info, graph URI display  
✅ **Knowledge Graph** - Visualizes prerequisites and concept relationships  
✅ **Pagination** - Load 0-100 paths by default  
✅ **Error Handling** - Comprehensive error states  
✅ **Loading States** - Visual feedback during data fetch  
✅ **Caching** - 5-minute cache with React Query  
✅ **MUI Components** - Uses Alert, Select, CircularProgress, Typography, Stack, Box  

## Component Architecture

```
LearningPathIntegration (Main)
├── MUI FormControl + Select (path selection)
├── MUI Alert (info/error/status)
└── LearningPathVisualization (graph)
```

## Data Model

```typescript
type LearningPathResponse = {
  id: number;
  topic: string;
  user_id: number;
  graph_uri?: string;
  created_at: string;
  updated_at?: string;
  kg_data?: Record<string, unknown>;  // JSON-LD format
};
```

## Knowledge Graph Format

The `kg_data` is JSON-LD format with concepts and relationships:

```json
{
  "@id": "http://learnora.ai/ont#concept_id",
  "@type": ["http://learnora.ai/ont#Concept"],
  "http://learnora.ai/ont#label": [{"@value": "Concept Name"}],
  "http://learnora.ai/ont#hasPrerequisite": [
    {"@id": "http://learnora.ai/ont#prereq_id"}
  ]
}
```

## Usage Examples

### Creating a Learning Path
```typescript
const { mutate } = useCreateLearningPath();

mutate({
  topic: "Python Programming",
  user_id: 1,
  graph_uri: "http://example.com/path"
});
```

### Fetching Paths
```typescript
const { data: paths, isLoading } = useLearningPaths(0, 20);
```

### Updating a Path
```typescript
const { mutate } = useUpdateLearningPath(pathId);
mutate({ topic: "Advanced Python" });
```

### Getting Path with KG
```typescript
const { data: pathWithKG } = useLearningPath(23, true);
// kg_data includes full knowledge graph
```

## Styling

- **MUI Components** - Alert, Select, CircularProgress, Typography, Stack, Box
- **Minimal Inline Styles** - Only spacing via `sx` prop
- **No Custom CSS** - Pure MUI styling
- **Responsive:** Flexbox layout via MUI

## Performance

- **Caching:** 5-minute stale time
- **Deduplication:** React Query prevents duplicate requests
- **Lazy Loading:** Selected path only fetches when ID is set
- **Pagination:** Supports any skip/limit combination

## Error Handling

| Scenario | Display |
|----------|---------|
| Loading paths fails | Red error box |
| Loading selected path fails | Error in visualization area |
| No paths available | Empty state message |
| No KG data | Info message suggesting `include_kg=true` |

## Authentication

All endpoints require OAuth2 Bearer token. Automatically handled by `apiClient` from `baseClient.ts`.

## Type Definitions

All types in `types.ts`:
- `LearningPathCreate` - Request to create path
- `LearningPathUpdate` - Request to update path
- `LearningPathResponse` - Path data response
- `ConceptCreate` - Request to create concept
- `ConceptResponse` - Concept data response
- `TestParseRequest` - Test endpoint request

## Troubleshooting

**No data loads:**
- Check API is running
- Verify auth token valid
- Check network tab in DevTools

**Graph not rendering:**
- Verify `kg_data` exists in response
- Check `LearningPathVisualization` component
- Use `include_kg=true` in query

**Selection not working:**
- Check React DevTools for state
- Verify `useLearningPath` enabled
- Look for console errors

## Next Steps

- [ ] Integrate into main application page
- [ ] Add search/filter functionality
- [ ] Implement path creation form
- [ ] Add path editing capabilities
- [ ] Build unit tests
- [ ] Add E2E tests

## Related Files

- `learningPathService.ts` - Service layer (optional)
- `component/README.md` - Visualization component docs
- `component/LearningPathVisualization.tsx` - Graph visualization
- Agent feature (`features/agent/`) - Similar pattern reference

## Query Keys

Used for cache management:
```typescript
learningPathKeys.all           // ['learningPaths']
learningPathKeys.lists()       // ['learningPaths', 'list']
learningPathKeys.list(s, l)    // [..., { skip, limit }]
learningPathKeys.detail(id)    // ['learningPaths', 'detail', id]

conceptKeys.all                // ['concepts']
conceptKeys.lists()            // ['concepts', 'list']
conceptKeys.detail(id)         // ['concepts', 'detail', id]
```

## Cache Configuration

```typescript
// All queries use these settings:
staleTime: 5 * 60 * 1000        // 5 minutes
refetchOnWindowFocus: true
refetchOnReconnect: true
enabled: <conditional>           // For lazy queries
```

## Summary

A complete, production-ready implementation with:
- ✅ Type-safe TypeScript
- ✅ Automatic caching via React Query
- ✅ Full CRUD operations
- ✅ Knowledge graph visualization
- ✅ User-friendly UI component
- ✅ Comprehensive error handling
- ✅ Clean, maintainable code

Ready to integrate into the main application immediately.
