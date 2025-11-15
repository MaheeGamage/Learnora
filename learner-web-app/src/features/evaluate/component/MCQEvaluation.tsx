import { 
    Box, 
    Typography, 
    Button, 
    Alert, 
    CircularProgress, 
    Stack, 
    Radio, 
    RadioGroup, 
    FormControlLabel,
    FormControl,
    Paper,
    LinearProgress
} from "@mui/material";
import React, { useState, useEffect } from "react";
import { useGenerateMCQ } from "../../agent/queries";
import { useUpdateLearningPath } from "../../learning-path/queries";
import type { MCQQuestion } from "../../agent/types";
import { buildUserKnowsConceptTriple, hasPassedEvaluation } from "../utils/kgUpdateHelper";

interface MCQEvaluationProps {
    conceptName: string;
    conceptId: string;
    learningPathId: number;
    userId: number;
    learningPathKg?: Record<string, unknown>[] | null;
    onBack: () => void;
}

const MCQEvaluation: React.FC<MCQEvaluationProps> = ({
    conceptName,
    conceptId,
    learningPathId,
    userId,
    learningPathKg,
    onBack,
}) => {
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [selectedAnswer, setSelectedAnswer] = useState<string>("");
    const [showExplanation, setShowExplanation] = useState(false);
    const [userAnswers, setUserAnswers] = useState<string[]>([]);
    const [showResults, setShowResults] = useState(false);
    const [updateSuccess, setUpdateSuccess] = useState(false);
    const [updateError, setUpdateError] = useState<string | null>(null);
    const [isUpdatingKG, setIsUpdatingKG] = useState(false);

    const { mutate: generateMCQ, isPending, data, error } = useGenerateMCQ();
    const { mutate: updateLearningPath } = useUpdateLearningPath(learningPathId);

    // Fetch questions on mount
    useEffect(() => {
        generateMCQ({
            concept_name: conceptName,
            concept_id: conceptId,
            difficulty_level: "Beginner",
            question_count: 5,
            learning_path_db_id: learningPathId,
        });
    }, [generateMCQ, conceptName, conceptId, learningPathId]);

    // Auto-update knowledge graph when user passes
    useEffect(() => {
        if (showResults && !updateSuccess && !isUpdatingKG && !updateError) {
            const score = calculateScore();
            if (hasPassedEvaluation(score)) {
                handleUpdateKnowledgeGraph();
            }
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [showResults]);

    const questions: MCQQuestion[] = data?.questions || [];
    const currentQuestion = questions[currentQuestionIndex];
    const isLastQuestion = currentQuestionIndex === questions.length - 1;

    const handleAnswerSelect = (answer: string) => {
        setSelectedAnswer(answer);
    };

    const handleSubmitAnswer = () => {
        if (!selectedAnswer) return;
        
        setShowExplanation(true);
        setUserAnswers([...userAnswers, selectedAnswer]);
    };

    const handleNext = () => {
        if (isLastQuestion) {
            // Show results after last question
            setShowResults(true);
            return;
        }
        
        setCurrentQuestionIndex(currentQuestionIndex + 1);
        setSelectedAnswer("");
        setShowExplanation(false);
    };

    const calculateScore = () => {
        if (!questions.length) return 0;
        const correct = userAnswers.filter(
            (answer, index) => answer === questions[index]?.correct_answer
        ).length;
        return Math.round((correct / questions.length) * 100);
    };

    const handleUpdateKnowledgeGraph = async () => {
        setIsUpdatingKG(true);
        setUpdateError(null);

        try {
            const userKnowsTriple = buildUserKnowsConceptTriple(userId, conceptId);
            
            // Merge existing KG data with user triplet
            const updatedKgData = learningPathKg 
                ? [...learningPathKg, userKnowsTriple]
                : [userKnowsTriple];
            
            updateLearningPath(
                { kg_data: updatedKgData },
                {
                    onSuccess: () => {
                        setUpdateSuccess(true);
                    },
                    onError: (err) => {
                        setUpdateError(
                            err instanceof Error ? err.message : "Failed to update knowledge graph"
                        );
                    },
                    onSettled: () => {
                        setIsUpdatingKG(false);
                    },
                }
            );
        } catch (err) {
            setUpdateError(err instanceof Error ? err.message : "An error occurred");
            setIsUpdatingKG(false);
        }
    };

    // Loading state
    if (isPending) {
        return (
            <Box display="flex" flexDirection="column" alignItems="center" justifyContent="center" minHeight="400px" gap={2}>
                <CircularProgress />
                <Typography variant="body1" color="text.secondary">
                    Generating questions for {conceptName}...
                </Typography>
            </Box>
        );
    }

    // Error state
    if (error) {
        return (
            <Stack spacing={2}>
                <Alert severity="error">
                    Error generating questions: {error instanceof Error ? error.message : "Unknown error"}
                </Alert>
                <Button variant="outlined" onClick={onBack}>
                    Back to Concept Selection
                </Button>
            </Stack>
        );
    }

    // No questions returned
    if (!questions.length) {
        return (
            <Stack spacing={2}>
                <Alert severity="warning">No questions were generated. Please try again.</Alert>
                <Button variant="outlined" onClick={onBack}>
                    Back to Concept Selection
                </Button>
            </Stack>
        );
    }

    // Evaluation complete - show results
    if (showResults) {
        const score = calculateScore();
        const passed = hasPassedEvaluation(score);

        return (
            <Paper elevation={2} sx={{ p: 4 }}>
                <Stack spacing={3} alignItems="center">
                    <Typography variant="h4" color="primary">
                        Evaluation Complete!
                    </Typography>
                    <Typography variant="h5">
                        Your Score: {score}%
                    </Typography>
                    <Typography variant="body1" color="text.secondary">
                        You answered {userAnswers.filter((ans, i) => ans === questions[i]?.correct_answer).length} out of {questions.length} questions correctly.
                    </Typography>

                    {passed && !updateSuccess && !isUpdatingKG && (
                        <Alert severity="info">
                            Congratulations! You passed. We're updating your knowledge graph...
                        </Alert>
                    )}

                    {updateSuccess && (
                        <Alert severity="success">
                            Success! Your knowledge graph has been updated. You now know {conceptName}!
                        </Alert>
                    )}

                    {updateError && (
                        <Alert severity="error">
                            Error updating knowledge graph: {updateError}
                        </Alert>
                    )}

                    {isUpdatingKG && (
                        <Stack direction="row" spacing={1} alignItems="center">
                            <CircularProgress size={24} />
                            <Typography variant="body2">Updating your profile...</Typography>
                        </Stack>
                    )}

                    {passed && !updateSuccess && (
                        <Button
                            variant="contained"
                            onClick={handleUpdateKnowledgeGraph}
                            disabled={isUpdatingKG}
                        >
                            {isUpdatingKG ? "Updating..." : "Update My Knowledge Graph"}
                        </Button>
                    )}

                    <Button variant="contained" onClick={onBack}>
                        Back to Concept Selection
                    </Button>
                </Stack>
            </Paper>
        );
    }

    return (
        <Stack spacing={3}>
            {/* Header */}
            <Box>
                <Typography variant="h6" gutterBottom>
                    Evaluating: {conceptName}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                    Question {currentQuestionIndex + 1} of {questions.length}
                </Typography>
                <LinearProgress 
                    variant="determinate" 
                    value={((currentQuestionIndex + 1) / questions.length) * 100} 
                    sx={{ mt: 1 }}
                />
            </Box>

            {/* Question */}
            <Paper elevation={2} sx={{ p: 3 }}>
                <Stack spacing={3}>
                    <Typography variant="h6">
                        {currentQuestion.question}
                    </Typography>

                    <FormControl component="fieldset">
                        <RadioGroup value={selectedAnswer} onChange={(e) => handleAnswerSelect(e.target.value)}>
                            {Object.entries(currentQuestion.options).map(([key, value]) => (
                                <FormControlLabel
                                    key={key}
                                    value={key}
                                    control={<Radio />}
                                    label={`${key}. ${value}`}
                                    disabled={showExplanation}
                                    sx={{
                                        mb: 1,
                                        p: 1,
                                        borderRadius: 1,
                                        backgroundColor: showExplanation
                                            ? key === currentQuestion.correct_answer
                                                ? "success.light"
                                                : key === selectedAnswer
                                                ? "error.light"
                                                : "transparent"
                                            : "transparent",
                                    }}
                                />
                            ))}
                        </RadioGroup>
                    </FormControl>

                    {/* Explanation */}
                    {showExplanation && (
                        <Alert 
                            severity={selectedAnswer === currentQuestion.correct_answer ? "success" : "error"}
                            sx={{ mt: 2 }}
                        >
                            <Typography variant="subtitle2" gutterBottom>
                                {selectedAnswer === currentQuestion.correct_answer 
                                    ? "Correct!" 
                                    : `Incorrect. The correct answer is ${currentQuestion.correct_answer}.`}
                            </Typography>
                            <Typography variant="body2">
                                {currentQuestion.explanation}
                            </Typography>
                        </Alert>
                    )}

                    {/* Action Buttons */}
                    <Box display="flex" gap={2} justifyContent="space-between">
                        <Button variant="outlined" onClick={onBack}>
                            Exit Evaluation
                        </Button>
                        
                        {!showExplanation ? (
                            <Button 
                                variant="contained" 
                                onClick={handleSubmitAnswer}
                                disabled={!selectedAnswer}
                            >
                                Submit Answer
                            </Button>
                        ) : (
                            <Button 
                                variant="contained" 
                                onClick={handleNext}
                            >
                                {isLastQuestion ? "Finish" : "Next Question"}
                            </Button>
                        )}
                    </Box>
                </Stack>
            </Paper>
        </Stack>
    );
};

export default MCQEvaluation;
