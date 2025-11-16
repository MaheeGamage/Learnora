/**
 * Utility functions for generating evaluate page URLs
 */

/**
 * Generate a URL to the evaluate page with pre-selected learning path and concept
 * 
 * @param learningPathId - The ID of the learning path
 * @param conceptId - The RDF concept ID (will be URL-encoded automatically)
 * @returns The formatted URL string
 * 
 * @example
 * ```typescript
 * const url = generateEvaluateUrl(42, "http://learnora.ai/ont#named_entity_recognition_(ner)");
 * // Returns: "/evaluate/42?conceptId=http%3A%2F%2Flearnora.ai%2Font%23named_entity_recognition_(ner)"
 * navigate(url);
 * ```
 */
export function generateEvaluateUrl(learningPathId: number, conceptId?: string): string {
  const basePath = `/evaluate/${learningPathId}`;
  
  if (conceptId) {
    const encodedConceptId = encodeURIComponent(conceptId);
    return `${basePath}?conceptId=${encodedConceptId}`;
  }
  
  return basePath;
}

/**
 * Generate evaluate URL with only learning path ID
 * 
 * @param learningPathId - The ID of the learning path
 * @returns The formatted URL string
 */
export function generateEvaluateUrlForPath(learningPathId: number): string {
  return `/evaluate/${learningPathId}`;
}

/**
 * Decode a concept ID from URL parameters
 * Handles URL-encoded RDF concept IDs
 * 
 * @param encodedConceptId - The URL-encoded concept ID
 * @returns The decoded concept ID
 */
export function decodeConceptId(encodedConceptId: string): string {
  return decodeURIComponent(encodedConceptId);
}

/**
 * Encode a concept ID for use in URL parameters
 * 
 * @param conceptId - The RDF concept ID to encode
 * @returns The URL-encoded concept ID
 */
export function encodeConceptId(conceptId: string): string {
  return encodeURIComponent(conceptId);
}
