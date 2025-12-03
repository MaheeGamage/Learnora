// Content Discovery API Service
import apiClient from '../../api/baseClient';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_V1_PREFIX = '/api/v1';

export interface LearningContent {
    id: string;
    title: string;
    content_type: string;
    source: string;
    url: string;
    description: string;
    difficulty: string;
    duration_minutes: number;
    tags: string[];
    prerequisites: string[];
    metadata: Record<string, unknown>;
    created_at: string;
    checksum?: string;
}

export interface VideoHighlight {
    timestamp: string;
    topic: string;
    description: string;
    importance_score: number;
}

export interface SearchResultItem {
    content: LearningContent;
    score: number;
    relevance_score: number;
    personalization_boost: number;

    // 🆕 Personalized content fields
    personalized_summary?: string;
    tldr?: string;
    key_takeaways?: string[];
    highlights?: VideoHighlight[];
    estimated_time?: number;
}

export interface SearchRequest {
    query: string;
    strategy?: 'bm25' | 'dense' | 'hybrid';
    top_k?: number;
    refresh_content?: boolean;
    auto_discover?: boolean;
    discovery_sources?: string[];
    use_nlp?: boolean;

    // 🆕 Personalization options
    personalize?: boolean;
    max_summary_words?: number;
}

export interface SearchResponse {
    query: string;
    processed_query: string;
    user_id: string;
    strategy: string;
    results: SearchResultItem[];
    stats: {
        total_indexed: number;
        returned: number;
    };
    nlp_analysis?: {
        intent: Record<string, unknown>;
        entities: Record<string, unknown>;
        key_terms: string[];
    };
}

export interface ContentStats {
    total_indexed: number;
    crawler_enabled: boolean;
    api_fetcher_enabled: boolean;
    nlp_enabled: boolean;
    auto_discovery_enabled: boolean;
}

export interface CrawlRequest {
    urls: string[];
    custom_keywords?: string[];
}

export interface CrawlResponse {
    discovered_count: number;
    total_indexed: number;
}

export interface IndexContentRequest {
    contents: LearningContent[];
}

export interface IndexContentResponse {
    indexed_count: number;
    total_indexed: number;
}

export interface SetKeywordsRequest {
    keywords: string[];
}

export interface SetKeywordsResponse {
    keywords: string[];
    count: number;
    message: string;
}

/**
 * Search for learning content
 */
export async function searchContent(
    request: SearchRequest,
    token?: string // Made optional since apiClient will handle auth
): Promise<SearchResponse> {
    const response = await apiClient.post<SearchResponse>(
        '/content-discovery/search',
        request
    );

    return response.data;
}

/**
 * Crawl URLs and index discovered content
 */
export async function crawlUrls(
    request: CrawlRequest,
    token?: string // Made optional since apiClient will handle auth
): Promise<CrawlResponse> {
    const response = await apiClient.post<CrawlResponse>(
        '/content-discovery/crawl',
        request
    );

    return response.data;
}

/**
 * Manually index learning content
 */
export async function indexContent(
    request: IndexContentRequest,
    token?: string // Made optional since apiClient will handle auth
): Promise<IndexContentResponse> {
    const response = await apiClient.post<IndexContentResponse>(
        '/content-discovery/index',
        request
    );

    return response.data;
}

/**
 * Set custom keywords for tag extraction
 */
export async function setCustomKeywords(
    request: SetKeywordsRequest,
    token?: string // Made optional since apiClient will handle auth
): Promise<SetKeywordsResponse> {
    const response = await apiClient.post<SetKeywordsResponse>(
        '/content-discovery/set-keywords',
        request
    );

    return response.data;
}

/**
 * Enable or disable automatic content discovery
 */
export async function enableAutoDiscovery(
    enabled: boolean,
    token?: string // Made optional since apiClient will handle auth
): Promise<{ auto_discovery_enabled: boolean }> {
    const response = await apiClient.post<{ auto_discovery_enabled: boolean }>(
        `/content-discovery/enable-auto-discovery?enabled=${enabled}`
    );

    return response.data;
}

/**
 * Get content discovery statistics
 */
export async function getContentStats(token?: string): Promise<ContentStats> {
    const response = await apiClient.get<ContentStats>(
        '/content-discovery/stats'
    );

    return response.data;
}

/**
 * Get all indexed content
 */
export async function getAllContent(
    skip = 0,
    limit = 100,
    token?: string // Made optional since apiClient will handle auth
): Promise<LearningContent[]> {
    const response = await apiClient.get<LearningContent[]>(
        `/content-discovery/contents?skip=${skip}&limit=${limit}`
    );

    return response.data;
}

/**
 * Get a specific content item by ID
 */
export async function getContentById(
    contentId: string,
    token?: string // Made optional since apiClient will handle auth
): Promise<LearningContent> {
    const response = await apiClient.get<LearningContent>(
        `/content-discovery/content/${contentId}`
    );

    return response.data;
}

/**
 * Get recommended content (mock for now - can be enhanced)
 */
export async function getRecommendations(
    token?: string // Made optional since apiClient will handle auth
): Promise<LearningContent[]> {
    // For now, get recent content as recommendations
    // This can be enhanced with a dedicated recommendations endpoint
    return getAllContent(0, 6);
}
