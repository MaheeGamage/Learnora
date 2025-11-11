import { useEffect, useMemo } from "react";
import Graph from "graphology";
import { SigmaContainer, useLoadGraph, useRegisterEvents } from "@react-sigma/core";
import type { JsonLdDocument } from "jsonld";
import { GRAPH_CONFIG } from "../constant";
import "@react-sigma/core/lib/style.css";

interface LearningPathVisualizationProps {
    jsonldData: JsonLdDocument | JsonLdDocument[] | null;
    height?: string;
    width?: string;
}

interface LoadGraphProps {
    jsonldData: JsonLdDocument | JsonLdDocument[] | null;
}

// Component that loads the graph from JSON-LD
export const LoadGraph: React.FC<LoadGraphProps> = ({ jsonldData }) => {
    const loadGraph = useLoadGraph();
    const registerEvents = useRegisterEvents();

    useEffect(() => {
        if (!jsonldData) return;

        const buildGraph = async () => {
            try {
                const graph = new Graph({ type: "directed", multi: true });
                
                // Maps to store node metadata
                const nodeMetadata = new Map<string, { type: string; label: string; prerequisites: string[] }>();
                
                /**
                 * Extracts label from JSON-LD item
                 */
                // eslint-disable-next-line @typescript-eslint/no-explicit-any
                const getLabel = (item: any): string => {
                    if (typeof item !== "object") return String(item);
                    
                    // Check for label property
                    const labelValue = item[GRAPH_CONFIG.PREDICATES.LABEL];
                    let label = "";
                    
                    if (Array.isArray(labelValue) && labelValue.length > 0) {
                        label = labelValue[0]["@value"] || labelValue[0];
                    } else {
                        // Fallback to @id with cleaning
                        const id = item["@id"] || "";
                        label = id.split("#").pop()?.replace(/_/g, " ") || id;
                    }
                    
                    // Truncate long labels to prevent overlap
                    if (label.length > GRAPH_CONFIG.LABEL.MAX_LENGTH) {
                        return label.substring(0, GRAPH_CONFIG.LABEL.MAX_LENGTH - 3) + "...";
                    }
                    
                    return label;
                };

                /**
                 * Determines node color based on type and prerequisites
                 */
                const getNodeColor = (nodeType: string, hasPrerequisites: boolean): string => {
                    if (nodeType === GRAPH_CONFIG.NODE_TYPES.GOAL) {
                        return GRAPH_CONFIG.COLORS.GOAL;
                    } else if (nodeType === GRAPH_CONFIG.NODE_TYPES.CONCEPT) {
                        return hasPrerequisites 
                            ? GRAPH_CONFIG.COLORS.CONCEPT 
                            : GRAPH_CONFIG.COLORS.CONCEPT_NO_PREREQ;
                    } else if (nodeType === GRAPH_CONFIG.NODE_TYPES.LEARNING_PATH) {
                        return GRAPH_CONFIG.COLORS.LEARNING_PATH;
                    }
                    return GRAPH_CONFIG.COLORS.CONCEPT;
                };

                /**
                 * Determines node size based on type and prerequisites
                 */
                const getNodeSize = (nodeType: string, hasPrerequisites: boolean): number => {
                    if (nodeType === GRAPH_CONFIG.NODE_TYPES.GOAL) {
                        return GRAPH_CONFIG.SIZES.GOAL;
                    } else if (nodeType === GRAPH_CONFIG.NODE_TYPES.CONCEPT) {
                        return hasPrerequisites 
                            ? GRAPH_CONFIG.SIZES.CONCEPT 
                            : GRAPH_CONFIG.SIZES.CONCEPT_NO_PREREQ;
                    } else if (nodeType === GRAPH_CONFIG.NODE_TYPES.LEARNING_PATH) {
                        return GRAPH_CONFIG.SIZES.LEARNING_PATH;
                    }
                    return GRAPH_CONFIG.SIZES.CONCEPT;
                };

                /**
                 * First pass: Collect all nodes and their metadata
                 */
                // eslint-disable-next-line @typescript-eslint/no-explicit-any
                const collectNodeMetadata = (item: any) => {
                    if (typeof item !== "object" || !item["@id"]) return;

                    const nodeId = item["@id"];
                    const nodeTypes = Array.isArray(item["@type"]) ? item["@type"] : [item["@type"]];
                    const nodeType = nodeTypes[0] || "";
                    const label = getLabel(item);
                    
                    // Extract prerequisites
                    const prerequisites: string[] = [];
                    const prereqValue = item[GRAPH_CONFIG.PREDICATES.HAS_PREREQUISITE];
                    if (Array.isArray(prereqValue)) {
                        prereqValue.forEach((prereq) => {
                            if (typeof prereq === "object" && prereq["@id"]) {
                                prerequisites.push(prereq["@id"]);
                            }
                        });
                    }

                    nodeMetadata.set(nodeId, { type: nodeType, label, prerequisites });
                };

                /**
                 * Calculate node levels using topological sort (BFS)
                 * Leftmost nodes (level 0) have no prerequisites
                 * Rightmost nodes (highest level) are goals or have the most dependencies
                 */
                const calculateNodeLevels = (): Map<string, number> => {
                    const levels = new Map<string, number>();
                    
                    // Find all goal nodes - they should be at the rightmost position
                    const goalNodes: string[] = [];
                    nodeMetadata.forEach((metadata, nodeId) => {
                        if (metadata.type === GRAPH_CONFIG.NODE_TYPES.GOAL) {
                            goalNodes.push(nodeId);
                        }
                    });
                    
                    // Calculate levels using DFS from each node
                    const calculateLevel = (nodeId: string, visited: Set<string>): number => {
                        if (levels.has(nodeId)) return levels.get(nodeId)!;
                        if (visited.has(nodeId)) return 0; // Cycle detection
                        
                        const metadata = nodeMetadata.get(nodeId);
                        if (!metadata) return 0;
                        
                        if (metadata.prerequisites.length === 0) {
                            levels.set(nodeId, 0);
                            return 0;
                        }
                        
                        visited.add(nodeId);
                        let maxPrereqLevel = -1;
                        
                        for (const prereqId of metadata.prerequisites) {
                            const prereqLevel = calculateLevel(prereqId, visited);
                            maxPrereqLevel = Math.max(maxPrereqLevel, prereqLevel);
                        }
                        
                        visited.delete(nodeId);
                        const level = maxPrereqLevel + 1;
                        levels.set(nodeId, level);
                        return level;
                    };
                    
                    // Calculate levels for all nodes
                    nodeMetadata.forEach((_, nodeId) => {
                        calculateLevel(nodeId, new Set());
                    });
                    
                    // Set goals to the highest level + 1
                    const maxLevel = Math.max(...Array.from(levels.values()), 0);
                    goalNodes.forEach(goalId => {
                        levels.set(goalId, maxLevel + 1);
                    });
                    
                    return levels;
                };

                /**
                 * Add nodes to graph with calculated positions
                 */
                const addNodesToGraph = (levels: Map<string, number>) => {
                    // Group nodes by level
                    const nodesByLevel = new Map<number, string[]>();
                    levels.forEach((level, nodeId) => {
                        if (!nodesByLevel.has(level)) {
                            nodesByLevel.set(level, []);
                        }
                        nodesByLevel.get(level)!.push(nodeId);
                    });

                    // Add nodes with calculated positions, centered vertically per level
                    nodesByLevel.forEach((nodeIds, level) => {
                        const nodesInLevel = nodeIds.length;
                        // Calculate total height needed for this level
                        const totalHeight = (nodesInLevel - 1) * GRAPH_CONFIG.LAYOUT.NODE_SPACING;
                        // Start Y position to center the nodes vertically
                        const startY = GRAPH_CONFIG.LAYOUT.START_Y - (totalHeight / 2);
                        
                        nodeIds.forEach((nodeId, index) => {
                            const metadata = nodeMetadata.get(nodeId);
                            if (!metadata) return;

                            const hasPrerequisites = metadata.prerequisites.length > 0;
                            const x = GRAPH_CONFIG.LAYOUT.START_X + (level * GRAPH_CONFIG.LAYOUT.LEVEL_SPACING);
                            const y = startY + (index * GRAPH_CONFIG.LAYOUT.NODE_SPACING);

                            graph.addNode(nodeId, {
                                x,
                                y,
                                size: getNodeSize(metadata.type, hasPrerequisites),
                                label: metadata.label,
                                color: getNodeColor(metadata.type, hasPrerequisites),
                            });
                        });
                    });
                };

                /**
                 * Add edges to graph
                 */
                const addEdgesToGraph = () => {
                    nodeMetadata.forEach((metadata, nodeId) => {
                        // Add prerequisite edges
                        metadata.prerequisites.forEach((prereqId) => {
                            if (graph.hasNode(prereqId) && graph.hasNode(nodeId)) {
                                try {
                                    graph.addDirectedEdge(prereqId, nodeId, {
                                        type: "arrow",
                                        size: 2,
                                        color: GRAPH_CONFIG.COLORS.EDGE,
                                    });
                                } catch (e) {
                                    // Edge might already exist in multi-graph
                                    console.warn("Edge already exists:", prereqId, "->", nodeId);
                                }
                            }
                        });
                    });
                };

                // Dynamically import jsonld to avoid build issues
                const jsonldModule = await import("jsonld");
                const jsonld = jsonldModule.default;

                // Expand the JSON-LD to a full RDF graph
                const expanded = await jsonld.expand(jsonldData);
                
                // First pass: collect all node metadata
                for (const item of expanded) {
                    collectNodeMetadata(item);
                }

                // Calculate node levels for left-to-right layout
                const levels = calculateNodeLevels();

                // Add nodes to graph with positions
                addNodesToGraph(levels);

                // Add edges
                addEdgesToGraph();

                loadGraph(graph);
            } catch (error) {
                console.error("Error processing JSON-LD:", error);
            }
        };

        buildGraph();
    }, [jsonldData, loadGraph]);

    useEffect(() => {
        registerEvents({
            clickNode: (event) => {
                console.log("Node clicked:", event.node);
            },
        });
    }, [registerEvents]);

    return null;
};

const LearningPathVisualization: React.FC<LearningPathVisualizationProps> = ({
    jsonldData,
    height = "500px",
    width = "100%",
}) => {
    const style = useMemo(() => ({ height, width }), [height, width]);

    const sigmaSettings = useMemo(() => ({
        renderEdgeLabels: false, // Disable edge labels to reduce clutter
        labelSize: GRAPH_CONFIG.LABEL.SIZE,
        labelWeight: GRAPH_CONFIG.LABEL.WEIGHT,
        labelColor: { color: GRAPH_CONFIG.LABEL.COLOR },
        defaultNodeColor: "#999999",
        defaultEdgeColor: "#cccccc",
        labelRenderedSizeThreshold: 0, // Always show labels
        enableEdgeEvents: false,
        // Improve label rendering
        labelFont: GRAPH_CONFIG.LABEL.FONT,
        labelGridCellSize: 200, // Increase grid cell size for better label spacing
    }), []);

    return (
        <SigmaContainer style={style} settings={sigmaSettings}>
            <LoadGraph jsonldData={jsonldData} />
        </SigmaContainer>
    );
};

export default LearningPathVisualization;