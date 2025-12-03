import { Handle, Position } from '@xyflow/react';
import { Box, Typography } from '@mui/material';
import { EmojiEvents as GoalIcon } from '@mui/icons-material';
import type { FlowNodeData } from '../../types';

interface GoalNodeProps {
  data: FlowNodeData;
}

export default function GoalNode({ data }: Readonly<GoalNodeProps>) {
  return (
    <>
      <Handle type="target" position={Position.Left} />
      
      <Box
        sx={{
          minWidth: 200,
          maxWidth: 250,
          padding: '16px 20px',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        //   background: '#949bd5ff',
          border: '3px solid #5a67d8',
          borderRadius: '16px',
        //   boxShadow: '0 8px 16px rgba(102, 126, 234, 0.3), 0 0 0 4px rgba(102, 126, 234, 0.1)',
          display: 'flex',
          alignItems: 'center',
          gap: 1.5,
          position: 'relative',
        //   '&::before': {
        //     content: '""',
        //     position: 'absolute',
        //     top: -2,
        //     left: -2,
        //     right: -2,
        //     bottom: -2,
        //     background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        //     borderRadius: '16px',
        //     opacity: 0.3,
        //     filter: 'blur(8px)',
        //     zIndex: -1,
        //   },
        }}
      >
        <GoalIcon 
          sx={{ 
            fontSize: 32, 
            color: '#ffd700',
            filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.3))',
          }} 
        />
        <Box sx={{ flex: 1 }}>
          <Typography
            variant="caption"
            sx={{
              color: 'rgba(255, 255, 255, 0.9)',
              fontWeight: 600,
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
              fontSize: '0.65rem',
              display: 'block',
              mb: 0.5,
            }}
          >
            Goal
          </Typography>
          <Typography
            variant="body1"
            sx={{
              color: '#ffffff',
              fontWeight: 700,
              wordBreak: 'break-word',
              lineHeight: 1.3,
            }}
          >
            {data.label}
          </Typography>
        </Box>
      </Box>
      
      <Handle type="source" position={Position.Right} />
    </>
  );
}
