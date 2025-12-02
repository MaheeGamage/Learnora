# Feed Generation Implementation Plan

## Analysis Summary

### Content Discovery Module Overview

The content-discovery module has **two main approaches** for fetching content:

#### 1. **Search-Based Approach** (`searchContent`)
- **Primary Function**: `searchContent(request, token)`
- **Features**:
  - Multiple search strategies: `bm25`, `dense`, `hybrid`
  - Auto-discovery: Can automatically crawl and index new content if no results found
  - NLP Analysis: Extracts intent, entities, and key terms
  - **Personalization**: Can generate personalized summaries, TLDRs, key takeaways, and highlights
  - Discovery sources: YouTube, Medium, GitHub
- **Use Case**: When user actively searches for specific topics/concepts
- **Returns**: `SearchResponse` with `SearchResultItem[]` (includes relevance scores and personalization data)

#### 2. **Pre-Indexed Content Approach**
- **Functions**:
  - `getAllContent(skip, limit, token)` - Get all indexed content (paginated)
  - `getContentById(contentId, token)` - Get specific content item
  - `getRecommendations(token)` - Get recommended content (currently returns recent 6 items)
- **Use Case**: Display existing indexed content without active search
- **Returns**: `LearningContent[]` or single `LearningContent`

### Supporting Services

#### Preferences Service
- `getPreferences(token)` - Get user's learning preferences
- `updatePreferences(updates, token)` - Update preferences
- `trackInteraction(interaction, token)` - Track content interactions
- `getLearningInsights(token)` - Get user's learning stats

#### Interaction Types
- `viewed`, `clicked`, `completed`, `bookmarked`, `shared`, `rated`

---

## Feed Generation Implementation Plan

### Option 1: Search-Based Feed (Recommended for Ready Concepts)

**Approach**: Use selected ready concepts as search queries to find relevant content

#### Implementation Steps:

1. **Map Concepts to Queries**
   - Convert selected concept labels into search queries
   - Example: Concept "Python Basics" → Query "Python Basics tutorial"

2. **Execute Parallel Searches**
   - For each selected concept, call `searchContent()` with:
     - `query`: concept label
     - `strategy`: 'hybrid' (best results)
     - `top_k`: 2-3 items per concept
     - `personalize`: true
     - `auto_discover`: true (discover new content if needed)
     - `use_nlp`: true

3. **Aggregate Results**
   - Combine results from all concept searches
   - Remove duplicates (same content appearing for multiple concepts)
   - Sort by relevance_score or personalization_boost
   - Tag each result with the concept(s) it matches

4. **Convert to Feed Items**
   - Map `SearchResultItem` → `FeedContent`
   - Include personalized summaries and key takeaways
   - Add concept tags for filtering

#### Pros:
✅ Automatically finds relevant content for each concept
✅ Includes personalization (summaries, TLDRs, highlights)
✅ Auto-discovery can find new content
✅ High relevance through search ranking
✅ Supports NLP intent detection

#### Cons:
❌ Requires API call for each concept (can be slow with many concepts)
❌ Depends on content being indexed/discoverable
❌ May return duplicate content for related concepts

---

### Option 2: Pre-Indexed Content with Filtering

**Approach**: Fetch all indexed content and filter by concept tags/keywords

#### Implementation Steps:

1. **Fetch All Content**
   - Call `getAllContent(0, limit, token)` once
   - Cache results in component state

2. **Filter by Concept Relevance**
   - For each content item, check if:
     - Tags match concept labels
     - Title/description contains concept keywords
     - Prerequisites match concept prerequisites

3. **Score and Sort**
   - Score each item by:
     - Number of matched concepts
     - User preferences alignment
     - Content difficulty vs concept level
   - Sort by score descending

4. **Convert to Feed Items**
   - Map filtered `LearningContent[]` → `FeedContent[]`
   - No personalization (unless added separately)

#### Pros:
✅ Single API call (fast)
✅ Works offline with cached data
✅ Simple filtering logic
✅ No duplicate handling needed

#### Cons:
❌ Limited to already indexed content
❌ No personalization features
❌ May miss relevant content not yet indexed
❌ Filtering logic can be complex and inaccurate

---

### Option 3: Hybrid Approach (Best of Both)

**Approach**: Combine pre-indexed content with targeted searches for selected concepts

#### Implementation Steps:

1. **Initial Load**: Fetch recommendations/recent content
   - Use `getRecommendations(token)` for baseline feed
   - Display immediately while searches execute

2. **Concept-Based Search**: When concepts selected
   - Execute parallel searches for selected concepts
   - Limit to 2 items per concept to avoid overwhelming
   - Use `strategy: 'hybrid'` with `personalize: true`

3. **Merge Results**
   - Combine recommendations + search results
   - Deduplicate by content ID
   - Sort by: concept match → relevance → personalization boost

4. **Progressive Loading**
   - Show recommendations immediately
   - Add search results as they arrive
   - Show loading indicators per concept

#### Pros:
✅ Fast initial load
✅ Personalized results for selected concepts
✅ Best of both worlds
✅ Progressive enhancement

#### Cons:
❌ More complex implementation
❌ Need to handle multiple loading states
❌ Cache invalidation complexity

---

## Recommended Implementation: **Hybrid Approach**

### Phase 1: Basic Feed (Quick Win)
```typescript
// 1. Show recommendations on load (no concepts selected)
const feedItems = await getRecommendations(token);

// 2. Display in Feed component
```

### Phase 2: Concept-Based Search (Core Feature)
```typescript
// When user selects concepts:
const searches = selectedConcepts.map(concept => 
  searchContent({
    query: concept.label,
    strategy: 'hybrid',
    top_k: 2,
    personalize: true,
    auto_discover: true,
    use_nlp: true,
  }, token)
);

const results = await Promise.all(searches);
const feedItems = results
  .flatMap(r => r.results)
  .filter(uniqueById)
  .map(toFeedContent);
```

### Phase 3: Preferences Integration
```typescript
// Use user preferences to further personalize:
const preferences = await getPreferences(token);

// Filter by preferred_formats, preferred_difficulty, available_time_daily
// Boost content matching knowledge_areas and learning_goals
```

### Phase 4: Interaction Tracking
```typescript
// Track when user clicks/views content from feed:
await trackInteraction({
  content_id: item.id,
  interaction_type: 'clicked',
  content_title: item.title,
  // ... other metadata
}, token);

// Use insights to improve future recommendations
```

---

## Data Flow Diagram

```
User Selects Concepts
    ↓
Feed Component
    ↓
┌─────────────────┬──────────────────┐
│  Recommendations │  Concept Searches │
│  (instant)       │  (on selection)   │
└─────────────────┴──────────────────┘
    ↓                     ↓
    └──── Merge & Dedupe ────┘
              ↓
    ┌────────────────────┐
    │ Sort by Relevance   │
    │ + Personalization   │
    └────────────────────┘
              ↓
    ┌────────────────────┐
    │ Convert to Feed     │
    │ Items               │
    └────────────────────┘
              ↓
        Display Cards
```

---

## Type Mapping

### SearchResultItem → FeedContent
```typescript
{
  id: result.content.id,
  type: 'content',
  title: result.content.title,
  description: result.personalized_summary || result.content.description,
  source: result.content.source,
  url: result.content.url,
  imageUrl: undefined, // Add if available in metadata
  topic: selectedConcept.label,
  readTime: `${result.estimated_time || result.content.duration_minutes} min`,
  publishedDate: result.content.created_at,
}
```

---

## Next Steps

1. ✅ **Confirm approach** with user
2. Create feed service functions:
   - `generateFeedFromConcepts(concepts, token)`
   - `getFeedRecommendations(token)`
   - `mergeFeedResults(recommendations, searchResults)`
3. Implement in Feed component
4. Add loading states and error handling
5. Integrate interaction tracking
6. Add preferences-based filtering (optional)

