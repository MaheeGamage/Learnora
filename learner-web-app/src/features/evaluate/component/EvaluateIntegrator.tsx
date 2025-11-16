import { Box, Button, Alert, CircularProgress, Stack, Autocomplete, TextField } from "@mui/material";
import React, { useState, useEffect } from "react";
import { useSearchParams, useParams } from "react-router";
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
    const [searchParams] = useSearchParams();
    const { learningPathId } = useParams<{ learningPathId: string }>();

    const { session } = useSession();
    const userId = session?.user.id ? Number.parseInt(session.user.id, 10) : null;
    const { learningPaths, activeLearningPath, setActiveLearningPath, isLoading: isLoadingPaths, error: pathsError } = useLearningPathContext();

    // Set active learning path based on URL parameter
    useEffect(() => {
        if (learningPathId) {
            const pathId = Number.parseInt(learningPathId, 10);
            if (!Number.isNaN(pathId) && pathId !== activeLearningPath?.id) {
                setActiveLearningPath(pathId);
            }
        }
    }, [learningPathId, activeLearningPath?.id, setActiveLearningPath]);

    // Pre-select concept based on URL parameter
    useEffect(() => {
        const conceptIdParam = searchParams.get('conceptId');
        
        if (conceptIdParam && activeLearningPath?.kg_data) {
            // Decode the URL-encoded concept ID
            const decodedConceptId = decodeURIComponent(conceptIdParam);
            
            // Extract concepts from the active learning path
            const concepts = extractConcepts(activeLearningPath.kg_data);
            
            // Find the concept matching the ID from URL
            const conceptToSelect = concepts.find(c => c.id === decodedConceptId);
            
            if (conceptToSelect) {
                setSelectedConcept(conceptToSelect);
            }
        }
    }, [searchParams, activeLearningPath]);

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
        // Check if URL param doesn't match active learning path
        if (learningPathId) {
            const urlPathId = Number.parseInt(learningPathId, 10);
            if (!Number.isNaN(urlPathId) && activeLearningPath?.id && urlPathId !== activeLearningPath.id) {
                return (
                    <Alert severity="warning">
                        The learning path in the URL (ID: {urlPathId}) doesn't match the active learning path (ID: {activeLearningPath.id}). 
                        Please change the learning path from the side menu.
                    </Alert>
                );
            }
        }

        if (selectedPathId === null) {
            return (
                <Alert severity="info">
                    Please select a learning path from the side menu to evaluate concepts.
                </Alert>
            );
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