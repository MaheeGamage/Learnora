import apiClient from "../../api/baseClient";
import type { ChatSession, ContinueChatParams, StartChatParams } from "./types";

// Create a new chat session
export const startChat = async (params: StartChatParams): Promise<ChatSession> => {
  const response = await apiClient.post<ChatSession>('/agent/chat', params);
  return response.data;
}

// Continue an existing chat session by thread_id
export const continueChat = async (thread_id: string, params: ContinueChatParams): Promise<ChatSession> => {
  const response = await apiClient.post<ChatSession>(`/agent/chat/${thread_id}`, params);
  return response.data;
}

// Get chat session by thread_id
export const getChatSession = async (thread_id: string): Promise<ChatSession> => {
  const response = await apiClient.get<ChatSession>(`/agent/chat/${thread_id}`);
  return response.data;
}