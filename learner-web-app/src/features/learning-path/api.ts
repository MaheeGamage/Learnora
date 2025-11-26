import apiClient from "../../api/baseClient";
import type {
  LearningPathCreate,
  LearningPathUpdate,
  LearningPathResponse,
  ConceptCreate,
  ConceptResponse,
  TestParseRequest,
} from "./types";

/**********************************************************************
 * LEARNING PATH ENDPOINTS
 **********************************************************************/
export const createLearningPath = async (
  params: LearningPathCreate
): Promise<LearningPathResponse> => {
  const response = await apiClient.post<LearningPathResponse>(
    "/learning-paths/",
    params
  );
  return response.data;
};

export const getAllLearningPaths = async (
  skip: number = 0,
  limit: number = 100
): Promise<LearningPathResponse[]> => {
  const response = await apiClient.get<LearningPathResponse[]>(
    "/learning-paths/",
    {
      params: { skip, limit },
    }
  );
  return response.data;
};

export const getLearningPath = async (
  learningPathId: number,
  includeKg: boolean = false
): Promise<LearningPathResponse> => {
  const response = await apiClient.get<LearningPathResponse>(
    `/learning-paths/${learningPathId}`,
    {
      params: { include_kg: includeKg },
    }
  );
  return response.data;
};

export const updateLearningPath = async (
  learningPathId: number,
  params: LearningPathUpdate
): Promise<LearningPathResponse> => {
  const response = await apiClient.put<LearningPathResponse>(
    `/learning-paths/${learningPathId}`,
    params
  );
  return response.data;
};

export const deleteLearningPath = async (learningPathId: number): Promise<void> => {
  await apiClient.delete(`/learning-paths/${learningPathId}`);
};

/**********************************************************************
 * CONCEPT ENDPOINTS
 * TODO: This concept endpoints need to be moved to a separate module
 **********************************************************************/

export const listConcepts = async (): Promise<string[]> => {
  const response = await apiClient.get<string[]>("/concepts/");
  return response.data;
};

export const createConcept = async (
  params: ConceptCreate
): Promise<ConceptResponse> => {
  const response = await apiClient.post<ConceptResponse>("/concepts/", params);
  return response.data;
};

export const getConcept = async (conceptId: string): Promise<ConceptResponse> => {
  const response = await apiClient.get<ConceptResponse>(`/concepts/${conceptId}`);
  return response.data;
};

export const getConceptPrerequisites = async (
  conceptId: string
): Promise<string[]> => {
  const response = await apiClient.get<string[]>(
    `/concepts/${conceptId}/prerequisites`
  );
  return response.data;
};

// Test endpoint - parse and save learning path
export const testParseAndSaveLearningPath = async (
  params: TestParseRequest
): Promise<LearningPathResponse> => {
  const response = await apiClient.post<LearningPathResponse>(
    "/learning-paths/test/parse-and-save",
    params
  );
  return response.data;
};
