/**
 * Configuration constants for Learning Path Graph Visualization
 */

export const GRAPH_CONFIG = {
    // Node Types
    NODE_TYPES: {
        GOAL: "http://learnora.ai/ont#Goal",
        CONCEPT: "http://learnora.ai/ont#Concept",
        LEARNING_PATH: "http://learnora.ai/ont#LearningPath",
    },

    // Predicates
    PREDICATES: {
        HAS_PREREQUISITE: "http://learnora.ai/ont#hasPrerequisite",
        HAS_GOAL: "http://learnora.ai/ont#hasGoal",
        INCLUDES_CONCEPT: "http://learnora.ai/ont#includesConcept",
        LABEL: "http://learnora.ai/ont#label",
    },

    // Visual Styling
    COLORS: {
        GOAL: "#4CAF50", // Green for goals
        CONCEPT: "#2196F3", // Blue for concepts
        CONCEPT_NO_PREREQ: "#FF9800", // Orange for concepts without prerequisites
        LEARNING_PATH: "#9C27B0", // Purple for learning path
        EDGE: "#666666", // Gray for edges
    },

    // Node Sizes
    SIZES: {
        GOAL: 20,
        CONCEPT: 12,
        CONCEPT_NO_PREREQ: 15,
        LEARNING_PATH: 25,
    },

    // Layout Settings
    LAYOUT: {
        // Horizontal spacing between levels
        LEVEL_SPACING: 350,
        // Vertical spacing between nodes at same level
        NODE_SPACING: 120,
        // Starting X position for leftmost nodes
        START_X: 100,
        // Starting Y position
        START_Y: 300,
        // Padding around labels to prevent overlap
        LABEL_PADDING: 20,
        // ForceAtlas2 duration in milliseconds
        FA2_DURATION: 2000,
    },

    // Label Settings
    LABEL: {
        SIZE: 14,
        WEIGHT: "normal" as const,
        COLOR: "#000000",
        FONT: "Arial, sans-serif",
        // Maximum label length before truncation
        MAX_LENGTH: 50,
    },

    // ForceAtlas2 Settings Override
    FA2_SETTINGS: {
        barnesHutOptimize: true,
        strongGravityMode: true,
        gravity: 0.05,
        scalingRatio: 10,
        slowDown: 1.5,
    },
} as const;

/**
 * MCQ Evaluation Configuration
 */
export const MCQ_CONFIG = {
    // Minimum score percentage to update knowledge graph
    PASSING_SCORE_THRESHOLD: 50,
    
    // Ontology predicates for KG updates
    ONTOLOGY_PREDICATES: {
        KNOWS: "http://learnora.ai/ont#knows",
    },
} as const;

export type NodeType = typeof GRAPH_CONFIG.NODE_TYPES[keyof typeof GRAPH_CONFIG.NODE_TYPES];
