import { Box, Button, Alert, CircularProgress, Stack, Autocomplete, TextField } from "@mui/material";
import React, { useState } from "react";
import type { LearningPathResponse } from "../../learning-path/types";
import { extractConcepts } from "../../../common/util/jsonldUtil";
import { useSession } from "../../../common/hooks/useSession";
import MCQEvaluation from "./MCQEvaluation";
import { useLearningPathContext } from "../../../hooks/useLearningPathContext";

interface EvaluateIntegratorProps {
    initialPathId?: number;
}

const EvaluateIntegrator: React.FC<EvaluateIntegratorProps> = () => {
    const [selectedConcept, setSelectedConcept] = useState<{ id: string; label: string } | null>(null);
    const [isEvaluating, setIsEvaluating] = useState(false);

    const { session } = useSession();
    const userId = session?.user.id ? Number.parseInt(session.user.id, 10) : null;
    const { learningPaths, activeLearningPath, isLoading: isLoadingPaths, error: pathsError } = useLearningPathContext();



    if (!learningPaths || learningPaths.length === 0) {
        return <Alert severity="info">No learning paths available</Alert>;
    }

    const renderEvaluationUI = () => {
        if (isEvaluating && selectedConcept && activeLearningPath?.id && userId) {
            return (
                <MCQEvaluation
                    conceptName={selectedConcept.label}
                    conceptId={selectedConcept.id}
                    learningPathId={activeLearningPath.id}
                    userId={userId}
                    learningPathKg={activeLearningPath?.kg_data as Record<string, unknown>[] | null}
                    onBack={() => setIsEvaluating(false)}
                />
            );
        }

        if (isEvaluating && !userId) {
            return (
                <Alert severity="warning">
                    User information not available. Please log in.
                </Alert>
            );
        }

        return (
            <Button
                variant="contained"
                disabled={!selectedConcept}
                onClick={() => setIsEvaluating(true)}
            >
                Start Evaluation
            </Button>
        );
    };

    const renderContent = (
        selectedPathId: number | null,
        selectedPath: LearningPathResponse | undefined,
        isLoadingPath: boolean,
        pathError: Error | null
    ) => {
        if (selectedPathId === null) {
            return <Alert severity="info">Select a learning path to evaluate</Alert>;
        }

        if (isLoadingPath) {
            return (
                <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
                    <CircularProgress />
                </Box>
            );
        }

        if (pathError) {
            return (
                <Alert severity="error">
                    Error loading learning path: {pathError instanceof Error ? pathError.message : "Unknown error"}
                </Alert>
            );
        }

        if (!selectedPath) {
            return null;
        }

        const concepts = extractConcepts((selectedPath as LearningPathResponse)?.kg_data);

        return (
            <Stack spacing={2}>
                <Box>
                    <Autocomplete
                        options={concepts}
                        getOptionLabel={(opt) => opt.label}
                        renderInput={(params) => <TextField {...params} label="Select concept" variant="outlined" />}
                        value={selectedConcept}
                        onChange={(_e, value) => setSelectedConcept(value)}
                        isOptionEqualToValue={(option, value) => option.id === value.id}
                        disabled={isEvaluating}
                        sx={{ width: 400 }}
                    />
                </Box>

                <Box>
                    {renderEvaluationUI()}
                </Box>
            </Stack>
        );
    };

    return (
        <Box>
            {renderContent(activeLearningPath?.id || null, activeLearningPath, !!isLoadingPaths, pathsError || null)}
        </Box>
    );
};

export default EvaluateIntegrator;