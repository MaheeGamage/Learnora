import type { ConceptWithStatus } from "../../learning-path/utils/conceptStatusUtils";
import { searchContent, type SearchResultItem } from "../../content-discovery/contentDiscoveryService";

/**
 * Configuration for feed generation
 */
export interface FeedConfig {
  /** Number of content items to fetch per concept */
  itemsPerConcept: number;
  /** Search strategy to use */
  strategy: 'bm25' | 'dense' | 'hybrid';
  /** Enable personalized summaries and highlights */
  enablePersonalization: boolean;
  /** Maximum words for personalized summary */
  maxSummaryWords: number;
}

/**
 * Default feed configuration
 */
export const DEFAULT_FEED_CONFIG: FeedConfig = {
  itemsPerConcept: 2,
  strategy: 'hybrid',
  enablePersonalization: false,
  maxSummaryWords: 150,
};

/**
 * Extended search result item with concept tracking
 */
export interface FeedSearchResultItem extends SearchResultItem {
  concept_label: string;
  concept_id: string;
}

/**
 * Result from feed generation
 */
export interface FeedGenerationResult {
  items: FeedSearchResultItem[];
  conceptsSearched: string[];
  errors: Array<{ concept: string; error: string }>;
}

/**
 * Generate feed content for a single concept
 */
async function generateFeedForConcept(
  concept: ConceptWithStatus,
  config: FeedConfig,
  token: string
): Promise<{ items: FeedSearchResultItem[]; error?: string }> {
  try {
    const response = await searchContent(
      {
        query: concept.label,
        strategy: config.strategy,
        top_k: config.itemsPerConcept,
        personalize: config.enablePersonalization,
        max_summary_words: config.maxSummaryWords,
        auto_discover: true,
        use_nlp: true,
      },
      token
    );

    // Add concept tracking to each result
    const itemsWithConcept: FeedSearchResultItem[] = response.results.map(item => ({
      ...item,
      concept_label: concept.label,
      concept_id: concept.id,
    }));

    return { items: itemsWithConcept };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    return { items: [], error: errorMessage };
  }
}

/**
 * Generate feed content for multiple concepts in parallel
 * 
 * @param concepts - Array of ready concepts to generate content for
 * @param config - Feed generation configuration
 * @param token - Authentication token
 * @returns Feed generation result with items and any errors
 */
export async function generateFeedFromConcepts(
  concepts: ConceptWithStatus[],
  config: FeedConfig,
  token: string
): Promise<FeedGenerationResult> {
  if (concepts.length === 0) {
    return {
      items: [],
      conceptsSearched: [],
      errors: [],
    };
  }

  // Execute searches in parallel for all concepts
  const searchPromises = concepts.map((concept) =>
    generateFeedForConcept(concept, config, token)
      .then((result) => ({ concept: concept.label, ...result }))
  );

  const results = await Promise.all(searchPromises);

  // Collect all items and errors
  const allItems: FeedSearchResultItem[] = [];
  const errors: Array<{ concept: string; error: string }> = [];
  const conceptsSearched: string[] = [];

  for (const result of results) {
    conceptsSearched.push(result.concept);
    allItems.push(...result.items);
    
    if (result.error) {
      errors.push({ concept: result.concept, error: result.error });
    }
  }

  // Remove duplicate content (same ID appearing for multiple concepts)
  // Keep the first occurrence with its concept tracking
  const uniqueItems = Array.from(
    new Map(allItems.map((item) => [item.content.id, item])).values()
  );

  return {
    items: uniqueItems,
    conceptsSearched,
    errors,
  };
}
