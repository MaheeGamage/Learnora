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