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
  Background,
  Controls,

} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { jsonldToFlow } from '../utils/jsonldToFlow';
import type { FlowNodeData } from '../types';
import type { JsonLdDocument } from 'jsonld';
import { Box } from '@mui/material';
import ConceptNode from './reactFlow/ConceptNode';
import GoalNode from './reactFlow/GoalNode';

interface LearningPathFlowProps {
  jsonldData: JsonLdDocument | JsonLdDocument[] | null;
}

const nodeTypes = {
  'concept-node': ConceptNode,
  'goal-node': GoalNode,
};

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
    <Box sx={{ width: '100%', height: '50vh', border: '1px solid #ccc', borderRadius: '4px', position: 'relative' }}>
      {/* Legend */}
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        fitView
      >
        <Background />
        <Controls />
      </ReactFlow>
    </Box>
  );
}