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
  message?: string;
  mode?: AgentMode;
}

export type ContinueChatParams = {
  message: string;
  mode?: AgentMode;
}

// MCQ Generation Types
export type DifficultyLevel = 'Beginner' | 'Intermediate' | 'Advanced';

export type MCQOption = {
  A: string;
  B: string;
  C: string;
  D: string;
}

export type MCQQuestion = {
  question: string;
  options: MCQOption;
  correct_answer: 'A' | 'B' | 'C' | 'D';
  explanation: string;
}

export type MCQGenerationRequest = {
  concept_name: string;
  concept_description?: string;
  difficulty_level: DifficultyLevel;
  question_count?: number; // 1-20, default 5
  learning_path_db_id: number;
  learning_path?: Array<Record<string, unknown>>;
  concept_id?: string;
}

export type MCQGenerationResponse = {
  questions: MCQQuestion[];
}