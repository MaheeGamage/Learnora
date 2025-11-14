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
import type { MCQQuestion } from "../../agent/types";

interface MCQEvaluationProps {
    conceptName: string;
    conceptId: string;
    learningPathId: number;
    onBack: () => void;
}

const MCQEvaluation: React.FC<MCQEvaluationProps> = ({
    conceptName,
    conceptId,
    learningPathId,
    onBack,
}) => {
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [selectedAnswer, setSelectedAnswer] = useState<string>("");
    const [showExplanation, setShowExplanation] = useState(false);
    const [userAnswers, setUserAnswers] = useState<string[]>([]);
    const [showResults, setShowResults] = useState(false);

    const { mutate: generateMCQ, isPending, data, error } = useGenerateMCQ();

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
