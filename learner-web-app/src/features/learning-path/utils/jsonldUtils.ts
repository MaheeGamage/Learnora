import type { JsonLdDocument } from "jsonld";

/**
 * Utility to get a safe local id from a full URI
 * Extracts the last part of the URI and sanitizes it for use as an ID
 */
export const getLocalId = (uri: string): string => {
  if (!uri) return "";
  const parts = uri.split("#");
  const last = parts.length > 1 ? parts.pop()! : uri.split("/").pop()!;
  // Replace characters that are not allowed in DOM ids
  return String(last).replaceAll(/[^a-zA-Z0-9_-]/g, "_");
};

/**
 * Find label from JSON-LD item
 * Searches for common label predicates in the item
 */
export const findLabel = (item: Record<string, unknown>): string => {
  const keys = Object.keys(item);
  const labelKey = keys.find((k) => /label$/i.test(k) || /#label/.test(k));
  if (!labelKey) return getLocalId((item["@id"] as string) || "");
  const value = item[labelKey];
  if (Array.isArray(value) && value.length > 0) {
    const first = value[0];
    if (first && typeof first === "object" && "@value" in first)
      return String((first as Record<string, unknown>)["@value"]);
    if (typeof first === "string") return first;
  }
  // Fallback: prefer the id-derived label instead of stringifying an object
  const idVal = item["@id"];
  if (typeof idVal === "string") return getLocalId(idVal);
  return "";
};

/**
 * Check if item is a Concept or Goal type
 */
export const isConceptOrGoal = (item: Record<string, unknown>): boolean => {
  const t = item["@type"];
  if (!t) return false;
  
  const types = Array.isArray(t) ? t : [t];
  return types.some(type => {
    if (typeof type !== "string") return false;
    const localType = getLocalId(type);
    return localType === "Concept" || localType === "Goal";
  });
};

/**
 * Check if item is a Concept type only (excludes Goals)
 */
export const isConcept = (item: Record<string, unknown>): boolean => {
  const t = item["@type"];
  if (!t) return false;
  
  const types = Array.isArray(t) ? t : [t];
  return types.some(type => {
    if (typeof type !== "string") return false;
    const localType = getLocalId(type);
    return localType === "Concept";
  });
};

/**
 * Parse type from JSON-LD item
 */
export const parseType = (item: Record<string, unknown>): string | undefined => {
  const t = item["@type"];
  if (Array.isArray(t) && t.length > 0 && typeof t[0] === "string")
    return getLocalId(t[0]);
  if (typeof t === "string") return getLocalId(t);
  return undefined;
};

/**
 * Parse prerequisites from JSON-LD item
 * Returns an array of local IDs of prerequisite concepts
 */
export const parsePrerequisites = (item: Record<string, unknown>): string[] => {
  const prereqKeys = [
    "http://learnora.ai/ont#hasPrerequisite",
    "hasPrerequisite",
    "has_prerequisite"
  ];
  
  let prereqArray: unknown[] = [];
  for (const key of prereqKeys) {
    if (Array.isArray(item[key])) {
      prereqArray = item[key] as unknown[];
      break;
    }
  }

  const prerequisites: string[] = [];
  for (const p of prereqArray) {
    if (p && typeof p === "object" && (p as Record<string, unknown>)["@id"]) {
      const idVal = (p as Record<string, unknown>)["@id"];
      if (typeof idVal === "string") prerequisites.push(getLocalId(idVal));
    }
  }
  return prerequisites;
};

/**
 * Collect known concepts from JSON-LD data
 * Extracts all concept IDs that the user knows from the data
 */
export const collectKnownConcepts = (jsonld: JsonLdDocument[]): Set<string> => {
  const knownSet = new Set<string>();
  for (const item of jsonld) {
    if (!item) continue;
    const knows = item["http://learnora.ai/ont#knows"] ?? item["knows"];
    if (!knows) continue;
    const arr = Array.isArray(knows) ? knows : [knows];
    for (const k of arr) {
      if (!k) continue;
      if (typeof k === "string") {
        knownSet.add(getLocalId(k));
      } else if (typeof k === "object" && (k as Record<string, unknown>)["@id"]) {
        const idVal = (k as Record<string, unknown>)["@id"];
        if (typeof idVal === "string") knownSet.add(getLocalId(idVal));
      }
    }
  }
  return knownSet;
};

/**
 * Concept status type
 */
export type ConceptStatus = 'known' | 'ready' | 'locked';

/**
 * Determine the status of a concept based on user knowledge and prerequisites
 * @param conceptId - The local ID of the concept
 * @param prerequisites - Array of prerequisite concept local IDs
 * @param knownSet - Set of known concept local IDs
 * @returns The concept status
 */
export const determineConceptStatus = (
  conceptId: string,
  prerequisites: string[],
  knownSet: Set<string>
): ConceptStatus => {
  // If user already knows this concept
  if (knownSet.has(conceptId)) return 'known';
  
  // If no prerequisites, it's ready to learn
  if (!prerequisites || prerequisites.length === 0) return 'ready';
  
  // Check if all prerequisites are known
  const allPrereqsKnown = prerequisites.every(prereqId => knownSet.has(prereqId));
  
  return allPrereqsKnown ? 'ready' : 'locked';
};
