export type Message = {
  role: 'human' | 'agent';
  content: string;
}

export type ChatSession = {
  thread_id: string;
  status: string;               // e.g., "in_progress", "completed"
  messages: Message[];
  topic: string;
  learning_path_json: string;   // assuming a JSON string
  learning_path: string;
}

export const AgentMode = {
  BASIC: "basic", // Starting a new conversation
  LPP: "lpp",     // Planning a learning path
} as const;

export type AgentMode = typeof AgentMode[keyof typeof AgentMode];

export type StartChatParams = {
  message: string;
  mode?: AgentMode;
}

export type ContinueChatParams = {
  message: string;
  mode?: AgentMode;
}