import {
    CheckCircle as CheckCircleIcon,
    Lightbulb as LightbulbIcon,
    PlayCircle as PlayCircleIcon,
    Schedule as ScheduleIcon,
    StarBorder as StarBorderIcon,
    Star as StarIcon,
    TaskAlt as TaskAltIcon,
    AutoAwesome as TipsIcon
} from '@mui/icons-material';
import { Box, Chip, Collapse, IconButton, Paper, Rating, Snackbar, Tooltip, Typography } from '@mui/material';
import { useState } from 'react';
import type { SearchResultItem } from './contentDiscoveryService';
import { trackInteraction } from './preferencesService';
import { useSession } from '../../common/hooks/useSession';

interface ContentCardProps {
    result: SearchResultItem;
    onSelect?: (result: SearchResultItem) => void;
}

const DIFFICULTY_COLORS = {
    beginner: { bgcolor: 'success.light', color: 'success.dark' },
    intermediate: { bgcolor: 'info.light', color: 'info.dark' },
    advanced: { bgcolor: 'secondary.light', color: 'secondary.dark' },
    expert: { bgcolor: 'error.light', color: 'error.dark' },
};

const CONTENT_TYPE_ICONS: Record<string, string> = {
    article: '📄',
    video: '🎥',
    tutorial: '📚',
    course: '🎓',
    documentation: '📖',
    blog: '✍️',
    default: '📌',
};

export default function ContentCard({ result, onSelect }: ContentCardProps) {
    const { session } = useSession();
    const { content, relevance_score, personalized_summary, tldr, key_takeaways, highlights, estimated_time } = result;
    const difficultyColor = DIFFICULTY_COLORS[content.difficulty as keyof typeof DIFFICULTY_COLORS] || { bgcolor: 'grey.200', color: 'grey.800' };
    const icon = CONTENT_TYPE_ICONS[content.content_type.toLowerCase()] || CONTENT_TYPE_ICONS.default;
    const [clickTime] = useState(Date.now());
    const [showTracked, setShowTracked] = useState(false);
    const [showPersonalization, setShowPersonalization] = useState(true);
    const [userRating, setUserRating] = useState<number | null>(null);
    const [showRatingSuccess, setShowRatingSuccess] = useState(false);
    const [isCompleted, setIsCompleted] = useState(false);
    const [showCompletedSuccess, setShowCompletedSuccess] = useState(false);

    const hasPersonalization = Boolean(personalized_summary || tldr || key_takeaways || highlights);

    const handleComplete = async (event: React.SyntheticEvent) => {
        event.stopPropagation(); // Prevent card click

        if (!session?.access_token || isCompleted) return;

        setIsCompleted(true);

        try {
            await trackInteraction({
                content_id: content.id,
                interaction_type: 'completed',
                content_title: content.title,
                content_type: content.content_type,
                content_difficulty: content.difficulty,
                content_duration_minutes: content.duration_minutes,
                content_tags: content.tags,
                duration_seconds: Math.floor((Date.now() - clickTime) / 1000),
                completion_percentage: 100,
            }, session.access_token);

            setShowCompletedSuccess(true);
        } catch (error) {
            console.error('Failed to mark as complete:', error);
            setIsCompleted(false); // Revert on error
        }
    };

    const handleRating = async (event: React.SyntheticEvent, newValue: number | null) => {
        event.stopPropagation(); // Prevent card click

        if (!session?.access_token || newValue === null) return;

        setUserRating(newValue);

        try {
            await trackInteraction({
                content_id: content.id,
                interaction_type: 'rated',
                content_title: content.title,
                content_type: content.content_type,
                content_difficulty: content.difficulty,
                content_duration_minutes: content.duration_minutes,
                content_tags: content.tags,
                duration_seconds: 0,
                completion_percentage: 0,
                rating: newValue,
            }, session.access_token);

            setShowRatingSuccess(true);
        } catch (error) {
            console.error('Failed to save rating:', error);
        }
    };

    const handleClick = async () => {
        // Track interaction
        if (session?.access_token) {
            const durationSeconds = Math.floor((Date.now() - clickTime) / 1000);

            try {
                await trackInteraction({
                    content_id: content.id,
                    interaction_type: 'clicked',
                    content_title: content.title,
                    content_type: content.content_type,
                    content_difficulty: content.difficulty,
                    content_duration_minutes: content.duration_minutes,
                    content_tags: content.tags,
                    duration_seconds: durationSeconds,
                    completion_percentage: 0,
                }, session.access_token);

                // Show tracking confirmation
                setShowTracked(true);
            } catch (error) {
                console.error('Failed to track interaction:', error);
            }
        }

        if (onSelect) {
            onSelect(result);
        } else {
            window.open(content.url, '_blank', 'noopener,noreferrer');
        }
    };

    return (
        <>
            <Paper
                onClick={handleClick}
                elevation={1}
                sx={{
                    p: 3,
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                    '&:hover': {
                        boxShadow: 8,
                        borderColor: 'primary.main',
                    },
                    border: 1,
                    borderColor: 'divider',
                }}
            >
                {/* Header */}
                <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', mb: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1.5, flex: 1 }}>
                        <Typography variant="h4" component="span">
                            {icon}
                        </Typography>
                        <Box sx={{ flex: 1 }}>
                            <Typography
                                variant="h6"
                                sx={{
                                    fontWeight: 600,
                                    overflow: 'hidden',
                                    textOverflow: 'ellipsis',
                                    display: '-webkit-box',
                                    WebkitLineClamp: 2,
                                    WebkitBoxOrient: 'vertical',
                                    transition: 'color 0.2s',
                                    '&:hover': {
                                        color: 'primary.main',
                                    },
                                }}
                            >
                                {content.title}
                            </Typography>
                            <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5 }}>
                                {content.source}
                            </Typography>
                        </Box>
                    </Box>

                    {/* Relevance Score */}
                    <Box
                        sx={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: 0.5,
                            bgcolor: 'primary.light',
                            px: 1,
                            py: 0.5,
                            borderRadius: 1,
                        }}
                    >
                        <StarIcon sx={{ fontSize: 16, color: 'primary.main' }} />
                        <Typography variant="caption" fontWeight="medium" color="primary.main">
                            {(relevance_score * 100).toFixed(0)}%
                        </Typography>
                    </Box>
                </Box>

                {/* Description */}
                <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{
                        mb: 2,
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        display: '-webkit-box',
                        WebkitLineClamp: 3,
                        WebkitBoxOrient: 'vertical',
                    }}
                >
                    {content.description}
                </Typography>

                {/* 🆕 Personalized Content Section */}
                {hasPersonalization && (
                    <Collapse in={showPersonalization}>
                        <Box sx={{ mb: 2, p: 2, bgcolor: 'background.default', borderRadius: 1, border: 1, borderColor: 'divider' }}>
                            {/* TL;DR */}
                            {tldr && (
                                <Box sx={{ mb: 2, p: 1.5, bgcolor: 'info.light', borderRadius: 1, borderLeft: 3, borderColor: 'info.main', opacity: 0.9 }}>
                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                                        <TipsIcon sx={{ fontSize: 18, color: 'info.dark' }} />
                                        <Typography variant="caption" fontWeight="bold" color="info.dark">
                                            TL;DR
                                        </Typography>
                                    </Box>
                                    <Typography variant="body2" sx={{ fontStyle: 'italic', color: 'text.primary' }}>
                                        {tldr}
                                    </Typography>
                                </Box>
                            )}

                            {/* Personalized Summary */}
                            {personalized_summary && (
                                <Box sx={{ mb: 2 }}>
                                    <Typography variant="caption" fontWeight="bold" color="text.secondary" sx={{ mb: 0.5, display: 'block' }}>
                                        📝 Summary
                                    </Typography>
                                    <Typography variant="body2" color="text.primary">
                                        {personalized_summary}
                                    </Typography>
                                </Box>
                            )}

                            {/* Key Takeaways */}
                            {key_takeaways && key_takeaways.length > 0 && (
                                <Box sx={{ mb: 2 }}>
                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 1 }}>
                                        <LightbulbIcon sx={{ fontSize: 16, color: 'warning.main' }} />
                                        <Typography variant="caption" fontWeight="bold" color="text.secondary">
                                            Key Takeaways
                                        </Typography>
                                    </Box>
                                    <Box component="ul" sx={{ m: 0, pl: 2.5 }}>
                                        {key_takeaways.map((takeaway, idx) => (
                                            <Typography key={idx} component="li" variant="body2" sx={{ mb: 0.5 }}>
                                                {takeaway}
                                            </Typography>
                                        ))}
                                    </Box>
                                </Box>
                            )}

                            {/* Video Highlights */}
                            {highlights && highlights.length > 0 && (
                                <Box>
                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 1 }}>
                                        <PlayCircleIcon sx={{ fontSize: 16, color: 'success.main' }} />
                                        <Typography variant="caption" fontWeight="bold" color="text.secondary">
                                            Key Moments
                                        </Typography>
                                    </Box>
                                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                                        {highlights.map((highlight, idx) => (
                                            <Chip
                                                key={idx}
                                                label={`${highlight.timestamp} - ${highlight.topic}`}
                                                size="small"
                                                sx={{
                                                    bgcolor: 'success.light',
                                                    color: 'success.dark',
                                                    fontSize: '0.7rem',
                                                    opacity: 0.9,
                                                    '&:hover': {
                                                        opacity: 1,
                                                    },
                                                }}
                                                title={highlight.description}
                                            />
                                        ))}
                                    </Box>
                                </Box>
                            )}
                        </Box>
                    </Collapse>
                )}

                {/* Tags */}
                {content.tags && content.tags.length > 0 && (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                        {content.tags.slice(0, 5).map((tag) => (
                            <Chip key={tag} label={tag} size="small" variant="outlined" />
                        ))}
                        {content.tags.length > 5 && (
                            <Chip
                                label={`+${content.tags.length - 5} more`}
                                size="small"
                                variant="outlined"
                                sx={{ color: 'text.secondary' }}
                            />
                        )}
                    </Box>
                )}

                {/* Footer */}
                <Box
                    sx={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        pt: 2,
                        borderTop: 1,
                        borderColor: 'divider',
                        flexWrap: 'wrap',
                        gap: 2,
                    }}
                >
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                        <Chip
                            label={content.difficulty}
                            size="small"
                            sx={{
                                bgcolor: difficultyColor.bgcolor,
                                color: difficultyColor.color,
                                fontWeight: 'medium',
                            }}
                        />
                        <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'capitalize' }}>
                            {content.content_type}
                        </Typography>
                    </Box>

                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        {/* 🆕 Rating Component */}
                        <Tooltip title="Rate this content">
                            <Box onClick={(e) => e.stopPropagation()}>
                                <Rating
                                    name={`rating-${content.id}`}
                                    value={userRating}
                                    onChange={handleRating}
                                    size="small"
                                    icon={<StarIcon fontSize="inherit" />}
                                    emptyIcon={<StarBorderIcon fontSize="inherit" />}
                                    sx={{
                                        '& .MuiRating-iconFilled': {
                                            color: 'warning.main',
                                        },
                                        '& .MuiRating-iconHover': {
                                            color: 'warning.light',
                                        },
                                    }}
                                />
                            </Box>
                        </Tooltip>

                        {/* 🆕 Mark as Complete Button */}
                        <Tooltip title={isCompleted ? "Completed! ✓" : "Mark as complete"}>
                            <span>
                                <IconButton
                                    onClick={handleComplete}
                                    disabled={isCompleted}
                                    size="small"
                                    sx={{
                                        color: isCompleted ? 'success.main' : 'action.active',
                                        '&:hover': {
                                            bgcolor: isCompleted ? 'transparent' : 'success.light',
                                        },
                                        '&.Mui-disabled': {
                                            color: 'success.main',
                                        }
                                    }}
                                >
                                    <TaskAltIcon fontSize="small" />
                                </IconButton>
                            </span>
                        </Tooltip>

                        {(estimated_time || content.duration_minutes > 0) && (
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, color: 'text.secondary' }}>
                                <ScheduleIcon sx={{ fontSize: 16 }} />
                                <Typography variant="caption">
                                    {estimated_time || content.duration_minutes} min
                                    {estimated_time && estimated_time !== content.duration_minutes && (
                                        <Typography
                                            component="span"
                                            variant="caption"
                                            sx={{ ml: 0.5, color: 'success.main', fontWeight: 'medium' }}
                                            title="Adjusted for your level"
                                        >
                                            (adjusted)
                                        </Typography>
                                    )}
                                </Typography>
                            </Box>
                        )}
                    </Box>
                </Box>
            </Paper>

            {/* Tracking Confirmation Snackbar */}
            <Snackbar
                open={showTracked}
                autoHideDuration={2000}
                onClose={() => setShowTracked(false)}
                message={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <CheckCircleIcon sx={{ fontSize: 18 }} />
                        <span>Interaction tracked! View in Preferences</span>
                    </Box>
                }
                anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
            />

            {/* 🆕 Rating Success Snackbar */}
            <Snackbar
                open={showRatingSuccess}
                autoHideDuration={2000}
                onClose={() => setShowRatingSuccess(false)}
                message={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <StarIcon sx={{ fontSize: 18, color: 'warning.main' }} />
                        <span>Rating saved! This helps improve your recommendations</span>
                    </Box>
                }
                anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
            />

            {/* 🆕 Completion Success Snackbar */}
            <Snackbar
                open={showCompletedSuccess}
                autoHideDuration={3000}
                onClose={() => setShowCompletedSuccess(false)}
                message={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <TaskAltIcon sx={{ fontSize: 18, color: 'success.main' }} />
                        <span>Content completed! Knowledge graph, learning path, and assessment updated 🎉</span>
                    </Box>
                }
                anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
            />
        </>
    );
}
