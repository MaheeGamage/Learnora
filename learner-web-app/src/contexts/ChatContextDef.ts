import { createContext } from 'react';

export interface ChatContextType {
  activeThreadId: string | null;
  setActiveThreadId: (threadId: string | null) => void;
  clearActiveThread: () => void;
}

export const ChatContext = createContext<ChatContextType | undefined>(undefined);
