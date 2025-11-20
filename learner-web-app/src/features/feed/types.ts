export type FeedItemType = 'content' | 'evaluation';

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

export type FeedItem = FeedContent | FeedEvaluation;
