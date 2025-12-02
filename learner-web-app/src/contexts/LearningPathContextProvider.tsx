import { useState, useEffect } from "react";
import { LearningPathContext } from "./LearningPathContextDef";
import { useLearningPath, useLearningPaths } from "../features/learning-path/queries";

const STORAGE_KEY = 'learnora_active_learning_path_id';

export const LearningPathContextProvider = ({ children }: { children: React.ReactNode }) => {
    const [activeLearningPathId, setActiveLearningPathIdState] = useState<number | null>(null);
    const [isHydrated, setIsHydrated] = useState<boolean>(false);

    // Load from localStorage on mount
    useEffect(() => {
        const storedPathId = localStorage.getItem(STORAGE_KEY);
        if (storedPathId) {
            setActiveLearningPathIdState(Number(storedPathId));
        }
        setIsHydrated(true);
    }, []);

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

    // Sync state updates to localStorage
    const setActiveLearningPath = (learningPathId: number | null) => {
        setActiveLearningPathIdState(learningPathId);
        if (learningPathId !== null) {
            localStorage.setItem(STORAGE_KEY, learningPathId.toString());
        } else {
            localStorage.removeItem(STORAGE_KEY);
        }
    }

    const clearActiveLearningPath = () => {
        setActiveLearningPath(null);
    }

    // if (isLoadingPaths || isLoadingPath) {
    //     return <div>Loading learning paths...</div>;
    // }

    // if (pathsError || pathError) {
    //     return <div>Error loading learning paths: {(pathsError || pathError) instanceof Error ? (pathsError || pathError)?.message : "Unknown error"}</div>;
    // }

    // Don't render children until hydrated to avoid hydration mismatch
    if (!isHydrated) {
        return null;
    }

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