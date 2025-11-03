# Demo Chat Window Usage Guide

## Overview

The `DemoChatWindow` component simulates AI responses for testing and demonstration purposes without needing a backend connection.

## What It Does

When enabled, `DemoChatWindow`:

1. **Accepts user input** - Type messages and click send (or press Enter)
2. **Shows typing indicator** - Displays animated dots while "thinking"
3. **Simulates network delay** - Waits 1-2 seconds before responding
4. **Generates responses** - Returns random demo messages
5. **Stores history** - Keeps all messages in conversation history
6. **Maintains state** - Conversation persists as you interact

## Usage

### Current Implementation (Dashboard)

The dashboard already uses `DemoChatWindow`:

```tsx
<ChatPanelWrapper 
  defaultOpen={true} 
  width={350}
  chatComponent={<DemoChatWindow agentTitle="Learning AI Agent" enableDemo={true} />}
>
```

### Basic Usage

```tsx
import { DemoChatWindow } from '@/common/components/DemoChatWindow';

// In your component
<DemoChatWindow 
  agentTitle="My Assistant"
  enableDemo={true}
/>
```

### Props

```typescript
interface DemoChatWindowProps {
  agentTitle?: string;    // Title shown at top (default: "Learning AI Agent")
  enableDemo?: boolean;   // Enable/disable demo mode (default: true)
}
```

## Features

### Welcome Message
The chat starts with a welcome message from the AI agent to get you started.

### Demo Responses
The component uses 8 different pre-written responses that are randomly selected:
- "That's an interesting question! Let me help you with that."
- "I understand what you mean. Here are some suggestions..."
- "Great! Let me provide you with more information on this topic."
- "I can help you explore this further. What specific aspect interests you?"
- "That makes sense. Based on what you said, I recommend..."
- "Interesting perspective! Let me share some insights..."
- "I appreciate the question. Here's what I found..."
- "Absolutely! Let me help you understand this better."

### Simulated Delays
- Each response takes 1-2 seconds to appear
- Typing indicator shows during this delay
- Simulates realistic conversation flow

## Testing the Implementation

### What to Test

1. ✅ **Send Messages**
   - Type a message
   - Press Enter or click Send button
   - Message appears on right side in blue

2. ✅ **Receive Responses**
   - After 1-2 seconds, a response appears
   - Response on left side in gray
   - Different random response each time

3. ✅ **Typing Indicator**
   - Watch for animated dots while waiting
   - Indicator disappears when response arrives

4. ✅ **Conversation History**
   - All messages stay visible
   - Scroll through long conversations
   - Messages auto-scroll to latest

5. ✅ **UI Elements**
   - Avatar icons for user and agent
   - Timestamps on messages
   - Rounded message bubbles
   - Input field and send button

6. ✅ **Panel Controls**
   - Close button hides chat panel
   - Floating button appears when closed
   - Floating button opens panel again
   - Smooth animations

## Switching to Real Backend

When you're ready to use a real AI backend, replace `DemoChatWindow` with `ChatWindow`:

### Before (Demo)
```tsx
<DemoChatWindow agentTitle="Learning AI Agent" enableDemo={true} />
```

### After (Production)
```tsx
import { ChatWindow, type ChatMessage } from '@/common/components/ChatWindow';
import { useState } from 'react';

function MyProductionChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async (userMessage: string) => {
    // Add user message
    const userMsg: ChatMessage = {
      id: `msg-${Date.now()}`,
      sender: 'user',
      text: userMessage,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMsg]);

    // Call your backend API
    setIsLoading(true);
    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        body: JSON.stringify({ message: userMessage }),
      });
      const data = await response.json();

      const assistantMsg: ChatMessage = {
        id: `msg-${Date.now()}`,
        sender: 'assistant',
        text: data.response,
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

// Then in your layout:
<ChatPanelWrapper chatComponent={<MyProductionChat />}>
```

## Customizing Demo Responses

Edit `DemoChatWindow.tsx` to add more demo responses:

```tsx
const DEMO_RESPONSES = [
  "Your custom response here...",
  "Another response...",
  // Add more as needed
];
```

## Troubleshooting

### Message not appearing?
- Make sure the input field is not empty
- Check that the Send button is enabled
- Try pressing Enter instead of clicking Send

### No typing indicator?
- The delay is 1-2 seconds - wait a moment
- Check console for any errors

### Chat panel not visible?
- Click the floating chat button in bottom-right
- Make sure `defaultOpen={true}` in ChatPanelWrapper

### Responses always the same?
- They're randomly selected from the list
- Keep talking to see variety
- Add more responses to the DEMO_RESPONSES array

## Next Steps

1. ✅ Test the current demo implementation
2. ✅ Verify all UI elements work as expected
3. ✅ Check responsiveness on mobile/tablet
4. ✅ When ready, replace with real backend integration
5. ✅ Deploy to production
