# Chat Component Implementation Transition Guide

## Overview

This guide shows how to transition from the demo chat to a production chat connected to your backend API.

## Current Architecture

```
Dashboard (Layout)
└── ChatPanelWrapper (UI Container)
    └── DemoChatWindow (Simulates AI)
        └── ChatWindow (Pure UI)
```

## Three Implementation Approaches

### 1. Demo Mode (Current - for testing)

**File:** `DemoChatWindow.tsx`

```tsx
import { DemoChatWindow } from '@/common/components/DemoChatWindow';

<ChatPanelWrapper 
  chatComponent={<DemoChatWindow agentTitle="Learning AI Agent" />}
>
```

**Pros:**
- No backend needed
- Quick testing
- Works offline
- Good for UI verification

**Cons:**
- Random responses only
- No real AI interaction
- Not production-ready

---

### 2. Custom Hook with Backend (Recommended for Production)

**File:** `useAgentChat.ts`

```typescript
import { useState, useCallback } from 'react';
import { ChatMessage } from '@/common/components/ChatWindow';

export interface UseAgentChatOptions {
  agentTitle?: string;
  apiEndpoint?: string;
}

export function useAgentChat(options: UseAgentChatOptions = {}) {
  const {
    agentTitle = 'Learning AI Agent',
    apiEndpoint = '/api/chat',
  } = options;

  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome',
      sender: 'assistant',
      text: `Hello! I'm ${agentTitle}. How can I help you today?`,
      timestamp: new Date(),
    },
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(async (userText: string) => {
    // Add user message
    const userMessage: ChatMessage = {
      id: `msg-user-${Date.now()}`,
      sender: 'user',
      text: userText,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(apiEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userText,
          conversationId: 'user-123', // Add user/session context as needed
        }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
      }

      const data = await response.json();

      // Add assistant message
      const assistantMessage: ChatMessage = {
        id: `msg-assistant-${Date.now()}`,
        sender: 'assistant',
        text: data.response || data.text || 'I could not generate a response.',
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMessage);

      // Optionally add error message to chat
      const errorChatMessage: ChatMessage = {
        id: `msg-error-${Date.now()}`,
        sender: 'assistant',
        text: `Sorry, I encountered an error: ${errorMessage}. Please try again.`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorChatMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [apiEndpoint]);

  return {
    messages,
    isLoading,
    error,
    sendMessage,
  };
}
```

**Usage in Component:**

```tsx
import { ChatWindow } from '@/common/components/ChatWindow';
import { useAgentChat } from '@/common/hooks/useAgentChat';

function ProductionChatComponent() {
  const { messages, isLoading, error, sendMessage } = useAgentChat({
    agentTitle: 'Learning AI Agent',
    apiEndpoint: '/api/v1/chat', // Your backend endpoint
  });

  return (
    <ChatWindow
      agentTitle="Learning AI Agent"
      messages={messages}
      onSendMessage={sendMessage}
      isLoading={isLoading}
    />
  );
}
```

**Usage in Dashboard:**

```tsx
import { ChatPanelWrapper } from '@/common/components/ChatPanel';
import ProductionChatComponent from '@/common/components/ProductionChatComponent';

<ChatPanelWrapper 
  chatComponent={<ProductionChatComponent />}
>
```

---

### 3. Feature-Toggle Between Demo and Production

**File:** `dashboard.tsx` with conditional rendering

```tsx
import { DemoChatWindow } from '@/common/components/DemoChatWindow';
import ProductionChatComponent from '@/common/components/ProductionChatComponent';

export default function MainDashboardLayout() {
  // Toggle via environment or config
  const USE_DEMO = import.meta.env.MODE === 'development';

  const ChatComponent = USE_DEMO 
    ? DemoChatWindow 
    : ProductionChatComponent;

  return (
    <DashboardLayout>
      <ChatPanelWrapper 
        chatComponent={<ChatComponent agentTitle="Learning AI Agent" />}
      >
        {/* Main content */}
      </ChatPanelWrapper>
    </DashboardLayout>
  );
}
```

---

## Migration Steps (Demo → Production)

### Step 1: Create Backend API

Your backend should handle POST requests:

```
POST /api/chat
Content-Type: application/json

{
  "message": "What is machine learning?",
  "conversationId": "user-123"
}

Response:
{
  "response": "Machine learning is a subset of AI...",
  "conversationId": "user-123"
}
```

### Step 2: Create Production Component

Create `ProductionChatComponent.tsx`:

```tsx
import { ChatWindow } from '@/common/components/ChatWindow';
import { useAgentChat } from '@/common/hooks/useAgentChat';

export function ProductionChatComponent() {
  const { messages, isLoading, sendMessage } = useAgentChat({
    apiEndpoint: '/api/chat',
  });

  return (
    <ChatWindow
      agentTitle="Learning AI Agent"
      messages={messages}
      onSendMessage={sendMessage}
      isLoading={isLoading}
    />
  );
}

export default ProductionChatComponent;
```

### Step 3: Update Dashboard

```tsx
// Change this:
import { DemoChatWindow } from '@/common/components/DemoChatWindow';

// To this:
import ProductionChatComponent from '@/common/components/ProductionChatComponent';

// And update the usage:
<ChatPanelWrapper 
  chatComponent={<ProductionChatComponent />}
>
```

### Step 4: Test

1. Verify API endpoint is accessible
2. Test message sending
3. Check response display
4. Verify error handling
5. Test long conversations

---

## File Structure for Production

```
src/
└── common/
    ├── components/
    │   ├── ChatPanel.tsx           (UI wrapper - unchanged)
    │   ├── ChatWindow.tsx          (Pure UI - unchanged)
    │   ├── DemoChatWindow.tsx      (Demo only - keep for testing)
    │   └── ProductionChatComponent.tsx  (Your production component)
    └── hooks/
        └── useAgentChat.ts         (Backend integration hook)
```

---

## Error Handling

The hook provides error state:

```tsx
const { messages, isLoading, error, sendMessage } = useAgentChat();

if (error) {
  console.error('Chat error:', error);
  // Handle error in UI
}
```

---

## Best Practices

1. **Keep ChatWindow pure** - No API calls, just UI
2. **Use custom hooks** - Handle API logic in hooks
3. **Type everything** - Use TypeScript interfaces
4. **Handle errors** - Show user-friendly messages
5. **Add loading states** - Typing indicator while waiting
6. **Cache messages** - Store conversation history locally
7. **User context** - Pass user ID in API requests
8. **Rate limiting** - Add debounce if needed

---

## Environment Variables

Add to `.env`:

```
VITE_API_URL=http://localhost:8000
VITE_CHAT_ENDPOINT=/api/chat
VITE_USE_DEMO=false
```

Usage in code:

```tsx
const apiEndpoint = `${import.meta.env.VITE_API_URL}${import.meta.env.VITE_CHAT_ENDPOINT}`;
const useDemo = import.meta.env.VITE_USE_DEMO === 'true';
```

---

## Testing Your Implementation

### Unit Tests

```typescript
import { renderHook, act } from '@testing-library/react';
import { useAgentChat } from './useAgentChat';

describe('useAgentChat', () => {
  it('should send message and receive response', async () => {
    const { result } = renderHook(() => useAgentChat());

    await act(async () => {
      await result.current.sendMessage('Hello');
    });

    expect(result.current.messages).toHaveLength(2); // Welcome + user message
  });
});
```

### Integration Tests

Test the complete flow from UI to backend and back.

---

## Summary

| Aspect | Demo | Production |
|--------|------|-----------|
| Component | `DemoChatWindow` | `ProductionChatComponent` |
| Backend | None | Your API |
| Setup Time | Instant | ~30 mins |
| Use Case | Testing/Demo | Live system |
| Transition | Keep both files | Replace import |

When ready to go production, simply replace the import and update your dashboard!
