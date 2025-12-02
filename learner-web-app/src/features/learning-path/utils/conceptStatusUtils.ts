import type { JsonLdDocument } from "jsonld";
import {
  getLocalId,
  findLabel,
  parsePrerequisites,
  collectKnownConcepts,
  determineConceptStatus,
  type ConceptStatus,
} from "./jsonldUtils";

// Re-export ConceptStatus for backward compatibility
export type { ConceptStatus };

/**
 * Concept with its learning status
 */
export interface ConceptWithStatus {
  id: string;
  label: string;
  status: ConceptStatus;
  prerequisites: string[];
}

/**
 * Extract all concepts with their status from learning path JSON-LD data
 */
export function extractConceptsWithStatus(
  jsonld: JsonLdDocument[] = []
): ConceptWithStatus[] {
  const concepts: ConceptWithStatus[] = [];
  const knownSet = collectKnownConcepts(jsonld);

  for (const item of jsonld) {
    if (!item) continue;
    
    // Only include Concept types, exclude Goals
    const itemType = item["@type"];
    if (!itemType) continue;
    const types = Array.isArray(itemType) ? itemType : [itemType];
    const isConcept = types.some(type => {
      if (typeof type !== "string") return false;
      const localType = getLocalId(type);
      return localType === "Concept";
    });
    if (!isConcept) continue;
    
    const idRaw = item["@id"];
    if (typeof idRaw !== "string") continue;
    
    const localId = getLocalId(idRaw);
    const label = findLabel(item);
    const prerequisites = parsePrerequisites(item);
    const status = determineConceptStatus(localId, prerequisites, knownSet);

    concepts.push({
      id: idRaw,
      label,
      status,
      prerequisites,
    });
  }

  return concepts;
}

/**
 * Extract only ready concepts from learning path JSON-LD data
 * These are concepts that the user doesn't know yet but has all prerequisites satisfied
 */
export function extractReadyConcepts(
  jsonld: JsonLdDocument[] = []
): ConceptWithStatus[] {
  const allConcepts = extractConceptsWithStatus(jsonld);
  return allConcepts.filter(concept => concept.status === 'ready');
}

/**
 * Get concept status from learning path data
 */
export function getConceptStatus(
  conceptId: string,
  jsonld: JsonLdDocument[] = []
): ConceptStatus | null {
  const concepts = extractConceptsWithStatus(jsonld);
  const concept = concepts.find(c => c.id === conceptId || getLocalId(c.id) === conceptId);
  return concept ? concept.status : null;
}
