import { useContext } from 'react';
import { ChatContext, type ChatContextType } from '../contexts/ChatContextDef';

/**
 * Hook to access chat context
 * Must be used within ChatProvider
 */
export function useChatContext(): ChatContextType {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChatContext must be used within ChatProvider');
  }
  return context;
}
