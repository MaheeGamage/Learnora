/**
 * Service for managing user learning preferences and interactions
 */
import apiClient from '../../api/baseClient';

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export interface UserPreferences {
    id: number;
    user_id: number;
    preferred_formats: string[];
    learning_style: string;
    available_time_daily: number;
    knowledge_areas: Record<string, string>;
    learning_goals: string[];
    preferred_difficulty: string;
    auto_evolve: boolean;
    created_at: string;
    updated_at: string | null;
}

export interface PreferencesUpdate {
    preferred_formats?: string[];
    learning_style?: string;
    available_time_daily?: number;
    knowledge_areas?: Record<string, string>;
    learning_goals?: string[];
    preferred_difficulty?: string;
    auto_evolve?: boolean;
}

export interface ContentInteraction {
    content_id: string;
    interaction_type: 'viewed' | 'clicked' | 'completed' | 'bookmarked' | 'shared' | 'rated';
    content_title?: string;
    content_type?: string;
    content_difficulty?: string;
    content_duration_minutes?: number;
    content_tags?: string[];
    duration_seconds?: number;
    rating?: number;
    completion_percentage?: number;
}

export interface LearningInsights {
    preferences: {
        preferred_formats: string[];
        learning_style: string;
        preferred_difficulty: string;
        available_time_daily: number;
        knowledge_areas: Record<string, string>;
        learning_goals: string[];
        auto_evolve: boolean;
    };
    stats: {
        total_interactions: number;
        completed_count: number;
        completion_rate: number;
        average_rating: number | null;
        learning_streak_days: number;
    };
    last_updated: string | null;
}

/**
 * Get user's learning preferences
 */
export async function getPreferences(token?: string): Promise<UserPreferences> {
    try {
        const response = await apiClient.get<UserPreferences>('/api/v1/preferences/');
        return response.data;
    } catch (error) {
        if (error instanceof TypeError && error.message.includes('fetch')) {
            throw new Error('Network error: Unable to connect to backend server');
        }
        throw error;
    }
}

/**
 * Update user's learning preferences
 */
export async function updatePreferences(
    updates: PreferencesUpdate,
    token?: string
): Promise<UserPreferences> {
    const response = await apiClient.put<UserPreferences>('/api/v1/preferences/', updates);
    return response.data;
}

/**
 * Track a content interaction
 */
export async function trackInteraction(
    interaction: ContentInteraction,
    token?: string
): Promise<void> {
    console.log('Tracking URL:', `${API_URL}/preferences/interactions`);
    const response = await apiClient.post<void>('/api/v1/preferences/interactions', interaction);
    return response.data;
}

/**
 * Get learning insights and statistics
 */
export async function getLearningInsights(token?: string): Promise<LearningInsights> {
    try {
        const response = await apiClient.get<LearningInsights>('/api/v1/preferences/insights');
        return response.data;
    } catch (error) {
        if (error instanceof TypeError && error.message.includes('fetch')) {
            throw new Error('Network error: Unable to connect to backend server');
        }
        throw error;
    }
}
