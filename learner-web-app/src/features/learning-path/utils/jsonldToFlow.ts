import { type Node, type Edge, MarkerType } from "@xyflow/react";
import type { JsonLdDocument } from "jsonld";
import type { FlowNodeData } from "../types";
import {
  getLocalId,
  findLabel,
  isConceptOrGoal,
  parseType,
  parsePrerequisites,
  collectKnownConcepts,
  determineConceptStatus,
} from "./jsonldUtils";

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
    { id: string; idRaw:string; label: string; type?: string; prerequisites: string[]; known?: boolean; status?: 'known' | 'ready' | 'locked' }
  >();

  // Collect known concepts from any user 'knows' fields before building node meta
  const knownSet = collectKnownConcepts(jsonld);

  const collectNodeMeta = (items: Array<Record<string, unknown>>) => {
    for (const item of items) {
      if (!item) continue;
      
      // Only process Concept and Goal types
      if (!isConceptOrGoal(item)) continue;
      
      const idRaw = item["@id"];
      if (typeof idRaw !== "string") continue;
      const localId = getLocalId(idRaw);
      const type = parseType(item);
      const label = findLabel(item);
      const prerequisites = parsePrerequisites(item);

      const known = knownSet.has(localId);

      nodeMeta.set(localId, { id: localId, idRaw, label, type, prerequisites, known });
    }
  };

  collectNodeMeta(jsonld);

  // Apply status to all nodes
  for (const [nodeId, meta] of nodeMeta) {
    meta.status = determineConceptStatus(nodeId, meta.prerequisites, knownSet);
  }

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
    
    // Goals should be at the rightmost position (highest level)
    if (meta.type === "Goal") {
      // Don't calculate level yet, will be set after all concepts
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

  // Calculate levels for all non-goal nodes first
  for (const [key, meta] of nodeMeta) {
    if (meta.type !== "Goal") {
      calcLevel(key);
    }
  }
  
  // Find the maximum level from concepts
  let maxConceptLevel = -1;
  for (const [, level] of levels) {
    if (level > maxConceptLevel) {
      maxConceptLevel = level;
    }
  }
  
  // Place all goals at the rightmost position (one level after the last concept)
  const goalLevel = maxConceptLevel + 1;
  for (const [key, meta] of nodeMeta) {
    if (meta.type === "Goal") {
      levels.set(key, goalLevel);
    }
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
        data: { 
          label: meta?.label, 
          originalId: meta?.id, 
          type: meta?.type, 
          known: meta?.known,
          status: meta?.status,
          concept: { id: meta.idRaw, label: meta.label }
        },
        type: meta?.type === "Goal" ? "goal-node" : "concept-node",
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
        edges.push({ id: edgeId, source, target, markerEnd: { type: MarkerType.ArrowClosed } });
      }
    }
  }

  return { nodes, edges };
}

export default jsonldToFlow;
