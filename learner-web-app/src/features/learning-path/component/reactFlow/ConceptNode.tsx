import { Handle, Position, NodeToolbar } from '@xyflow/react';
import { Box, Typography, Button } from '@mui/material';
import { useNavigate } from 'react-router';
import type { FlowNodeData } from '../../types';
import { useLearningPathContext } from '../../../../hooks/useLearningPathContext';
import { generateEvaluateUrl } from '../../../evaluate/utils/urlUtils';
import { getConceptStatusStyle } from '../../utils/conceptStatusStyle';

interface ConceptNodeProps {
  data: FlowNodeData;
}

export default function ConceptNode({ data }: Readonly<ConceptNodeProps>) {
  const statusStyle = getConceptStatusStyle(data.status);
  const { activeLearningPath } = useLearningPathContext();
  const navigate = useNavigate();

  const handleEvaluate = () => {
    if (activeLearningPath?.id && data.concept?.id) {
      const url = generateEvaluateUrl(activeLearningPath.id, data.concept.id);
      navigate(url);
    }
  };

  return (
    <>
      <NodeToolbar
        isVisible={data.forceToolbarVisible as boolean | undefined}
        position={data.toolbarPosition as Position | undefined}
        align={data.align as 'start' | 'center' | 'end' | undefined}
      >
        <Button variant="contained" size="small" onClick={handleEvaluate}>Evaluate</Button>
        <Button variant="contained" size="small"
          onClick={() => {
            console.log(data)
          }}
        >Content</Button>
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
