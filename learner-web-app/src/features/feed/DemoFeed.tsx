import { Box, Container, Typography, Stack } from "@mui/material";
import React from "react";
import FeedContentCard from "./components/FeedContentCard";
import FeedEvaluationCard from "./components/FeedEvaluationCard";
import type { FeedItem } from "./types";

const DUMMY_FEED_ITEMS: FeedItem[] = [
    {
        id: '1',
        type: 'content',
        title: 'Introduction to Machine Learning',
        description: 'A comprehensive guide to understanding the basics of Machine Learning, including supervised and unsupervised learning.',
        source: 'TechCrunch',
        url: 'https://techcrunch.com/',
        imageUrl: 'https://picsum.photos/seed/ml/600/300',
        topic: 'Machine Learning',
        readTime: '5 min read',
        publishedDate: '2 hours ago'
    },
    {
        id: '2',
        type: 'evaluation',
        topic: 'Python Basics',
        question: 'Which of the following is the correct file extension for Python files?',
        options: {
            A: '.pyth',
            B: '.pt',
            C: '.py',
            D: '.p'
        },
        correctAnswer: 'C',
        explanation: 'Python files are saved with the .py extension.',
        difficulty: 'Beginner'
    },
    {
        id: '3',
        type: 'content',
        title: 'Understanding React Hooks',
        description: 'Learn how to use useState, useEffect, and other built-in hooks to manage state and side effects in your functional components.',
        source: 'React Docs',
        url: 'https://react.dev/',
        imageUrl: 'https://picsum.photos/seed/react/600/300',
        topic: 'React',
        readTime: '8 min read',
        publishedDate: '5 hours ago'
    },
    {
        id: '4',
        type: 'evaluation',
        topic: 'Data Structures',
        question: 'What is the time complexity of accessing an element in an array by index?',
        options: {
            A: 'O(n)',
            B: 'O(log n)',
            C: 'O(1)',
            D: 'O(n^2)'
        },
        correctAnswer: 'C',
        explanation: 'Accessing an array element by index is a constant time operation O(1) because the memory address can be calculated directly.',
        difficulty: 'Intermediate'
    },
    {
        id: '5',
        type: 'content',
        title: 'The Future of AI Agents',
        description: 'Explore how autonomous AI agents are changing the landscape of software development and automation.',
        source: 'AI Weekly',
        url: 'https://example.com',
        imageUrl: 'https://picsum.photos/seed/ai/600/300',
        topic: 'Artificial Intelligence',
        readTime: '6 min read',
        publishedDate: '1 day ago'
    }
];

/**
 * Demo feed component
 */
const DemoFeed: React.FC = () => {
    return (
        <Container maxWidth="md">
            <Box sx={{ mb: 4 }}>
                <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
                    Your Learning Feed
                </Typography>
                <Typography variant="body1" color="text.secondary">
                    {/* Discover content and test your knowledge based on your learning path. */}
                    This is a demo feed for demosntration purposes.
                </Typography>
            </Box>

            <Stack spacing={3}>
                {DUMMY_FEED_ITEMS.map((item) => (
                    <React.Fragment key={item.id}>
                        {item.type === 'content' ? (
                            <FeedContentCard item={item} />
                        ) : item.type === 'evaluation' ? (
                            <FeedEvaluationCard item={item} />
                        ) : null}
                    </React.Fragment>
                ))}
            </Stack>
            
            <Box sx={{ mt: 4, textAlign: 'center' }}>
                <Typography variant="body2" color="text.secondary">
                    You've reached the end of your feed for now.
                </Typography>
            </Box>
        </Container>
    );
};

export default DemoFeed;