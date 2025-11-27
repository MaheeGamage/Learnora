import { useState, type ReactNode } from 'react';
import { Drawer, Box, Typography, IconButton } from '@mui/material';
import ChatIcon from '@mui/icons-material/Chat';
import CloseIcon from '@mui/icons-material/Close';

interface ChatPanelProps {
  readonly defaultOpen?: boolean;
  readonly width?: number;
}

interface RightSidePanelProps {
  readonly open: boolean;
  readonly onClose: () => void;
  readonly width?: number;
  readonly chatComponent?: ReactNode;
  readonly title?: string;
}

function RightSidePanel({ open, onClose, width = 350, chatComponent, title = 'Chat Panel' }: RightSidePanelProps) {
  return (
    <Drawer
      anchor="right"
      open={open}
      onClose={onClose}
      variant="persistent"
      sx={{
        width: { xs: 0, sm: open ? width : 0 },
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: { xs: '100%', sm: width },
          boxSizing: 'border-box',
          top: 64, // Start below the toolbar on all screen sizes
          height: 'calc(100% - 64px)',
          borderLeft: '1px solid',
          borderColor: 'divider',
        },
      }}
    >
      <Box sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">{title}</Typography>
          <IconButton onClick={onClose} size="small" aria-label="close chat panel">
            <CloseIcon />
          </IconButton>
        </Box>
        <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', overflow: 'auto' }}>
          {chatComponent || (
            <Box sx={{ border: '1px dashed grey', borderRadius: 1, p: 2, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Typography variant="body2" color="text.secondary">
                Chat window content goes here...
              </Typography>
            </Box>
          )}
        </Box>
      </Box>
    </Drawer>
  );
}

export function ChatPanel({ defaultOpen = true, width = 350 }: ChatPanelProps) {
  const [rightPanelOpen, setRightPanelOpen] = useState(defaultOpen);

  return (
    <>
      <Box 
        sx={{ 
          flexGrow: 1, 
          transition: 'margin-right 0.3s',
          marginRight: { xs: 0, sm: rightPanelOpen ? `${width}px` : 0 },
        }}
      />
      
      <RightSidePanel 
        open={rightPanelOpen} 
        onClose={() => setRightPanelOpen(false)}
        width={width}
      />
      
      {/* Floating action button - only show when panel is closed */}
      {!rightPanelOpen && (
        <IconButton
          onClick={() => setRightPanelOpen(true)}
          sx={{
            position: 'fixed',
            bottom: 24,
            right: 24,
            bgcolor: 'primary.main',
            color: 'white',
            '&:hover': {
              bgcolor: 'primary.dark',
            },
            width: 56,
            height: 56,
            boxShadow: 3,
            zIndex: 1300,
          }}
          aria-label="open chat panel"
        >
          <ChatIcon />
        </IconButton>
      )}
    </>
  );
}

interface ChatPanelWrapperProps {
  readonly children: ReactNode;
  readonly defaultOpen?: boolean;
  readonly width?: number;
  readonly chatComponent?: ReactNode;
  readonly title?: string;
}

export function ChatPanelWrapper({ children, defaultOpen = true, width = 350, chatComponent, title = 'Chat Panel' }: ChatPanelWrapperProps) {
  const [rightPanelOpen, setRightPanelOpen] = useState(defaultOpen);

  return (
    <Box sx={{ display: 'flex', minHeight: '100%', position: 'relative' }}>
      <Box 
        sx={{ 
          flexGrow: 1, 
          transition: 'margin-right 0.3s',
          // marginRight: { xs: 0, sm: rightPanelOpen ? `${width}px` : 0 },
        }}
      >
        {children}
      </Box>
      
      <RightSidePanel 
        open={rightPanelOpen} 
        onClose={() => setRightPanelOpen(false)}
        width={width}
        chatComponent={chatComponent}
        title={title}
      />
      
      {/* Floating action button - only show when panel is closed */}
      {!rightPanelOpen && (
        <IconButton
          onClick={() => setRightPanelOpen(true)}
          sx={{
            position: 'fixed',
            bottom: 24,
            right: 24,
            bgcolor: 'primary.main',
            color: 'white',
            '&:hover': {
              bgcolor: 'primary.dark',
            },
            width: 56,
            height: 56,
            boxShadow: 3,
            zIndex: 1300,
          }}
          aria-label="open chat panel"
        >
          <ChatIcon />
        </IconButton>
      )}
    </Box>
  );
}
