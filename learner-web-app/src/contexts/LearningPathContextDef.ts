import { createContext } from "react";
import type { LearningPathResponse } from "../features/learning-path/types";

export interface LearningPathContextType {
  learningPaths: LearningPathResponse[];
  activeLearningPath: LearningPathResponse | undefined;
  setActiveLearningPath: (learningPathId: number | null) => void;
  clearActiveLearningPath: () => void;
  isLoading?: boolean;
  error?: Error | null;
}

export const LearningPathContext = createContext<LearningPathContextType | undefined>(undefined);
