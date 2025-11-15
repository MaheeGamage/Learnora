import { Handle, Position, NodeToolbar } from '@xyflow/react';
import { Box, Typography, Button } from '@mui/material';
import type { FlowNodeData } from '../../types';

interface ConceptNodeProps {
  data: FlowNodeData;
}

const getStatusStyle = (status?: 'known' | 'ready' | 'locked') => {
  switch (status) {
    case 'known':
      return {
        borderColor: '#4caf50',
        backgroundColor: '#e8f5e9',
        icon: '✓',
      };
    case 'ready':
      return {
        borderColor: '#2196f3',
        backgroundColor: '#e3f2fd',
        icon: '🔓',
      };
    case 'locked':
      return {
        borderColor: '#f44336',
        backgroundColor: '#ffebee',
        icon: '🔒',
      };
    default:
      return {
        borderColor: '#e0e0e0',
        backgroundColor: '#ffffff',
        icon: '',
      };
  }
};

export default function ConceptNode({ data }: Readonly<ConceptNodeProps>) {
  const statusStyle = getStatusStyle(data.status);

  return (
    <>
      <NodeToolbar
        isVisible={data.forceToolbarVisible as boolean | undefined}
        position={data.toolbarPosition as Position | undefined}
        align={data.align as 'start' | 'center' | 'end' | undefined}
      >
        <Button variant="contained" size="small">Evaluate</Button>
        <Button variant="contained" size="small">Content</Button>
      </NodeToolbar>
      
      <Handle type="target" position={Position.Left} />
      
      <Box
        sx={{
        //   minWidth: 150,
          maxWidth: 180,
          padding: '8px 12px',
          backgroundColor: statusStyle.backgroundColor,
          border: `2px solid ${statusStyle.borderColor}`,
          borderRadius: '8px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.12)',
          display: 'flex',
          alignItems: 'center',
          gap: 1,
        }}
      >
        <Typography
        //   variant="body2"
          sx={{
            // fontWeight: data.status === 'ready' ? 600 : 400,
            wordBreak: 'break-word',
            lineHeight: 1.4,
          }}
        >
          {data.label}
        </Typography>
      </Box>
      
      <Handle type="source" position={Position.Right} />
    </>
  );
}
