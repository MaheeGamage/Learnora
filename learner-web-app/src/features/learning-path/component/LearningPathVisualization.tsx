import { useEffect, useMemo } from "react";
import Graph from "graphology";
import { SigmaContainer, useLoadGraph, useRegisterEvents } from "@react-sigma/core";
import forceAtlas2 from "graphology-layout-forceatlas2";
import FA2Layout from "graphology-layout-forceatlas2/worker";
import type { JsonLdDocument } from "jsonld";
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
                let globalId = 0;

                /**
                 * Adds a node to the graph from JSON-LD item
                 */
                // eslint-disable-next-line @typescript-eslint/no-explicit-any
                const addNode = (item: any): string => {
                    globalId++;
                    const subjectId =
                        typeof item === "object"
                            ? item["@id"] || item["@value"] || `${item["@type"]}#${globalId}`
                            : `${item}`;

                    graph.mergeNode(subjectId, {
                        x: Math.random(),
                        y: Math.random(),
                        size: 10,
                        label: subjectId,
                        color: "#FA4F40",
                    });

                    return `${subjectId}`;
                };

                /**
                 * Adds edges to the graph from JSON-LD item
                 */
                // eslint-disable-next-line @typescript-eslint/no-explicit-any
                const addEdges = (item: any, subjectId: string) => {
                    if (typeof item !== "object" || !("@type" in item)) return;

                    for (const [predicate, objects] of Object.entries(item)) {
                        if (predicate.startsWith("@")) continue;

                        if (Array.isArray(objects)) {
                            for (const obj of objects) {
                                if (obj !== null) {
                                    const objectId = parseJsonLdExtended(obj);
                                    graph.addDirectedEdge(subjectId, objectId, {
                                        type: "arrow",
                                        label: predicate,
                                    });
                                }
                            }
                        }
                    }
                };

                /**
                 * Recursive function that parses the extended JSON-LD structure
                 * and builds the graph.
                 */
                // eslint-disable-next-line @typescript-eslint/no-explicit-any
                const parseJsonLdExtended = (item: any): string => {
                    const subjectId = addNode(item);
                    addEdges(item, subjectId);
                    return subjectId;
                };

                // Dynamically import jsonld to avoid build issues
                const jsonldModule = await import("jsonld");
                const jsonld = jsonldModule.default;

                // Expand the JSON-LD to a full RDF graph
                const expanded = await jsonld.expand(jsonldData);
                for (const item of expanded) {
                    parseJsonLdExtended(item);
                }

                // Apply ForceAtlas2 layout
                const sensibleSettings = forceAtlas2.inferSettings(graph);
                const fa2Layout = new FA2Layout(graph, {
                    settings: sensibleSettings,
                });

                fa2Layout.start();

                // Stop layout after some time
                setTimeout(() => {
                    fa2Layout.stop();
                    fa2Layout.kill();
                }, 3000);

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

    return (
        <SigmaContainer style={style} settings={{ renderEdgeLabels: true }}>
            <LoadGraph jsonldData={jsonldData} />
        </SigmaContainer>
    );
};

export default LearningPathVisualization;