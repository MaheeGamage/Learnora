/**
 * Service for managing user learning preferences and interactions
 */

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
export async function getPreferences(token: string): Promise<UserPreferences> {
    try {
        const response = await fetch(`${API_URL}/preferences/`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Failed to fetch preferences: ${response.status} ${errorText}`);
        }

        return response.json();
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
    token: string
): Promise<UserPreferences> {
    const response = await fetch(`${API_URL}/preferences/`, {
        method: 'PUT',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(updates),
    });

    if (!response.ok) {
        throw new Error('Failed to update preferences');
    }

    return response.json();
}

/**
 * Track a content interaction
 */
export async function trackInteraction(
    interaction: ContentInteraction,
    token: string
): Promise<void> {
    console.log('Tracking URL:', `${API_URL}/preferences/interactions`);
    const response = await fetch(`${API_URL}/preferences/interactions`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(interaction),
    });

    if (!response.ok) {
        throw new Error('Failed to track interaction');
    }

    return response.json();
}

/**
 * Get learning insights and statistics
 */
export async function getLearningInsights(token: string): Promise<LearningInsights> {
    try {
        const response = await fetch(`${API_URL}/preferences/insights`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Failed to fetch insights: ${response.status} ${errorText}`);
        }

        return response.json();
    } catch (error) {
        if (error instanceof TypeError && error.message.includes('fetch')) {
            throw new Error('Network error: Unable to connect to backend server');
        }
        throw error;
    }
}
