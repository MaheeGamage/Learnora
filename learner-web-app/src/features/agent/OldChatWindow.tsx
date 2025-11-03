import * as React from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  AppBar,
  Toolbar,
  List,
  ListItem,
  ListItemText,
  Avatar,
  Stack,
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import { faker } from '@faker-js/faker';

interface Message {
  id: string;
  sender: 'user' | 'agent';
  text: string;
  timestamp: string;
}

const generateInitialMessages = (): Message[] => {
  const messages: Message[] = [];
  for (let i = 0; i < 5; i++) {
    messages.push({
      id: faker.string.uuid(),
      sender: i % 2 === 0 ? 'agent' : 'user',
      text: faker.lorem.sentence({ min: 5, max: 15 }),
      timestamp: faker.date.recent().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    });
  }
  return messages;
};

const agentName = faker.person.firstName();
const agentAvatar = faker.image.avatar();

export default function AgentChatWindow() {
  const [messages, setMessages] = React.useState<Message[]>(generateInitialMessages());
  const [newMessage, setNewMessage] = React.useState('');
  const messagesEndRef = React.useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  React.useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = () => {
    if (newMessage.trim()) {
      const newMsg: Message = {
        id: faker.string.uuid(),
        sender: 'user',
        text: newMessage.trim(),
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prevMessages) => [...prevMessages, newMsg]);
      setNewMessage('');

      // Simulate agent response after a short delay
      setTimeout(() => {
        const agentResponse: Message = {
          id: faker.string.uuid(),
          sender: 'agent',
          text: faker.lorem.sentence({ min: 5, max: 15 }),
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        };
        setMessages((prevMessages) => [...prevMessages, agentResponse]);
      }, 1000);
    }
  };

  return (
    <Paper
      elevation={5}
      sx={{
        // position: 'fixed',
        // right: 0,
        // top: 0,
        height: '60vh',
        // width: { xs: '100%', sm: '400px', md: '450px' },
        // display: 'flex',
        // flexDirection: 'column',
        // bgcolor: 'background.paper',
        // borderLeft: '1px solid',
        // borderColor: 'divider',
        // zIndex: 1200, // Ensure it's above other content
        boxShadow: '0px 0px 15px rgba(0, 0, 0, 0.1)',
      }}
    >
      <AppBar color="primary" elevation={0} sx={{ borderBottom: '1px solid', borderColor: 'divider' }}>
        <Toolbar>
          <Avatar src={agentAvatar} alt={agentName} sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            {agentName} (Agent)
          </Typography>
        </Toolbar>
      </AppBar>

      <List sx={{ flexGrow: 1, overflowY: 'auto', p: 2 }}>
        {messages.map((message) => (
          <ListItem
            key={message.id}
            sx={{
              justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start',
              p: 0, // Remove default padding to control spacing with Stack
              mb: 1,
            }}
          >
            <Stack
              direction="column"
              alignItems={message.sender === 'user' ? 'flex-end' : 'flex-start'}
              sx={{
                maxWidth: '80%',
                bgcolor: message.sender === 'user' ? 'primary.light' : 'grey.200',
                color: message.sender === 'user' ? 'primary.contrastText' : 'text.primary',
                borderRadius: '12px',
                p: 1.5,
                wordBreak: 'break-word',
                boxShadow: '0px 2px 4px rgba(0, 0, 0, 0.05)',
              }}
            >
              <ListItemText
                primary={message.text}
                primaryTypographyProps={{ variant: 'body2' }}
                sx={{ m: 0 }}
              />
              <Typography variant="caption" sx={{ color: message.sender === 'user' ? 'rgba(255,255,255,0.7)' : 'text.secondary', mt: 0.5 }}>
                {message.timestamp}
              </Typography>
            </Stack>
          </ListItem>
        ))}
        <div ref={messagesEndRef} />
      </List>

      <Box
        sx={{
          p: 2,
          borderTop: '1px solid',
          borderColor: 'divider',
          display: 'flex',
          gap: 1,
          alignItems: 'center',
          bgcolor: 'background.paper',
        }}
      >
        <TextField
          fullWidth
          variant="outlined"
          size="small"
          placeholder="Type a message..."
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          onKeyPress={(e) => {
            if (e.key === 'Enter') {
              handleSendMessage();
            }
          }}
          sx={{ '& .MuiOutlinedInput-root': { borderRadius: '25px' } }}
        />
        <Button
          variant="contained"
          endIcon={<SendIcon />}
          onClick={handleSendMessage}
          sx={{ borderRadius: '25px', minWidth: 'auto', p: '8px 16px' }}
        >
          Send
        </Button>
      </Box>
    </Paper>
  );
}