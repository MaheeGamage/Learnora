# Evaluate Page URL Implementation Guide

## Overview
The evaluate page now supports a RESTful URL structure with learning path ID as a path parameter and concept ID as a query parameter. This enables deep linking, shareable URLs, and automatic pre-selection of learning paths and concepts.

## URL Structure

```
http://localhost:5173/evaluate/{learning-path-id}?conceptId={encoded-concept-id}
```

- `{learning-path-id}`: The numeric ID of the learning path (optional)
- `{encoded-concept-id}`: URL-encoded RDF concept ID (optional)

### Complete URL Example

```
http://localhost:5173/evaluate/42?conceptId=http%3A%2F%2Flearnora.ai%2Font%23named_entity_recognition_(ner)
```

In this example:
- Learning Path ID: `42`
- Concept ID: `http://learnora.ai/ont#named_entity_recognition_(ner)` (URL-encoded)

---

## Implementation Details

### 1. Route Configuration (`routes.ts`)

```typescript
route("/evaluate/:learningPathId?", "./pages/evaluate.tsx"),
```

The `?` makes the `learningPathId` parameter optional, allowing the route to handle both:
- `/evaluate` - Without learning path ID
- `/evaluate/42` - With learning path ID

### 2. Component Updates (`EvaluateIntegrator.tsx`)

**Hooks Used:**
- `useParams()` - Extract learning path ID from URL path
- `useSearchParams()` - Extract concept ID from query string
- `useLearningPathContext()` - Access and update learning path context

**Key Features:**
- Automatically sets active learning path when URL contains `learningPathId`
- Automatically pre-selects concept when URL contains `conceptId`
- Shows warning if URL learning path doesn't match active learning path
- Prompts user to select from side menu when no learning path is selected
- Proper URL decoding for RDF concept IDs

**Component Logic:**
```typescript
// Set active learning path based on URL parameter
useEffect(() => {
    if (learningPathId) {
        const pathId = Number.parseInt(learningPathId, 10);
        if (!Number.isNaN(pathId) && pathId !== activeLearningPath?.id) {
            setActiveLearningPath(pathId);
        }
    }
}, [learningPathId, activeLearningPath?.id, setActiveLearningPath]);

// Pre-select concept based on URL parameter
useEffect(() => {
    const conceptIdParam = searchParams.get('conceptId');
    
    if (conceptIdParam && activeLearningPath?.kg_data) {
        const decodedConceptId = decodeURIComponent(conceptIdParam);
        const concepts = extractConcepts(activeLearningPath.kg_data);
        const conceptToSelect = concepts.find(c => c.id === decodedConceptId);
        
        if (conceptToSelect) {
            setSelectedConcept(conceptToSelect);
        }
    }
}, [searchParams, activeLearningPath]);
```

### 3. URL Encoding for RDF Concept IDs

Since concept IDs are RDF URLs (e.g., `http://learnora.ai/ont#named_entity_recognition_(ner)`), they must be URL-encoded:

```typescript
const conceptId = "http://learnora.ai/ont#named_entity_recognition_(ner)";
const encodedConceptId = encodeURIComponent(conceptId);
// Result: http%3A%2F%2Flearnora.ai%2Font%23named_entity_recognition_(ner)
```

### 4. Utility Functions (`urlUtils.ts`)

Helper functions are provided for consistent URL generation:

```typescript
// Generate URL with both learning path and concept
generateEvaluateUrl(learningPathId: number, conceptId?: string): string

// Generate URL with only learning path
generateEvaluateUrlForPath(learningPathId: number): string

// Encode/decode concept IDs
encodeConceptId(conceptId: string): string
decodeConceptId(encodedConceptId: string): string
```

---

## Usage Scenarios

### 1. No Parameters (Manual Selection)
```
http://localhost:5173/evaluate
```
- User must select learning path from side menu
- User manually selects concept from dropdown

### 2. Learning Path Only
```
http://localhost:5173/evaluate/42
```
- Pre-selects learning path ID 42
- User manually selects concept from that path

### 3. Full Pre-selection
```
http://localhost:5173/evaluate/42?conceptId=http%3A%2F%2Flearnora.ai%2Font%23named_entity_recognition_(ner)
```
- Pre-selects both learning path and concept
- User can immediately start evaluation

---

## How to Navigate Programmatically

### Using the Utility Functions

```typescript
import { generateEvaluateUrl } from '../features/evaluate/utils/urlUtils';
import { useNavigate } from 'react-router';

function ConceptCard({ learningPathId, conceptId, conceptLabel }: Props) {
  const navigate = useNavigate();
  
  const handleEvaluateConcept = () => {
    const url = generateEvaluateUrl(learningPathId, conceptId);
    navigate(url);
  };
  
  return (
    <button onClick={handleEvaluateConcept}>
      Evaluate {conceptLabel}
    </button>
  );
}
```

### Manual URL Construction

```typescript
// With both learning path and concept
const learningPathId = 42;
const conceptId = "http://learnora.ai/ont#named_entity_recognition_(ner)";
const url = `/evaluate/${learningPathId}?conceptId=${encodeURIComponent(conceptId)}`;
navigate(url);

// With only learning path
navigate(`/evaluate/${learningPathId}`);

// No parameters
navigate('/evaluate');
```

### Creating Direct Links

```typescript
<a href={`/evaluate/${learningPathId}?conceptId=${encodeURIComponent(conceptId)}`}>
  Evaluate {conceptLabel}
</a>
```

### Example: Navigating from Learning Path Visualization

```typescript
// In ConceptNode.tsx (React Flow node component)
const { activeLearningPath } = useLearningPathContext();
const navigate = useNavigate();

const handleEvaluate = () => {
  if (activeLearningPath?.id && data.concept?.id) {
    const url = generateEvaluateUrl(activeLearningPath.id, data.concept.id);
    navigate(url);
  }
};

<Button onClick={handleEvaluate}>Evaluate</Button>
```

### Example: Multiple Concepts

```typescript
const LearningPathView = () => {
  const navigate = useNavigate();
  const learningPathId = 42;
  
  const concepts = [
    { id: "http://learnora.ai/ont#named_entity_recognition_(ner)", label: "NER" },
    { id: "http://learnora.ai/ont#tokenization", label: "Tokenization" }
  ];
  
  return (
    <div>
      {concepts.map(concept => (
        <button
          key={concept.id}
          onClick={() => {
            navigate(generateEvaluateUrl(learningPathId, concept.id));
          }}
        >
          Evaluate {concept.label}
        </button>
      ))}
    </div>
  );
};
```

---

## Benefits

### User Experience
- ✅ **Shareable Links**: Direct links to specific concept evaluations
- ✅ **Bookmarkable**: Users can bookmark evaluation pages
- ✅ **Better UX**: Automatic pre-selection reduces clicks
- ✅ **Deep Linking**: Navigate directly from any part of the application

### Technical
- ✅ **RESTful Design**: Clear resource hierarchy (`/evaluate/{resource}`)
- ✅ **State Management**: URL becomes source of truth, works well with browser history
- ✅ **Flexible**: Supports both programmatic and manual workflows
- ✅ **Context Integration**: Works seamlessly with `LearningPathContext`
- ✅ **Scalability**: Easy to add more parameters in the future

### Design
- ✅ **Hierarchical Structure**: URL clearly shows concepts belong to learning paths
- ✅ **Standards Compliant**: Follows REST API design best practices
- ✅ **Maintainable**: Utility functions provide consistent URL generation

---

## Error Handling

### URL and Context Mismatch
If the learning path ID in the URL doesn't match the active learning path in the context:

```
Warning: The learning path in the URL (ID: 42) doesn't match the active learning path (ID: 35). 
Please change the learning path from the side menu.
```

### No Learning Path Selected
If no learning path is selected:

```
Info: Please select a learning path from the side menu to evaluate concepts.
```

---

## Testing

### Test Cases

1. **Direct URL with both parameters**
   - Navigate to: `/evaluate/42?conceptId=http%3A%2F%2Flearnora.ai%2Font%23tokenization`
   - Expected: Learning path 42 is selected, Tokenization concept is pre-selected

2. **URL with only learning path**
   - Navigate to: `/evaluate/42`
   - Expected: Learning path 42 is selected, concept dropdown is shown

3. **URL without parameters**
   - Navigate to: `/evaluate`
   - Expected: Info message shown, user must select from side menu

4. **Mismatched learning path**
   - Active learning path: 35
   - Navigate to: `/evaluate/42?conceptId=...`
   - Expected: Warning message shown

5. **Invalid concept ID**
   - Navigate to: `/evaluate/42?conceptId=invalid_id`
   - Expected: Learning path selected, no concept pre-selected

---

## Migration Notes

### Previous Implementation
- Learning paths were only selectable via dropdown in the component
- No URL-based navigation support
- State was not shareable or bookmarkable

### Current Implementation
- Learning paths can be selected via side menu or URL
- Full URL-based navigation with optional parameters
- State is shareable and bookmarkable
- Backward compatible with manual selection

### Breaking Changes
None - the implementation is backward compatible. Users can still manually select learning paths from the side menu.
