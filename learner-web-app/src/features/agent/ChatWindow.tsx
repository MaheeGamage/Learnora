import { useState, useRef, useEffect, type ReactNode } from 'react';
import {
  Box,
  TextField,
  IconButton,
  Typography,
  Paper,
  Stack,
  Avatar,
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import PersonIcon from '@mui/icons-material/Person';
import ReactMarkdown from 'react-markdown';

export interface ChatMessage {
  readonly id: string;
  readonly sender: 'user' | 'assistant';
  readonly text: string;
  readonly timestamp?: Date;
}

export interface ChatWindowProps {
  readonly agentTitle?: string;
  readonly messages?: ChatMessage[];
  readonly onSendMessage?: (message: string) => void;
  readonly isLoading?: boolean;
}

// Message bubble component
function MessageBubble({
  message,
  isUser,
}: {
  readonly message: ChatMessage;
  readonly isUser: boolean;
}) {
  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: isUser ? 'flex-end' : 'flex-start',
        mb: 2,
        gap: 1,
      }}
    >
      {!isUser && (
        <Avatar
          sx={{
            bgcolor: 'primary.main',
            width: 32,
            height: 32,
            flexShrink: 0,
          }}
        >
          <SmartToyIcon sx={{ fontSize: 18 }} />
        </Avatar>
      )}

      <Paper
        sx={{
          px: 2,
          py: 1,
          maxWidth: '80%',
          bgcolor: isUser ? 'primary.main' : 'action.hover',
          color: isUser ? 'primary.contrastText' : 'text.primary',
          borderRadius: isUser
            ? '18px 18px 4px 18px'
            : '18px 18px 18px 4px',
          wordWrap: 'break-word',
          overflowWrap: 'break-word',
        }}
      >
        <Box
          sx={{
            '& p': {
              margin: 0,
              marginBottom: '0.5em',
              fontSize: '0.875rem',
              lineHeight: 1.43,
              '&:last-child': {
                marginBottom: 0,
              },
            },
            '& strong': {
              fontWeight: 700,
            },
            '& em': {
              fontStyle: 'italic',
            },
            '& code': {
              bgcolor: isUser ? 'rgba(0, 0, 0, 0.1)' : 'rgba(0, 0, 0, 0.05)',
              padding: '2px 4px',
              borderRadius: '3px',
              fontSize: '0.85em',
              fontFamily: 'monospace',
            },
            '& pre': {
              bgcolor: isUser ? 'rgba(0, 0, 0, 0.1)' : 'rgba(0, 0, 0, 0.05)',
              padding: '8px',
              borderRadius: '4px',
              overflow: 'auto',
              margin: '0.5em 0',
              '& code': {
                bgcolor: 'transparent',
                padding: 0,
              },
            },
            '& ul, & ol': {
              marginTop: '0.5em',
              marginBottom: '0.5em',
              paddingLeft: '1.5em',
            },
            '& li': {
              marginBottom: '0.25em',
              fontSize: '0.875rem',
              lineHeight: 1.43,
            },
            '& a': {
              color: isUser ? 'inherit' : 'primary.main',
              textDecoration: 'underline',
            },
            '& h1, & h2, & h3, & h4, & h5, & h6': {
              marginTop: '0.5em',
              marginBottom: '0.5em',
              fontWeight: 600,
              '&:first-child': {
                marginTop: 0,
              },
            },
            '& blockquote': {
              borderLeft: '3px solid',
              borderColor: isUser ? 'rgba(255, 255, 255, 0.3)' : 'divider',
              paddingLeft: '1em',
              marginLeft: 0,
              marginTop: '0.5em',
              marginBottom: '0.5em',
            },
          }}
        >
          <ReactMarkdown>{message.text}</ReactMarkdown>
        </Box>
        {message.timestamp && (
          <Typography
            variant="caption"
            sx={{
              mt: 0.5,
              display: 'block',
              opacity: 0.7,
            }}
          >
            {message.timestamp.toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </Typography>
        )}
      </Paper>

      {isUser && (
        <Avatar
          sx={{
            bgcolor: 'secondary.main',
            width: 32,
            height: 32,
            flexShrink: 0,
          }}
        >
          <PersonIcon sx={{ fontSize: 18 }} />
        </Avatar>
      )}
    </Box>
  );
}

// Typing indicator component
function TypingIndicator() {
  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        gap: 1,
        mb: 2,
      }}
    >
      <Avatar
        sx={{
          bgcolor: 'primary.main',
          width: 32,
          height: 32,
        }}
      >
        <SmartToyIcon sx={{ fontSize: 18 }} />
      </Avatar>
      <Paper
        sx={{
          px: 2,
          py: 1.5,
          bgcolor: 'action.hover',
          borderRadius: '18px 18px 18px 4px',
        }}
      >
        <Box sx={{ display: 'flex', gap: 0.5 }}>
          {[0, 1, 2].map((i) => (
            <Box
              key={i}
              sx={{
                width: 8,
                height: 8,
                borderRadius: '50%',
                bgcolor: 'text.secondary',
                animation: 'bounce 1.4s infinite',
                animationDelay: `${i * 0.2}s`,
                '@keyframes bounce': {
                  '0%, 80%, 100%': { opacity: 0.5 },
                  '40%': { opacity: 1 },
                },
              }}
            />
          ))}
        </Box>
      </Paper>
    </Box>
  );
}

// Main chat component
export function ChatWindow({
  agentTitle = 'AI Agent',
  messages = [],
  onSendMessage,
  isLoading = false,
}: ChatWindowProps): ReactNode {
  const [inputValue, setInputValue] = useState('');
  const [localMessages, setLocalMessages] = useState<ChatMessage[]>(messages);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Sync external messages prop
  useEffect(() => {
    setLocalMessages(messages);
  }, [messages]);

  // Auto scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [localMessages, isLoading]);

  const handleSendMessage = () => {
    if (inputValue.trim()) {
      const userMessage: ChatMessage = {
        id: `msg-${Date.now()}`,
        sender: 'user',
        text: inputValue,
        timestamp: new Date(),
      };

      setLocalMessages((prev) => [...prev, userMessage]);
      onSendMessage?.(inputValue);
      setInputValue('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <Box
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        position: 'relative',
      }}
    >
      {/* Header */}
      <Box sx={{ pb: 2, borderBottom: '1px solid', borderColor: 'divider' }}>
        <Stack direction="row" spacing={1} alignItems="center">
          <Avatar
            sx={{
              width: 40,
              height: 40,
              bgcolor: 'primary.main',
            }}
          >
            <SmartToyIcon />
          </Avatar>
          <Box>
            <Typography variant="subtitle2" fontWeight={600}>
              {agentTitle}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Online
            </Typography>
          </Box>
        </Stack>
      </Box>

      {/* Messages Area */}
      <Box
        sx={{
          flexGrow: 1,
          overflowY: 'auto',
          py: 2,
          px: 1,
          display: 'flex',
          flexDirection: 'column',
          '&::-webkit-scrollbar': {
            width: '6px',
          },
          '&::-webkit-scrollbar-track': {
            bgcolor: 'action.hover',
          },
          '&::-webkit-scrollbar-thumb': {
            bgcolor: 'action.disabled',
            borderRadius: '3px',
            '&:hover': {
              bgcolor: 'action.active',
            },
          },
        }}
      >
        {localMessages.length === 0 ? (
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              height: '100%',
              gap: 2,
            }}
          >
            <SmartToyIcon
              sx={{
                fontSize: 48,
                color: 'action.disabled',
              }}
            />
            <Typography variant="body2" color="text.secondary" align="center">
              Start a conversation with {agentTitle}
            </Typography>
          </Box>
        ) : (
          <>
            {localMessages.map((msg) => (
              <MessageBubble
                key={msg.id}
                message={msg}
                isUser={msg.sender === 'user'}
              />
            ))}
            {isLoading && <TypingIndicator />}
            <div ref={messagesEndRef} />
          </>
        )}
      </Box>

      {/* Input Area */}
      <Box sx={{ pt: 2, borderTop: '1px solid', borderColor: 'divider' }}>
        <Stack direction="row" spacing={1} alignItems="flex-end">
          <TextField
            fullWidth
            multiline
            maxRows={4}
            minRows={1}
            placeholder="Type a message..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isLoading}
            variant="outlined"
            size="small"
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: '20px',
              },
            }}
          />
          <IconButton
            onClick={handleSendMessage}
            disabled={!inputValue.trim() || isLoading}
            sx={{
              bgcolor: 'primary.main',
              color: 'primary.contrastText',
              '&:hover': {
                bgcolor: 'primary.dark',
              },
              '&:disabled': {
                bgcolor: 'action.disabled',
                color: 'action.disabledBackground',
              },
            }}
          >
            <SendIcon />
          </IconButton>
        </Stack>
      </Box>
    </Box>
  );
}
