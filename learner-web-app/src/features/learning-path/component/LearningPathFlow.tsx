import { useState, useCallback, useEffect } from 'react';
import {
  ReactFlow,
  addEdge,
  applyNodeChanges,
  applyEdgeChanges,
  type Node,
  type Edge,
  type OnConnect,
  type OnNodesChange,
  type OnEdgesChange,
  
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { jsonldToFlow, type FlowNodeData } from '../utils/jsonldToFlow';
import type { JsonLdDocument } from 'jsonld';

interface LearningPathFlowProps {
    jsonldData: JsonLdDocument | JsonLdDocument[] | null;
}
 
export default function LearningPathFlow({ jsonldData }: Readonly<LearningPathFlowProps>) {
  const [nodes, setNodes] = useState<Node<FlowNodeData>[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);

  useEffect(() => {
    if (!jsonldData) {
      setNodes([]);
      setEdges([]);
      return;
    }
    const { nodes, edges } = jsonldToFlow(Array.isArray(jsonldData) ? jsonldData : [jsonldData]);
    setNodes(nodes);
    setEdges(edges);
  }, [jsonldData]);
 
  const onNodesChange: OnNodesChange = useCallback(
    (changes) => setNodes((nds) => applyNodeChanges(changes, nds) as Node<FlowNodeData>[]),
    [setNodes],
  );
  const onEdgesChange: OnEdgesChange = useCallback(
    (changes) => setEdges((eds) => applyEdgeChanges(changes, eds)),
    [setEdges],
  );
  const onConnect: OnConnect = useCallback(
    (connection) => setEdges((eds) => addEdge(connection, eds)),
    [setEdges],
  );
 
  return (
    <div style={{ width: '100vw', height: '100vh' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        fitView
      />
    </div>
  );
}