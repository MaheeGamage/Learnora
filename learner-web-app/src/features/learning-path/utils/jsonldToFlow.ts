import type { Node, Edge } from "@xyflow/react";
import type { JsonLdDocument } from "jsonld";

export interface FlowNodeData extends Record<string, unknown> {
  label: string;
  originalId?: string;
  type?: string;
}

// Utility to get a safe local id from a full uri
const getLocalId = (uri: string): string => {
  if (!uri) return "";
  const parts = uri.split("#");
  const last = parts.length > 1 ? parts.pop()! : uri.split("/").pop()!;
  // Replace characters that are not allowed in DOM ids
  // Use replaceAll with a regex to satisfy lint rule
  return String(last).replaceAll(/[^a-zA-Z0-9_-]/g, "_");
};

const findLabel = (item: Record<string, unknown>): string => {
  // Search for common label predicates
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

export function jsonldToFlow(
  jsonld: JsonLdDocument[] = [],
  opts?: {
    xSpacing?: number;
    ySpacing?: number;
    startX?: number;
    startY?: number;
  }
): { nodes: Node<FlowNodeData>[]; edges: Edge[] } {
  const xSpacing = opts?.xSpacing ?? 250;
  const ySpacing = opts?.ySpacing ?? 120;
  const startX = opts?.startX ?? 50;
  const startY = opts?.startY ?? 50;

  const nodeMeta = new Map<
    string,
    { id: string; label: string; type?: string; prerequisites: string[] }
  >();

  const getPrereqArray = (item: Record<string, unknown>): unknown[] => {
    if (Array.isArray(item["http://learnora.ai/ont#hasPrerequisite"]))
      return item["http://learnora.ai/ont#hasPrerequisite"] as unknown[];
    if (Array.isArray(item["hasPrerequisite"]))
      return item["hasPrerequisite"] as unknown[];
    if (Array.isArray(item["has_prerequisite"]))
      return item["has_prerequisite"] as unknown[];
    return [];
  };

  const parseType = (item: Record<string, unknown>): string | undefined => {
    const t = item["@type"];
    if (Array.isArray(t) && t.length > 0 && typeof t[0] === "string")
      return getLocalId(t[0]);
    if (typeof t === "string") return getLocalId(t);
    return undefined;
  };

  const parsePrereqs = (item: Record<string, unknown>): string[] => {
    const prereqArray = getPrereqArray(item);
    const prerequisites: string[] = [];
    for (const p of prereqArray) {
      if (p && typeof p === "object" && (p as Record<string, unknown>)["@id"]) {
        const idVal = (p as Record<string, unknown>)["@id"];
        if (typeof idVal === "string") prerequisites.push(getLocalId(idVal));
      }
    }
    return prerequisites;
  };

  const collectNodeMeta = (items: Array<Record<string, unknown>>) => {
    for (const item of items) {
      if (!item) continue;
      const idRaw = item["@id"];
      if (typeof idRaw !== "string") continue;
      const localId = getLocalId(idRaw);
      const type = parseType(item);
      const label = findLabel(item);
      const prerequisites = parsePrereqs(item);

      nodeMeta.set(localId, { id: localId, label, type, prerequisites });
    }
  };

  collectNodeMeta(jsonld);

  // Calculate levels (simple DFS)
  const levels = new Map<string, number>();
  const calcLevel = (nodeId: string, visited = new Set<string>()): number => {
    if (levels.has(nodeId)) return levels.get(nodeId)!;
    if (visited.has(nodeId)) return 0; // cycle guard
    visited.add(nodeId);
    const meta = nodeMeta.get(nodeId);
    if (!meta) {
      levels.set(nodeId, 0);
      visited.delete(nodeId);
      return 0;
    }
    if (!meta.prerequisites || meta.prerequisites.length === 0) {
      levels.set(nodeId, 0);
      visited.delete(nodeId);
      return 0;
    }
    let maxLevel = -1;
    for (const p of meta.prerequisites) {
      const l = calcLevel(p, visited);
      if (l > maxLevel) maxLevel = l;
    }
    visited.delete(nodeId);
    const nodeLevel = maxLevel + 1;
    levels.set(nodeId, nodeLevel);
    return nodeLevel;
  };

  for (const key of nodeMeta.keys()) {
    calcLevel(key);
  }

  // Group nodes by level
  const nodesByLevel = new Map<number, string[]>();
  for (const [id, lvl] of levels) {
    if (!nodesByLevel.has(lvl)) nodesByLevel.set(lvl, []);
    nodesByLevel.get(lvl)!.push(id);
  }

  // Convert to flow nodes
  const nodes: Node<FlowNodeData>[] = [];
  for (const [level, ids] of nodesByLevel) {
    // center Y positions for this level
    const nodesInLevel = ids.length;
    const totalHeight = (nodesInLevel - 1) * ySpacing;
    const startYForLevel = startY - totalHeight / 2;
    let index = 0;
    for (const id of ids) {
      const meta = nodeMeta.get(id)!;
      const x = startX + level * xSpacing;
      const y = Math.round(startYForLevel + index * ySpacing);
      if (!meta) continue;
      nodes.push({
        id: id,
        position: { x, y },
        data: { label: meta?.label, originalId: meta?.id, type: meta?.type },
        type: "node-with-toolbar",
      });
      index += 1;
    }
  }

  // Edges from prerequisite -> node
  const edges: Edge[] = [];
  const edgeSet = new Set<string>();
  for (const [id, meta] of nodeMeta) {
    if (!meta.prerequisites || meta.prerequisites.length === 0) continue;
    for (const p of meta.prerequisites) {
      const source = p;
      const target = id;
      const edgeId = `${source}-${target}`;
      if (!edgeSet.has(edgeId)) {
        edgeSet.add(edgeId);
        edges.push({ id: edgeId, source, target });
      }
    }
  }

  return { nodes, edges };
}

export default jsonldToFlow;
