import { Box, Typography, Button, Alert, CircularProgress, Stack, Autocomplete, TextField } from "@mui/material";
import React, { useState } from "react";
import LearningPathSelector from "../../learning-path/component/LearningPathSelector";
import { useLearningPaths, useLearningPath } from "../../learning-path/queries";
import type { LearningPathResponse } from "../../learning-path/types";
import { extractConcepts } from "../../../common/util/jsonldUtil";
import MCQEvaluation from "./MCQEvaluation";

interface EvaluateIntegratorProps {
    initialPathId?: number;
}

const EvaluateIntegrator: React.FC<EvaluateIntegratorProps> = ({ initialPathId }) => {
    const [selectedPathId, setSelectedPathId] = useState<number | null>(
        initialPathId || null
    );

    const [selectedConcept, setSelectedConcept] = useState<{ id: string; label: string } | null>(null);
    const [isEvaluating, setIsEvaluating] = useState(false);

    const {
        data: learningPaths,
    } = useLearningPaths(0, 100);

    const {
        data: selectedPath,
        isLoading: isLoadingPath,
        error: pathError,
    } = useLearningPath(selectedPathId, true);

    if (!learningPaths || learningPaths.length === 0) {
        return <Alert severity="info">No learning paths available</Alert>;
    }

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

        const concepts = extractConcepts((selectedPath as any)?.kg_data);

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
                    {isEvaluating && selectedConcept && selectedPathId ? (
                        <MCQEvaluation
                            conceptName={selectedConcept.label}
                            conceptId={selectedConcept.id}
                            learningPathId={selectedPathId}
                            onBack={() => setIsEvaluating(false)}
                        />) : (
                        <Button
                            variant="contained"
                            disabled={!selectedConcept}
                            onClick={() => setIsEvaluating(true)}
                        >
                            Start Evaluation
                        </Button>
                    )}
                </Box>
            </Stack>
        );
    }

    return (
        <Box>
            <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 2 }}>
                <Typography variant="h6">Learning Paths</Typography>
            </Box>

            <LearningPathSelector
                learningPaths={learningPaths}
                selectedPathId={selectedPathId}
                onChange={(id) => {
                    if (!isEvaluating) {
                        setSelectedPathId(id);
                        setSelectedConcept(null);
                    }
                }}
            />

            {renderContent(selectedPathId, selectedPath, isLoadingPath, pathError)}
        </Box>
    );
};

export default EvaluateIntegrator;