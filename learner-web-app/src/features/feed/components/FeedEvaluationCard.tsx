import {
  Box,
  Typography,
  Button,
  Paper,
  Chip,
  Alert,
  CircularProgress,
  Radio,
  RadioGroup,
  FormControlLabel,
  FormControl,
  Stack,
  LinearProgress,
  Collapse,
} from "@mui/material";
import { useState, useEffect } from "react";
import { Quiz as QuizIcon, CheckCircle as CheckIcon } from "@mui/icons-material";
import { useGenerateMCQ } from "../../agent/queries";
import { useUpdateLearningPath } from "../../learning-path/queries";
import type { MCQQuestion } from "../../agent/types";
import { buildUserKnowsConceptTriple, hasPassedEvaluation } from "../../evaluate/utils/kgUpdateHelper";

interface FeedEvaluationCardProps {
  conceptName: string;
  conceptId: string;
  learningPathId: number;
  userId: number;
  learningPathKg?: Record<string, unknown>[] | null;
}

/**
 * Inline evaluation card for the feed
 * Allows users to take concept evaluations directly in the feed
 */
export default function FeedEvaluationCard({
  conceptName,
  conceptId,
  learningPathId,
  userId,
  learningPathKg,
}: Readonly<FeedEvaluationCardProps>) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<string>("");
  const [showExplanation, setShowExplanation] = useState(false);
  const [userAnswers, setUserAnswers] = useState<string[]>([]);
  const [showResults, setShowResults] = useState(false);
  const [updateSuccess, setUpdateSuccess] = useState(false);
  const [isUpdatingKG, setIsUpdatingKG] = useState(false);

  const { mutate: generateMCQ, isPending, data, error } = useGenerateMCQ();
  const { mutate: updateLearningPath } = useUpdateLearningPath(learningPathId);

  // Generate questions when user starts evaluation
  useEffect(() => {
    if (isExpanded && !data && !isPending) {
      generateMCQ({
        concept_name: conceptName,
        concept_id: conceptId,
        difficulty_level: "Beginner",
        question_count: 3, // Fewer questions for feed (3 instead of 5)
        learning_path_db_id: learningPathId,
      });
    }
  }, [isExpanded, data, isPending, generateMCQ, conceptName, conceptId, learningPathId]);

  // Auto-update knowledge graph when user passes
  useEffect(() => {
    if (showResults && !updateSuccess && !isUpdatingKG) {
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

  const handleStartEvaluation = () => {
    setIsExpanded(true);
  };

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
      setShowResults(true);
      return;
    }

    setCurrentQuestionIndex(currentQuestionIndex + 1);
    setSelectedAnswer("");
    setShowExplanation(false);
  };

  const calculateScore = () => {
    if (!questions.length) return 0;

    let correctCount = 0;
    userAnswers.forEach((answer, index) => {
      const question = questions[index];
      if (question && answer === question.options[question.correct_answer]) {
        correctCount++;
      }
    });

    return (correctCount / questions.length) * 100;
  };

  const handleUpdateKnowledgeGraph = async () => {
    if (!learningPathKg || isUpdatingKG) return;

    setIsUpdatingKG(true);

    try {
      const updatedKg = [...learningPathKg];
      const userKnowsTriple = buildUserKnowsConceptTriple(userId, conceptId);

      // Check if the triple already exists
      const exists = updatedKg.some(
        (item) =>
          item["@id"] === userKnowsTriple["@id"] &&
          JSON.stringify(item["http://learnora.ai/ont#knows"]) ===
            JSON.stringify(userKnowsTriple["http://learnora.ai/ont#knows"])
      );

      if (!exists) {
        updatedKg.push(userKnowsTriple);
      }

      await new Promise((resolve, reject) => {
        updateLearningPath(
          { kg_data: updatedKg },
          {
            onSuccess: () => {
              setUpdateSuccess(true);
              resolve(undefined);
            },
            onError: (err) => {
              console.error("Failed to update knowledge graph:", err);
              reject(err);
            },
          }
        );
      });
    } catch (err) {
      console.error("Error updating knowledge graph:", err);
    } finally {
      setIsUpdatingKG(false);
    }
  };

  const handleClose = () => {
    setIsExpanded(false);
    setCurrentQuestionIndex(0);
    setSelectedAnswer("");
    setShowExplanation(false);
    setUserAnswers([]);
    setShowResults(false);
    setUpdateSuccess(false);
  };

  const score = showResults ? calculateScore() : 0;
  const passed = hasPassedEvaluation(score);

  return (
    <Paper
      elevation={0}
      sx={{
        border: "2px solid",
        borderColor: isExpanded ? "primary.main" : "divider",
        borderRadius: 2,
        overflow: "hidden",
        transition: "all 0.3s ease",
      }}
    >
      {/* Collapsed State */}
      {!isExpanded && (
        <Box
          sx={{
            p: 2.5,
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            bgcolor: "primary.50",
          }}
        >
          <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
            <QuizIcon color="primary" sx={{ fontSize: 32 }} />
            <Box>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
                Test Your Knowledge
              </Typography>
              <Typography variant="h6" fontWeight={700} color="primary.main">
                {conceptName}
              </Typography>
            </Box>
          </Box>
          <Button
            variant="contained"
            startIcon={<QuizIcon />}
            onClick={handleStartEvaluation}
          >
            Start Quiz
          </Button>
        </Box>
      )}

      {/* Expanded State */}
      <Collapse in={isExpanded}>
        <Box sx={{ p: 3 }}>
          {/* Header */}
          <Box sx={{ mb: 3 }}>
            <Chip
              label={`${conceptName} Quiz`}
              color="primary"
              size="small"
              sx={{ mb: 1 }}
            />
            {!showResults && questions.length > 0 && (
              <Box sx={{ mt: 2 }}>
                <Box
                  sx={{
                    display: "flex",
                    justifyContent: "space-between",
                    mb: 1,
                  }}
                >
                  <Typography variant="caption" color="text.secondary">
                    Question {currentQuestionIndex + 1} of {questions.length}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {Math.round(
                      ((currentQuestionIndex + 1) / questions.length) * 100
                    )}
                    % Complete
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={((currentQuestionIndex + 1) / questions.length) * 100}
                  sx={{ height: 6, borderRadius: 3 }}
                />
              </Box>
            )}
          </Box>

          {/* Loading State */}
          {isPending && (
            <Box sx={{ textAlign: "center", py: 4 }}>
              <CircularProgress />
              <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                Generating quiz questions...
              </Typography>
            </Box>
          )}

          {/* Error State */}
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              Failed to generate questions. Please try again.
            </Alert>
          )}

          {/* Question Display */}
          {!isPending && !error && !showResults && currentQuestion && (
            <Stack spacing={2}>
              <Typography variant="body1" fontWeight={500}>
                {currentQuestion.question}
              </Typography>

              <FormControl component="fieldset">
                <RadioGroup
                  value={selectedAnswer}
                  onChange={(e) => handleAnswerSelect(e.target.value)}
                >
                  {Object.entries(currentQuestion.options).map(([key, option]) => (
                    <FormControlLabel
                      key={key}
                      value={option}
                      control={<Radio />}
                      label={option}
                      disabled={showExplanation}
                      sx={{
                        border: "1px solid",
                        borderColor: showExplanation
                          ? option === currentQuestion.options[currentQuestion.correct_answer]
                            ? "success.main"
                            : option === selectedAnswer
                            ? "error.main"
                            : "divider"
                          : "divider",
                        borderRadius: 1,
                        mb: 1,
                        p: 1,
                        bgcolor: showExplanation
                          ? option === currentQuestion.options[currentQuestion.correct_answer]
                            ? "success.50"
                            : option === selectedAnswer
                            ? "error.50"
                            : "transparent"
                          : "transparent",
                      }}
                    />
                  ))}
                </RadioGroup>
              </FormControl>

              {showExplanation && (
                <Alert severity="info" sx={{ mt: 2 }}>
                  <Typography variant="body2" fontWeight={600} gutterBottom>
                    Explanation:
                  </Typography>
                  <Typography variant="body2">
                    {currentQuestion.explanation}
                  </Typography>
                </Alert>
              )}

              <Box sx={{ display: "flex", gap: 2, justifyContent: "flex-end" }}>
                <Button variant="outlined" onClick={handleClose}>
                  Cancel
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
                  <Button variant="contained" onClick={handleNext}>
                    {isLastQuestion ? "See Results" : "Next Question"}
                  </Button>
                )}
              </Box>
            </Stack>
          )}

          {/* Results Display */}
          {showResults && (
            <Stack spacing={2}>
              <Box sx={{ textAlign: "center", py: 2 }}>
                {passed ? (
                  <CheckIcon sx={{ fontSize: 64, color: "success.main" }} />
                ) : (
                  <QuizIcon sx={{ fontSize: 64, color: "warning.main" }} />
                )}
                <Typography variant="h5" fontWeight={600} sx={{ mt: 2 }}>
                  {passed ? "Congratulations!" : "Keep Learning!"}
                </Typography>
                <Typography variant="h3" fontWeight={700} color="primary">
                  {score.toFixed(0)}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  You got {userAnswers.filter((ans, i) => ans === questions[i]?.correct_answer).length} out of{" "}
                  {questions.length} correct
                </Typography>
              </Box>

              {passed && updateSuccess && (
                <Alert severity="success">
                  Great job! Your progress has been saved.
                </Alert>
              )}

              {passed && isUpdatingKG && (
                <Alert severity="info">
                  Updating your progress...
                </Alert>
              )}

              {!passed && (
                <Alert severity="info">
                  You need 70% or higher to pass. Review the content and try again!
                </Alert>
              )}

              <Button variant="contained" onClick={handleClose} fullWidth>
                Continue Learning
              </Button>
            </Stack>
          )}
        </Box>
      </Collapse>
    </Paper>
  );
}
