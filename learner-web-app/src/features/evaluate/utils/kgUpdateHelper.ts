import type { JsonLdNode } from "../../learning-path/types";
import { MCQ_CONFIG } from "../../learning-path/constant";

/**
 * Build a JSON-LD triplet for updating user knowledge graph
 * Represents: user knows concept
 *
 * @param userId - The user ID
 * @param conceptId - The concept ID
 * @returns JSON-LD node representing the "knows" relationship
 */
export const buildUserKnowsConceptTriple = (
  userId: string | number,
  conceptId: string
): JsonLdNode => {
  return {
    "@id": `http://learnora.ai/ont#user_${userId}`,
    [MCQ_CONFIG.ONTOLOGY_PREDICATES.KNOWS]: [
      {
        "@id": `http://learnora.ai/ont#${conceptId}`,
      },
    ],
  };
};

/**
 * Check if user passed the evaluation
 *
 * @param score - User's score percentage (0-100)
 * @returns true if score >= passing threshold
 */
export const hasPassedEvaluation = (score: number): boolean => {
  return score >= MCQ_CONFIG.PASSING_SCORE_THRESHOLD;
};
