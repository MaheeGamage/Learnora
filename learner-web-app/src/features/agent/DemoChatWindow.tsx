import { useState, useCallback, type ReactNode } from 'react';
import { ChatWindow, type ChatMessage } from './ChatWindow';

export interface DemoChatWindowProps {
  readonly agentTitle?: string;
  readonly enableDemo?: boolean;
}

// Simulated responses for demo mode
const DEMO_RESPONSES = [
  "That's an interesting question! Let me help you with that.",
  'I understand what you mean. Here are some suggestions...',
  'Great! Let me provide you with more information on this topic.',
  'I can help you explore this further. What specific aspect interests you?',
  'That makes sense. Based on what you said, I recommend...',
  'Interesting perspective! Let me share some insights...',
  "I appreciate the question. Here's what I found...",
  'Absolutely! Let me help you understand this better.',
];

/**
 * DemoChatWindow
 * 
 * A demo wrapper around ChatWindow that simulates agent responses.
 * Useful for testing UI and interactions without a backend.
 * 
 * Features:
 * - Simulates AI responses with slight delay
 * - Shows typing indicator during response
 * - Stores conversation history
 * - Easy to disable demo mode
 */
export function DemoChatWindow({
  agentTitle = 'Learning AI Agent',
  enableDemo = true,
}: DemoChatWindowProps): ReactNode {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome-msg',
      sender: 'assistant',
      text: 'Hello! I am your Learning AI Agent. Feel free to ask me anything about your learning journey. Type a message to get started!',
      timestamp: new Date(),
    },
  ]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = useCallback(
    async (userMessage: string) => {
      if (!enableDemo) return;

      // Add user message
      const userMsg: ChatMessage = {
        id: `msg-user-${Date.now()}`,
        sender: 'user',
        text: userMessage,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, userMsg]);
      setIsLoading(true);

      // Simulate network delay (1-2 seconds)
      await new Promise((resolve) =>
        setTimeout(resolve, 1000 + Math.random() * 1000)
      );

      // Get a random demo response
      const randomResponse =
        DEMO_RESPONSES[Math.floor(Math.random() * DEMO_RESPONSES.length)];

      // Add agent message
      const agentMsg: ChatMessage = {
        id: `msg-agent-${Date.now()}`,
        sender: 'assistant',
        text: randomResponse,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, agentMsg]);
      setIsLoading(false);
    },
    [enableDemo]
  );

  return (
    <ChatWindow
      agentTitle={agentTitle}
      messages={messages}
      onSendMessage={handleSendMessage}
      isLoading={isLoading}
    />
  );
}
