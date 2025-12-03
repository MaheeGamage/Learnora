# Code Refactoring: Eliminating Duplication

## Overview
Refactored the learning path utilities to eliminate code duplication between `jsonldToFlow.ts` and `conceptStatusUtils.ts` by extracting shared logic into reusable utility functions.

## Changes Made

### 1. Created New Shared Utility File
**File:** `/learner-web-app/src/features/learning-path/utils/jsonldUtils.ts`

Extracted and consolidated the following duplicate functions:
- `getLocalId()` - Converts full URI to safe local ID
- `findLabel()` - Extracts label from JSON-LD item
- `isConceptOrGoal()` - Checks if item is a Concept or Goal type
- `parseType()` - Extracts type from JSON-LD item
- `parsePrerequisites()` - Parses prerequisite array from JSON-LD item
- `collectKnownConcepts()` - Collects known concepts from user data
- `determineConceptStatus()` - Determines concept status (known/ready/locked)
- `ConceptStatus` type - Exported for reuse

### 2. Created Status Style Utility
**File:** `/learner-web-app/src/features/learning-path/utils/conceptStatusStyle.ts`

Extracted status styling logic from `ConceptNode.tsx`:
- `getConceptStatusStyle()` - Returns border color, background color, and icon for each status
- `ConceptStatusStyle` interface - Type definition for style configuration

### 3. Refactored Existing Files

#### `conceptStatusUtils.ts`
- **Removed:** All duplicate utility functions (getLocalId, findLabel, isConceptOrGoal, parsePrereqs, collectKnownConcepts, determineStatus)
- **Added:** Import of shared utilities from `jsonldUtils.ts`
- **Updated:** Function calls to use shared utilities
- **Re-exported:** `ConceptStatus` type for backward compatibility

#### `jsonldToFlow.ts`
- **Removed:** All duplicate utility functions (getLocalId, findLabel, isConceptOrGoal, parseType, parsePrereqs, collectKnownConcepts, determineStatus)
- **Added:** Import of shared utilities from `jsonldUtils.ts`
- **Updated:** Function calls to use shared utilities
- **Simplified:** Status determination logic (removed local function, using shared)

#### `ConceptNode.tsx`
- **Removed:** Local `getStatusStyle()` function
- **Added:** Import of `getConceptStatusStyle` from shared utilities
- **Updated:** Uses shared styling function

### 4. Created Barrel Export
**File:** `/learner-web-app/src/features/learning-path/utils/index.ts`

Consolidated exports for easier imports:
```typescript
// All utilities can now be imported from a single location
import { 
  getLocalId, 
  extractReadyConcepts, 
  getConceptStatusStyle 
} from '../features/learning-path/utils';
```

## Benefits

1. **DRY Principle**: Eliminated ~150 lines of duplicated code
2. **Maintainability**: Changes to logic only need to be made in one place
3. **Consistency**: All components use the same status determination and styling logic
4. **Testability**: Shared utilities are easier to unit test
5. **Reusability**: New features can easily import and use these utilities
6. **Type Safety**: Shared types ensure consistency across the codebase

## File Structure
```
learning-path/
  utils/
    ├── index.ts                    (barrel export)
    ├── jsonldUtils.ts              (core JSON-LD parsing utilities)
    ├── conceptStatusUtils.ts       (concept status extraction)
    ├── conceptStatusStyle.ts       (UI styling utilities)
    └── jsonldToFlow.ts             (flow diagram conversion)
```

## No Breaking Changes
All existing imports and functionality remain intact. The refactoring is purely internal - external consumers of these utilities are not affected.
