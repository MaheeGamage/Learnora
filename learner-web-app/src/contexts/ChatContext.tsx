import { useState, useEffect, type ReactNode } from 'react';
import { ChatContext } from './ChatContextDef';

const STORAGE_KEY = 'learnora_active_thread_id';

interface ChatProviderProps {
  readonly children: ReactNode;
}

/**
 * ChatProvider - Manages active chat thread ID with localStorage persistence
 * 
 * Features:
 * - Persists active thread ID to localStorage
 * - Automatically recovers thread on app reload
 * - Allows any component to access/update active thread
 */
export function ChatProvider({ children }: ChatProviderProps) {
  const [activeThreadId, setActiveThreadIdState] = useState<string | null>(null);
  const [isHydrated, setIsHydrated] = useState<boolean>(false);

  // Load from localStorage on mount
  useEffect(() => {
    const storedThreadId = localStorage.getItem(STORAGE_KEY);
    // TODO: Temporarily disabled to avoid issues with stale thread IDs
    // if (storedThreadId) {
    //   setActiveThreadIdState(storedThreadId);
    // }
    setIsHydrated(true);
  }, []);

  // Sync state updates to localStorage
  const setActiveThreadId = (threadId: string | null) => {
    setActiveThreadIdState(threadId);
    if (threadId) {
      localStorage.setItem(STORAGE_KEY, threadId);
    } else {
      localStorage.removeItem(STORAGE_KEY);
    }
  };

  const clearActiveThread = () => {
    setActiveThreadId(null);
  };

  // Don't render children until hydrated to avoid hydration mismatch
  if (!isHydrated) {
    return null;
  }

  return (
    <ChatContext.Provider
      value={{
        activeThreadId,
        setActiveThreadId,
        clearActiveThread,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
}
