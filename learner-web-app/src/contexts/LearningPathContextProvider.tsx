import { useState } from "react";
import { LearningPathContext } from "./LearningPathContextDef";
import { useLearningPath, useLearningPaths } from "../features/learning-path/queries";

export const LearningPathContextProvider = ({ children }: { children: React.ReactNode }) => {
    const [activeLearningPathId, setActiveLearningPathIdState] = useState<number | null>(null);

    const {
        data: learningPaths,
        isLoading: isLoadingPaths,
        error: pathsError,
    } = useLearningPaths(0, 100);

    const {
        data: selectedPath,
        isLoading: isLoadingPath,
        error: pathError,
    } = useLearningPath(activeLearningPathId, true);

    const setActiveLearningPath = (learningPathId: number | null) => {
        setActiveLearningPathIdState(learningPathId);
    }

    const clearActiveLearningPath = () => {
        setActiveLearningPathIdState(null);
    }

    // if (isLoadingPaths || isLoadingPath) {
    //     return <div>Loading learning paths...</div>;
    // }

    // if (pathsError || pathError) {
    //     return <div>Error loading learning paths: {(pathsError || pathError) instanceof Error ? (pathsError || pathError)?.message : "Unknown error"}</div>;
    // }

    return (
        <LearningPathContext.Provider value={{
            learningPaths: learningPaths || [],
            activeLearningPath: selectedPath || undefined,
            setActiveLearningPath,
            clearActiveLearningPath,
            isLoading: isLoadingPaths || isLoadingPath,
            error: pathsError || pathError || null,
        }}>
            {children}
        </LearningPathContext.Provider>
    );
}