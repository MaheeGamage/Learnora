# Chat Components Documentation

This document describes the chat component system used in Learnora.

## Component Architecture

The chat system consists of three main components with clear separation of concerns:

### 1. **ChatPanel** (`ChatPanel.tsx`)
**Purpose:** UI wrapper component for the chat panel
**Responsibility:** Layout and visibility management

- Provides persistent drawer on the right side
- Manages open/closed state
- Shows floating action button when closed
- Customizable width and default state

**Props:**
- `defaultOpen?: boolean` - Panel starts open/closed (default: true)
- `width?: number` - Panel width in pixels (default: 350)
- `chatComponent?: ReactNode` - The chat component to display
- `title?: string` - Header title (default: "Chat Panel")
- `children: ReactNode` - Main content (required for wrapper)

### 2. **ChatWindow** (`ChatWindow.tsx`)
**Purpose:** Pure UI chat component
**Responsibility:** Display and user interaction for chat

- Display chat messages with timestamps
- User input field with send button
- Typing indicator for loading state
- Auto-scroll to latest messages
- Message bubble styling (user vs assistant)
- Avatar icons for visual distinction

**Props:**
```typescript
interface ChatWindowProps {
  agentTitle?: string;           // Title of the chatbot (default: "AI Agent")
  messages?: ChatMessage[];      // Array of messages to display
  onSendMessage?: (message: string) => void;  // Callback when user sends message
  isLoading?: boolean;           // Show typing indicator (default: false)
}
```

**Message Interface:**
```typescript
interface ChatMessage {
  id: string;                    // Unique identifier
  sender: 'user' | 'assistant'; // Who sent the message
  text: string;                  // Message content
  timestamp?: Date;              // When message was sent
}
```

### 3. **ChatPanel Wrapper** (in `ChatPanel.tsx`)
**Purpose:** Combines layout and content
**Responsibility:** Integrate panel with page content

Used in layouts to wrap main content with chat panel on the right side.

## Usage Examples

### Basic Usage (In Layout)

```tsx
import { ChatPanelWrapper } from '@/common/components/ChatPanel';
import { ChatWindow } from '@/common/components/ChatWindow';

export function MainDashboardLayout() {
  return (
    <DashboardLayout>
      <ChatPanelWrapper 
        defaultOpen={true}
        width={350}
        chatComponent={<ChatWindow agentTitle="Learning AI Agent" />}
      >
        <PageContainer>
          <Outlet />
        </PageContainer>
      </ChatPanelWrapper>
    </DashboardLayout>
  );
}
```

### With Chat Logic

```tsx
import { useState } from 'react';
import { ChatWindow, type ChatMessage } from '@/common/components/ChatWindow';

function MyChatComponent() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async (text: string) => {
    // Add user message
    const userMsg: ChatMessage = {
      id: `msg-${Date.now()}`,
      sender: 'user',
      text,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMsg]);

    // Call your API
    setIsLoading(true);
    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        body: JSON.stringify({ message: text }),
      });
      const data = await response.json();

      // Add assistant message
      const assistantMsg: ChatMessage = {
        id: `msg-${Date.now()}`,
        sender: 'assistant',
        text: data.reply,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, assistantMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <ChatWindow
      agentTitle="Learning AI Agent"
      messages={messages}
      onSendMessage={handleSendMessage}
      isLoading={isLoading}
    />
  );
}
```

### In Single Page

```tsx
import { ChatPanelWrapper } from '@/common/components/ChatPanel';
import { ChatWindow } from '@/common/components/ChatWindow';

export function MyPage() {
  return (
    <ChatPanelWrapper 
      defaultOpen={false}
      width={400}
      chatComponent={<ChatWindow agentTitle="Page Assistant" />}
      title="Page Help"
    >
      <div>
        <h1>My Page Content</h1>
        <p>Content here...</p>
      </div>
    </ChatPanelWrapper>
  );
}
```

## Features

### ✅ Message Display
- Messages styled as bubbles with rounded corners
- Different styling for user (right, blue) vs assistant (left, gray)
- Time stamps on each message
- Avatar icons for visual distinction

### ✅ User Input
- Multi-line text input with character wrapping
- Send button that's disabled when input is empty
- Enter key to send (Shift+Enter for new line)
- Clears input after sending

### ✅ Auto-scroll
- Automatically scrolls to latest message
- Smooth scroll animation
- Works with typing indicator

### ✅ Loading State
- Animated typing indicator
- Shows when AI is thinking/responding
- Input disabled during loading

### ✅ Empty State
- Friendly message when no messages yet
- Prompts user to start conversation

### ✅ Responsive
- Full width on mobile
- Fixed width on desktop
- Drawer slides from right

## Customization

### Change Panel Width
```tsx
<ChatPanelWrapper width={400}>
```

### Customize Chat Title
```tsx
<ChatWindow agentTitle="My Custom Assistant" />
```

### Custom Styling
Since components use MUI Theme, customize via your theme:
```tsx
const theme = createTheme({
  palette: {
    primary: { main: '#your-color' },
  },
});
```

## Component Isolation Benefits

1. **ChatPanel** - Pure layout, can be reused for any side panel
2. **ChatWindow** - Pure UI, can be used anywhere (page, modal, etc.)
3. **ChatPanelWrapper** - Combines the two for common layout pattern
4. **Easy to extend** - Add features to ChatWindow without touching layout
5. **Easy to replace** - Swap ChatWindow with different component
6. **Easy to test** - Each component has clear input/output

## Future Enhancements

Potential features to add:
- Message attachments (files, images)
- Rich text formatting
- Emoji picker
- Message search
- Clear history button
- Settings for chat behavior
- Dark mode adjustments
