import React, { useState } from 'react';
import { 
    Card, 
    CardContent, 
    Typography, 
    Button, 
    Radio, 
    RadioGroup, 
    FormControlLabel, 
    FormControl, 
    Alert, 
    Box,
    Avatar,
    Chip
} from '@mui/material';
import QuizIcon from '@mui/icons-material/Quiz';
import type { FeedEvaluation } from '../types';

interface FeedEvaluationCardProps {
    item: FeedEvaluation;
}

const FeedEvaluationCard: React.FC<FeedEvaluationCardProps> = ({ item }) => {
    const [selectedAnswer, setSelectedAnswer] = useState<string>("");
    const [isSubmitted, setIsSubmitted] = useState(false);

    const handleAnswerSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
        setSelectedAnswer(event.target.value);
    };

    const handleSubmit = () => {
        setIsSubmitted(true);
    };

    const isCorrect = selectedAnswer === item.correctAnswer;

    const getDifficultyColor = (difficulty: string) => {
        if (difficulty === 'Beginner') return 'success';
        if (difficulty === 'Intermediate') return 'warning';
        return 'error';
    };

    const getOptionStyles = (key: string) => {
        let borderColor = 'divider';
        let backgroundColor = 'transparent';
        let opacity = 1;

        if (isSubmitted) {
            if (key === item.correctAnswer) {
                borderColor = 'success.main';
                backgroundColor = 'success.light';
            } else if (key === selectedAnswer) {
                borderColor = 'error.main';
                backgroundColor = 'error.light';
            } else {
                opacity = 0.7;
            }
        } else if (key === selectedAnswer) {
            borderColor = 'primary.main';
            backgroundColor = 'action.selected';
        }

        return {
            mb: 1,
            p: 1,
            borderRadius: 1,
            border: '1px solid',
            borderColor,
            backgroundColor,
            opacity
        };
    };

    return (
        <Card sx={{ maxWidth: '100%', mb: 2, borderRadius: 2, boxShadow: 3 }}>
             <Box sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                <Avatar sx={{ bgcolor: 'secondary.main' }}>
                    <QuizIcon />
                </Avatar>
                <Box>
                    <Typography variant="subtitle2" color="text.secondary">
                        Quick Quiz • {item.topic}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                        Test your knowledge
                    </Typography>
                </Box>
                 <Box sx={{ ml: 'auto' }}>
                    <Chip 
                        label={item.difficulty} 
                        size="small" 
                        color={getDifficultyColor(item.difficulty)} 
                        variant="outlined" 
                    />
                </Box>
            </Box>

            <CardContent>
                <Typography variant="h6" gutterBottom>
                    {item.question}
                </Typography>

                <FormControl component="fieldset" sx={{ width: '100%', mt: 1 }}>
                    <RadioGroup value={selectedAnswer} onChange={handleAnswerSelect}>
                        {Object.entries(item.options).map(([key, value]) => (
                            <FormControlLabel
                                key={key}
                                value={key}
                                control={<Radio />}
                                label={value}
                                disabled={isSubmitted}
                                sx={getOptionStyles(key)}
                            />
                        ))}
                    </RadioGroup>
                </FormControl>

                {isSubmitted && (
                    <Alert 
                        severity={isCorrect ? "success" : "info"}
                        sx={{ mt: 2 }}
                    >
                        <Typography variant="subtitle2" gutterBottom>
                            {isCorrect ? "Correct!" : `Not quite. The correct answer is ${item.correctAnswer}.`}
                        </Typography>
                        <Typography variant="body2">
                            {item.explanation}
                        </Typography>
                    </Alert>
                )}

                {!isSubmitted && (
                    <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
                        <Button 
                            variant="contained" 
                            onClick={handleSubmit}
                            disabled={!selectedAnswer}
                        >
                            Check Answer
                        </Button>
                    </Box>
                )}
            </CardContent>
        </Card>
    );
};

export default FeedEvaluationCard;
