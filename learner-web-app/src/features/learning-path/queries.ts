import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  createLearningPath,
  getAllLearningPaths,
  getLearningPath,
  updateLearningPath,
  deleteLearningPath,
  listConcepts,
  createConcept,
  getConcept,
  getConceptPrerequisites,
  testParseAndSaveLearningPath,
} from "./api";
import type {
  LearningPathCreate,
  LearningPathUpdate,
  LearningPathResponse,
  ConceptCreate,
  ConceptResponse,
  TestParseRequest,
} from "./types";

// Query keys
export const learningPathKeys = {
  all: ["learningPaths"] as const,
  lists: () => [...learningPathKeys.all, "list"] as const,
  list: (skip: number, limit: number) =>
    [...learningPathKeys.lists(), { skip, limit }] as const,
  details: () => [...learningPathKeys.all, "detail"] as const,
  detail: (id: number) => [...learningPathKeys.details(), id] as const,
};

export const conceptKeys = {
  all: ["concepts"] as const,
  lists: () => [...conceptKeys.all, "list"] as const,
  details: () => [...conceptKeys.all, "detail"] as const,
  detail: (id: string) => [...conceptKeys.details(), id] as const,
  prerequisites: (id: string) =>
    [...conceptKeys.detail(id), "prerequisites"] as const,
};

/**********************************************************************
 * LEARNING PATH QUERIES
 **********************************************************************/

/**
 * Fetch a single learning path by ID
 */
export function useLearningPath(
  learningPathId: number | null,
  includeKg: boolean = false
) {
  return useQuery({
    queryKey: learningPathKeys.detail(learningPathId || 0),
    queryFn: () => getLearningPath(learningPathId!, includeKg),
    enabled: !!learningPathId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Fetch all learning paths with pagination
 */
export function useLearningPaths(skip: number = 0, limit: number = 100) {
  return useQuery({
    queryKey: learningPathKeys.list(skip, limit),
    queryFn: () => getAllLearningPaths(skip, limit),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Create a new learning path
 */
export function useCreateLearningPath() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (params: LearningPathCreate) => createLearningPath(params),
    onSuccess: (data: LearningPathResponse) => {
      // Invalidate the list query to refetch updated data
      queryClient.invalidateQueries({
        queryKey: learningPathKeys.lists(),
      });
      // Cache the new learning path
      queryClient.setQueryData(learningPathKeys.detail(data.id), data);
    },
  });
}

/**
 * Update an existing learning path
 */
export function useUpdateLearningPath(learningPathId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (params: LearningPathUpdate) =>
      updateLearningPath(learningPathId, params),
    onSuccess: (data: LearningPathResponse) => {
      // Update the cache
      queryClient.setQueryData(learningPathKeys.detail(learningPathId), data);
      // Invalidate the list to ensure consistency
      queryClient.invalidateQueries({
        queryKey: learningPathKeys.lists(),
      });
    },
  });
}

/**
 * Delete a learning path
 */
export function useDeleteLearningPath() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (learningPathId: number) => deleteLearningPath(learningPathId),
    onSuccess: (_data, learningPathId) => {
      // Remove from cache
      queryClient.removeQueries({
        queryKey: learningPathKeys.detail(learningPathId),
      });
      // Invalidate the list
      queryClient.invalidateQueries({
        queryKey: learningPathKeys.lists(),
      });
    },
  });
}

/**********************************************************************
 * CONCEPT QUERIES
 * TODO: This concept endpoints need to be moved to a separate module
 **********************************************************************/

/**
 * Fetch all concepts
 */
export function useConcepts() {
  return useQuery({
    queryKey: conceptKeys.lists(),
    queryFn: () => listConcepts(),
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}

/**
 * Fetch a single concept by ID
 */
export function useConcept(conceptId: string | null) {
  return useQuery({
    queryKey: conceptKeys.detail(conceptId || ""),
    queryFn: () => getConcept(conceptId!),
    enabled: !!conceptId,
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}

/**
 * Fetch prerequisites for a concept
 */
export function useConceptPrerequisites(conceptId: string | null) {
  return useQuery({
    queryKey: conceptKeys.prerequisites(conceptId || ""),
    queryFn: () => getConceptPrerequisites(conceptId!),
    enabled: !!conceptId,
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}

/**
 * Create a new concept
 */
export function useCreateConcept() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (params: ConceptCreate) => createConcept(params),
    onSuccess: (data: ConceptResponse) => {
      // Invalidate concepts list
      queryClient.invalidateQueries({
        queryKey: conceptKeys.lists(),
      });
      // Cache the new concept
      queryClient.setQueryData(conceptKeys.detail(data.id), data);
    },
  });
}

// Test endpoint

/**
 * Test parse and save learning path
 */
export function useTestParseAndSaveLearningPath() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (params: TestParseRequest) => testParseAndSaveLearningPath(params),
    onSuccess: (data: LearningPathResponse) => {
      // Invalidate learning paths list
      queryClient.invalidateQueries({
        queryKey: learningPathKeys.lists(),
      });
      // Cache the created learning path
      queryClient.setQueryData(learningPathKeys.detail(data.id), data);
    },
  });
}
