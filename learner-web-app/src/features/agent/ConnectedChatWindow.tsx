import { useState, useEffect, type ReactNode } from 'react';
import { ChatWindow, type ChatMessage } from './ChatWindow';
import { useStartChat, useContinueChat, useChatSession } from './queries';
import { useChatContext } from '../../hooks/useChatContext';
import type { Message, AgentMode } from './types';

export interface ConnectedChatWindowProps {
  readonly agentTitle?: string;
  readonly mode?: AgentMode;
}

/**
 * ConnectedChatWindow - A connected version of ChatWindow that integrates with the chat API
 * using React Query for state management.
 * 
 * This component handles:
 * - Starting new chat sessions with optional mode (LPP for learning path planning)
 * - Continuing existing chat sessions
 * - Loading messages from ChatContext active thread
 * - Converting between API message format and UI message format
 * - Managing loading states
 * - Automatically syncing thread ID with ChatContext
 */
export function ConnectedChatWindow({
  agentTitle = 'AI Learning Assistant',
  mode,
}: ConnectedChatWindowProps): ReactNode {
  const { activeThreadId, setActiveThreadId } = useChatContext();
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  const startChatMutation = useStartChat();
  const continueChatMutation = useContinueChat(activeThreadId || '');
  
  // Hook to load existing chat session from ChatContext
  const { data: existingSession } = useChatSession(activeThreadId);

  // Convert API Message format to UI ChatMessage format
  const convertToUIMessage = (apiMessage: Message, index: number): ChatMessage => ({
    id: `msg-${index}-${Date.now()}`,
    sender: apiMessage.role === 'human' ? 'user' : 'assistant',
    text: apiMessage.content,
    timestamp: new Date(),
  });

  // Update messages when a chat mutation succeeds
  useEffect(() => {
    if (startChatMutation.isSuccess && startChatMutation.data) {
      const { thread_id, messages: apiMessages } = startChatMutation.data;
      // Store thread ID in ChatContext (also saves to localStorage)
      setActiveThreadId(thread_id);
      setMessages(apiMessages.map(convertToUIMessage));
    }
  }, [startChatMutation.isSuccess, startChatMutation.data, setActiveThreadId]);

  useEffect(() => {
    if (continueChatMutation.isSuccess && continueChatMutation.data) {
      const { messages: apiMessages } = continueChatMutation.data;
      setMessages(apiMessages.map(convertToUIMessage));
    }
  }, [continueChatMutation.isSuccess, continueChatMutation.data]);

  // Load messages from ChatContext active thread when it changes
  useEffect(() => {
    if (existingSession?.messages) {
      setMessages(existingSession.messages.map(convertToUIMessage));
    }
  }, [existingSession?.messages]);

  const handleSendMessage = (message: string) => {
    if (activeThreadId) {
      // Continue existing chat session
      continueChatMutation.mutate({
        message,
        mode,
      });
    } else {
      // Start a new chat session with optional mode
      // Only if no thread exists (defensive - normally thread should be created externally)
      startChatMutation.mutate({
        message,
        mode,
      });
    }
  };

  const isLoading = startChatMutation.isPending || continueChatMutation.isPending;

  return (
    <ChatWindow
      agentTitle={agentTitle}
      messages={messages}
      onSendMessage={handleSendMessage}
      isLoading={isLoading}
    />
  );
}
