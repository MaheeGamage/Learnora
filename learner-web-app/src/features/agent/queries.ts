import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { startChat, continueChat, getChatSession, generateMCQQuestions } from './api';
import type { AgentMode, ChatSession, MCQGenerationRequest } from './types';

// Query keys
export const chatKeys = {
  all: ['chat'] as const,
  session: (threadId: string) => [...chatKeys.all, 'session', threadId] as const,
};

export const mcqKeys = {
  all: ['mcq'] as const,
  generate: () => [...mcqKeys.all, 'generate'] as const,
};

// Hook to fetch a chat session by thread_id
export function useChatSession(threadId: string | null) {
  return useQuery({
    queryKey: chatKeys.session(threadId || ''),
    queryFn: () => getChatSession(threadId!),
    enabled: !!threadId, // Only run query if threadId exists
    staleTime: 30000, // Consider data fresh for 30 seconds
  });
}

// Hook to start a new chat session
export function useStartChat() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (params: { message?: string; mode?: AgentMode }) => startChat(params),
    onSuccess: (data: ChatSession) => {
      // Cache the new session
      queryClient.setQueryData(chatKeys.session(data.thread_id), data);
    },
  });
}

// Hook to continue an existing chat session
export function useContinueChat(threadId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (params: { message: string; mode?: AgentMode }) => 
      continueChat(threadId, params),
    onSuccess: (data: ChatSession) => {
      // Update the cached session
      queryClient.setQueryData(chatKeys.session(threadId), data);
    },
  });
}

// Hook to generate MCQ questions
export function useGenerateMCQ() {
  return useMutation({
    mutationFn: (params: MCQGenerationRequest) => generateMCQQuestions(params),
  });
}
