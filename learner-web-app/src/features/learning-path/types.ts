export type Concept = Record<string, unknown>;

export type JsonLdNode = Record<string, string | string[] | Record<string, unknown> | Record<string, unknown>[] | undefined>;

export type LearningPathCreate = {
  topic: string;
  user_id: number;
  graph_uri?: string | null;
};

export type LearningPathUpdate = {
  topic?: string | null;
  graph_uri?: string | null;
  kg_data?: Array<Record<string, unknown>> | null;
  goal?: string | null;
};

export type LearningPathResponse = {
  id: number;
  topic: string;
  user_id: number;
  graph_uri?: string | null;
  created_at: string;
  updated_at?: string | null;
  kg_data?: Record<string, unknown> | null;
};

// TODO: Below Concept types should be moved to a separate module

export type ConceptCreate = {
  concept_id: string;
  label: string;
  description?: string | null;
  prerequisites?: string[] | null;
};

export type ConceptResponse = {
  id: string;
  label: string;
  prerequisites?: string[];
};

export type TestParseRequest = {
  topic: string;
  concepts: Concept[];
};

export interface FlowNodeData extends Record<string, unknown> {
  label: string;
  originalId?: string;
  type?: string;
  known?: boolean;
  status?: 'known' | 'ready' | 'locked';
  concept: ConceptResponse;
}