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
  NodeToolbar,
  Handle,
  Position,
  
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { jsonldToFlow, type FlowNodeData } from '../utils/jsonldToFlow';
import type { JsonLdDocument } from 'jsonld';
import { Box, Button, Card, Chip, GlobalStyles } from '@mui/material';

interface LearningPathFlowProps {
    jsonldData: JsonLdDocument | JsonLdDocument[] | null;
}
 
function NodeWithToolbar({ data }) {
  return (
    <>
      <NodeToolbar
        isVisible={data.forceToolbarVisible || undefined}
        position={data.toolbarPosition}
        align={data.align}
      >
        <Button variant="contained">cut</Button>
        <Button variant="contained">copy</Button>
        <Button variant="contained">paste</Button>
      </NodeToolbar>
      {/* <Card variant="outlined" sx={{ padding: '4px', marginTop: '4px', backgroundColor: '#f5f5f5' }}>
        {data?.label}
      </Card> */}
      <Chip label={data?.label} variant="outlined" />
    </>
  );
}

const TextUpdaterNode = ({ data }) => {
  return (
    <div className="text-updater-node">
      <NodeToolbar
        isVisible={data.forceToolbarVisible || undefined}
        position={data.toolbarPosition}
        align={data.align}
      >
        <Button variant="contained">Evaluate</Button>
        <Button variant="contained">Content</Button>
      </NodeToolbar>
      <Handle type="target" position={Position.Left} />
      <div>{data.label}</div>
      <Handle type="source" position={Position.Right} />
    </div>
  );
};

const nodeTypes = {
  'node-with-toolbar': TextUpdaterNode,
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
    <Box sx={{ width: '100%', height: '40vh' }}>
      <GlobalStyles
        styles={{
          '.text-updater-node': {
            padding: '10px',
            border: '1px solid #ddd',
            background: '#fff',
            borderRadius: '3px',
          },
        }}
      />
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        fitView
      />
    </Box>
  );
}