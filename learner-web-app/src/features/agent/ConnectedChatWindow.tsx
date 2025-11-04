import { useState, useEffect, type ReactNode } from 'react';
import { ChatWindow, type ChatMessage } from './ChatWindow';
import { useStartChat, useContinueChat } from './queries';
import type { Message } from './types';

export interface ConnectedChatWindowProps {
  readonly agentTitle?: string;
  readonly initialTopic?: string;
}

/**
 * ConnectedChatWindow - A connected version of ChatWindow that integrates with the chat API
 * using React Query for state management.
 * 
 * This component handles:
 * - Starting new chat sessions
 * - Continuing existing chat sessions
 * - Converting between API message format and UI message format
 * - Managing loading states
 */
export function ConnectedChatWindow({
  agentTitle = 'AI Learning Assistant',
  initialTopic = 'General Learning',
}: ConnectedChatWindowProps): ReactNode {
  const [threadId, setThreadId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const topic = initialTopic;

  const startChatMutation = useStartChat();
  const continueChatMutation = useContinueChat(threadId || '');

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
      setThreadId(thread_id);
      setMessages(apiMessages.map(convertToUIMessage));
    }
  }, [startChatMutation.isSuccess, startChatMutation.data]);

  useEffect(() => {
    if (continueChatMutation.isSuccess && continueChatMutation.data) {
      const { messages: apiMessages } = continueChatMutation.data;
      setMessages(apiMessages.map(convertToUIMessage));
    }
  }, [continueChatMutation.isSuccess, continueChatMutation.data]);

  const handleSendMessage = (message: string) => {
    if (threadId) {
      // Continue existing chat session
      continueChatMutation.mutate({
        message,
        topic,
      });
    } else {
      // Start a new chat session
      startChatMutation.mutate({
        message,
        topic,
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
