# Learning Path Visualization Improvements

**Date**: November 11, 2025  
**Component**: `learner-web-app/src/features/learning-path/component/LearningPathVisualization.tsx`  
**Issue**: Label overlap and poor readability in graph visualization

## Problem Statement

The learning path graph visualization had significant usability issues:
- Node labels were overlapping, making text unreadable
- Random node positioning created visual clutter
- No clear visual hierarchy (goals vs concepts vs prerequisites)
- Lack of left-to-right flow for learning progression

## Solution Overview

Implemented a hierarchical left-to-right layout algorithm with improved spacing, color coding, and configurability.

## Key Changes

### 1. Hierarchical Layout Algorithm

**File**: `LearningPathVisualization.tsx`

- Implemented topological sorting using DFS to calculate node levels
- **Left-to-right flow**:
  - Level 0 (leftmost): Concepts without prerequisites (entry points)
  - Middle levels: Concepts with dependencies
  - Highest level (rightmost): Goals
- **Vertical centering**: Nodes at each level are centered around a midpoint for balanced distribution

### 2. Visual Differentiation

**Color Coding**:
- 🟢 Green (`#4CAF50`): Goals - learning objectives
- 🔵 Blue (`#2196F3`): Concepts with prerequisites
- 🟠 Orange (`#FF9800`): Concepts without prerequisites (starting points)
- 🟣 Purple (`#9C27B0`): Learning Path nodes

**Size Coding**:
- Goals: 20px (largest)
- Entry concepts: 15px (medium-large)
- Regular concepts: 12px (medium)

### 3. Overlap Prevention

**Spacing Improvements**:
- Horizontal spacing: 350px between levels (increased from 200px)
- Vertical spacing: 120px between nodes (increased from 100px)
- Vertical centering algorithm distributes nodes evenly

**Label Management**:
- Automatic truncation at 50 characters with "..." suffix
- Disabled edge labels to reduce clutter
- Increased label grid cell size to 200px for collision detection
- Always-visible labels for consistency

### 4. Configuration System

**New File**: `graphConstants.ts`

Centralized all configuration in a type-safe constant object:

```typescript
export const GRAPH_CONFIG = {
    NODE_TYPES: { /* ... */ },
    PREDICATES: { /* ... */ },
    COLORS: { /* ... */ },
    SIZES: { /* ... */ },
    LAYOUT: {
        LEVEL_SPACING: 350,
        NODE_SPACING: 120,
        START_X: 100,
        START_Y: 300,
    },
    LABEL: {
        SIZE: 14,
        FONT: "Arial, sans-serif",
        MAX_LENGTH: 50,
    },
}
```

Benefits:
- Single source of truth for all visual parameters
- Easy customization without modifying core logic
- Type-safe constants using TypeScript

## Technical Implementation

### Algorithm Flow

1. **Metadata Collection**: Parse JSON-LD and extract node information (type, label, prerequisites)
2. **Level Calculation**: DFS traversal to compute depth in dependency tree
3. **Positioning**: Calculate x,y coordinates based on level and vertical centering
4. **Rendering**: Create graph with nodes and directed edges

### Code Structure

- `getLabel()`: Extracts and truncates labels from JSON-LD
- `getNodeColor()`: Determines color based on node type
- `getNodeSize()`: Determines size based on node type
- `collectNodeMetadata()`: First-pass data extraction
- `calculateNodeLevels()`: Topological sort implementation
- `addNodesToGraph()`: Positioning and node creation
- `addEdgesToGraph()`: Edge creation from prerequisites

## Files Modified

1. **LearningPathVisualization.tsx** - Complete rewrite of graph building logic
2. **graphConstants.ts** (new) - Centralized configuration
3. **README.md** (new) - Component documentation

## Results

- ✅ No overlapping labels
- ✅ Clear left-to-right learning progression
- ✅ Visual hierarchy (color + size coding)
- ✅ Easily configurable layout
- ✅ Better readability and user experience

## Future Enhancements

Potential improvements for consideration:
- Interactive node tooltips with full label text
- Zoom-to-fit functionality
- Export graph as image
- Highlight critical path to goal
- Filter by concept difficulty/level
- Animated transitions when updating the graph
