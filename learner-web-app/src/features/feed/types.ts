import type { ConceptWithStatus } from '../learning-path/utils/conceptStatusUtils';

export type FeedItemType = 'content' | 'evaluation' | 'concept';

export interface FeedContent {
    id: string;
    type: 'content';
    title: string;
    description: string;
    source: string;
    url: string;
    imageUrl?: string;
    topic: string;
    readTime?: string;
    author?: string;
    publishedDate?: string;
}

export interface FeedEvaluation {
    id: string;
    type: 'evaluation';
    topic: string;
    question: string;
    options: Record<string, string>;
    correctAnswer: string;
    explanation: string;
    difficulty: 'Beginner' | 'Intermediate' | 'Advanced';
}

export interface FeedConcept {
    id: string;
    type: 'concept';
    concept: ConceptWithStatus;
    learningPathId: number;
}

export type FeedItem = FeedContent | FeedEvaluation | FeedConcept;
