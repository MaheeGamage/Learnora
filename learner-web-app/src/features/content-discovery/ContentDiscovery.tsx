import {
    Close as CloseIcon,
    Error as ErrorIcon,
    AutoAwesome as PersonalizeIcon,
    Rocket as RocketIcon,
    Search as SearchIcon
} from '@mui/icons-material';
import {
    Alert,
    Box,
    Button,
    Checkbox,
    CircularProgress,
    Container,
    FormControl,
    FormControlLabel,
    IconButton,
    InputAdornment,
    InputLabel,
    MenuItem,
    Select,
    TextField,
    ToggleButton,
    ToggleButtonGroup,
    Typography
} from '@mui/material';
import { useCallback, useEffect, useState } from 'react';
import { useSession } from '../../common/hooks/useSession';
import {
    getRecommendations,
    searchContent,
    type LearningContent,
    type SearchResultItem
} from './contentDiscoveryService';
import ContentCard from './ContentCard';

const CONTENT_TYPES = ['All', 'Article', 'Video', 'Tutorial', 'Course', 'Documentation'];
const DIFFICULTY_LEVELS = ['All', 'Beginner', 'Intermediate', 'Advanced', 'Expert'];

export default function ContentDiscovery() {
    const { session } = useSession();
    const [query, setQuery] = useState('');
    const [results, setResults] = useState<SearchResultItem[]>([]);
    const [recommendations, setRecommendations] = useState<LearningContent[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [hasSearched, setHasSearched] = useState(false);

    // Future feature: Crawl UI (handlers ready, UI pending)
    // const [crawlUrl, setCrawlUrl] = useState('');
    // const [urlsList, setUrlsList] = useState<string[]>([]);
    // const [keywords, setKeywords] = useState('');
    // const [keywordsList, setKeywordsList] = useState<string[]>([]);
    // const [crawling, setCrawling] = useState(false);
    // const [success, setSuccess] = useState<string | null>(null);
    // const [stats, setStats] = useState<ContentStats | null>(null);

    // Filters
    const [contentTypeFilter, setContentTypeFilter] = useState('All');
    const [difficultyFilter, setDifficultyFilter] = useState('All');
    const [searchStrategy, setSearchStrategy] = useState<'bm25' | 'dense' | 'hybrid'>('hybrid');

    // 🆕 Personalization toggle
    const [enablePersonalization, setEnablePersonalization] = useState(true);
    const summaryWords = 150; // TODO: Add slider UI to let users adjust this

    const loadRecommendations = useCallback(async () => {
        if (!session?.access_token) {
            return;
        }

        try {
            const recs = await getRecommendations(session.access_token);
            setRecommendations(recs);
        } catch (err) {
            console.error('Failed to load recommendations:', err);
        }
    }, [session?.access_token]);

    useEffect(() => {
        loadRecommendations();
    }, [loadRecommendations]);

    const handleSearch = useCallback(async (e?: React.FormEvent) => {
        if (e) e.preventDefault();

        if (!query.trim()) {
            setError('Please enter a search query');
            return;
        }

        if (!session?.access_token) {
            setError('Please sign in to search for content');
            return;
        }

        setLoading(true);
        setError(null);
        setHasSearched(true);

        try {
            // First search with auto-discovery enabled
            // This will automatically crawl if no results found
            const response = await searchContent(
                {
                    query: query.trim(),
                    strategy: searchStrategy,
                    top_k: 4,
                    use_nlp: true,
                    auto_discover: true, // ✨ Enable auto-discovery
                    discovery_sources: ['youtube', 'medium', 'github'], // API sources
                    personalize: enablePersonalization, // 🆕 Enable personalization
                    max_summary_words: summaryWords, // 🆕 Summary length
                },
                session.access_token
            );

            setResults(response.results);

            // Show info if content was auto-discovered
            if (response.stats.total_indexed > 0 && response.results.length === 0) {
                setError('No relevant content found. Try different keywords or add custom content via browser console.');
            }
        } catch (err) {
            if (err instanceof Error) {
                if (err.message.includes('Unauthorized') || err.message.includes('401')) {
                    setError('Your session has expired. Please sign in again.');
                } else {
                    setError(err.message);
                }
            } else {
                setError('Search failed');
            }
        } finally {
            setLoading(false);
        }
    }, [query, searchStrategy, session, enablePersonalization, summaryWords]);

    const handleClearSearch = () => {
        setQuery('');
        setResults([]);
        setHasSearched(false);
        setError(null);
        setContentTypeFilter('All');
        setDifficultyFilter('All');
    };

    const filteredResults = results.filter((result) => {
        const matchesContentType =
            contentTypeFilter === 'All' ||
            result.content.content_type.toLowerCase() === contentTypeFilter.toLowerCase();

        const matchesDifficulty =
            difficultyFilter === 'All' ||
            result.content.difficulty.toLowerCase() === difficultyFilter.toLowerCase();

        return matchesContentType && matchesDifficulty;
    });

    return (
        <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
            {/* Hero Section with Search */}
            <Box
                sx={{
                    background: 'linear-gradient(135deg, #1976d2 0%, #5e35b1 50%, #7b1fa2 100%)',
                    color: 'white',
                    py: 8,
                    px: 3,
                }}
            >
                <Container maxWidth="lg">
                    <Box sx={{ textAlign: 'center', mb: 4 }}>
                        <Typography variant="h3" fontWeight="bold" gutterBottom>
                            Discover Learning Content
                        </Typography>
                        <Typography variant="h6" sx={{ color: 'rgba(255, 255, 255, 0.9)' }}>
                            AI-powered search to find the perfect resources for your learning journey
                        </Typography>
                    </Box>

                    {/* Search Bar */}
                    <Box component="form" onSubmit={handleSearch}>
                        <TextField
                            fullWidth
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            placeholder="What would you like to learn today? (e.g., React hooks, Python data analysis)"
                            variant="outlined"
                            sx={{
                                bgcolor: 'background.paper',
                                borderRadius: 3,
                                '& .MuiOutlinedInput-root': {
                                    fontSize: '1.125rem',
                                },
                            }}
                            InputProps={{
                                startAdornment: (
                                    <InputAdornment position="start">
                                        <SearchIcon />
                                    </InputAdornment>
                                ),
                                endAdornment: query && (
                                    <InputAdornment position="end">
                                        <IconButton onClick={handleClearSearch} edge="end">
                                            <CloseIcon />
                                        </IconButton>
                                        <Button
                                            type="submit"
                                            variant="contained"
                                            disabled={loading || !query.trim()}
                                            sx={{ ml: 1 }}
                                        >
                                            {loading ? 'Searching...' : 'Search'}
                                        </Button>
                                    </InputAdornment>
                                ),
                            }}
                        />
                        {!query && (
                            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 1 }}>
                                <Button
                                    type="submit"
                                    variant="contained"
                                    disabled={loading || !query.trim()}
                                >
                                    {loading ? 'Searching...' : 'Search'}
                                </Button>
                            </Box>
                        )}
                    </Box>

                    {/* Search Strategy Toggle */}
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1, mt: 2 }}>
                        <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.9)' }}>
                            Search mode:
                        </Typography>
                        <ToggleButtonGroup
                            value={searchStrategy}
                            exclusive
                            onChange={(_, value) => value && setSearchStrategy(value)}
                            size="small"
                        >
                            <ToggleButton value="bm25" sx={{ color: 'white', borderColor: 'rgba(255, 255, 255, 0.3)' }}>
                                BM25
                            </ToggleButton>
                            <ToggleButton value="dense" sx={{ color: 'white', borderColor: 'rgba(255, 255, 255, 0.3)' }}>
                                Dense
                            </ToggleButton>
                            <ToggleButton value="hybrid" sx={{ color: 'white', borderColor: 'rgba(255, 255, 255, 0.3)' }}>
                                Hybrid
                            </ToggleButton>
                        </ToggleButtonGroup>
                    </Box>

                    {/* 🆕 Personalization Toggle */}
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 2, mt: 1 }}>
                        <FormControlLabel
                            control={
                                <Checkbox
                                    checked={enablePersonalization}
                                    onChange={(e) => setEnablePersonalization(e.target.checked)}
                                    sx={{
                                        color: 'rgba(255, 255, 255, 0.7)',
                                        '&.Mui-checked': {
                                            color: 'white',
                                        },
                                    }}
                                />
                            }
                            label={
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                    <PersonalizeIcon sx={{ fontSize: 18 }} />
                                    <Typography variant="body2">
                                        Personalize results (AI summaries & highlights)
                                    </Typography>
                                </Box>
                            }
                            sx={{ color: 'rgba(255, 255, 255, 0.9)' }}
                        />
                    </Box>
                </Container>
            </Box>

            {/* Main Content */}
            <Container maxWidth="xl" sx={{ py: 4 }}>
                {/* Error State */}
                {error && (
                    <Alert severity="error" icon={<ErrorIcon />} sx={{ mb: 3 }}>
                        {error}
                    </Alert>
                )}

                {/* 🆕 Personalization Info */}
                {enablePersonalization && hasSearched && results.length > 0 && (
                    <Alert severity="info" sx={{ mb: 3 }}>
                        <Typography variant="body2">
                            🎯 <strong>AI Personalization Active:</strong> Results include level-appropriate summaries, key takeaways, and video highlights tailored to your learning profile.
                        </Typography>
                    </Alert>
                )}

                {/* Filters & Results */}
                {hasSearched && results.length > 0 && (
                    <Box sx={{ mb: 3 }}>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: 2, mb: 3 }}>
                            <Typography variant="body2" fontWeight="medium">
                                Filter by:
                            </Typography>

                            {/* Content Type Filter */}
                            <FormControl size="small" sx={{ minWidth: 150 }}>
                                <InputLabel>Content Type</InputLabel>
                                <Select
                                    value={contentTypeFilter}
                                    onChange={(e) => setContentTypeFilter(e.target.value)}
                                    label="Content Type"
                                >
                                    {CONTENT_TYPES.map((type) => (
                                        <MenuItem key={type} value={type}>
                                            {type === 'All' ? 'All Types' : type}
                                        </MenuItem>
                                    ))}
                                </Select>
                            </FormControl>

                            {/* Difficulty Filter */}
                            <FormControl size="small" sx={{ minWidth: 150 }}>
                                <InputLabel>Difficulty</InputLabel>
                                <Select
                                    value={difficultyFilter}
                                    onChange={(e) => setDifficultyFilter(e.target.value)}
                                    label="Difficulty"
                                >
                                    {DIFFICULTY_LEVELS.map((level) => (
                                        <MenuItem key={level} value={level}>
                                            {level === 'All' ? 'All Levels' : level}
                                        </MenuItem>
                                    ))}
                                </Select>
                            </FormControl>

                            <Typography variant="body2" color="text.secondary" sx={{ ml: 'auto' }}>
                                {filteredResults.length} result{filteredResults.length !== 1 ? 's' : ''}
                            </Typography>
                        </Box>
                    </Box>
                )}

                {/* Search Results */}
                {hasSearched && (
                    <Box>
                        {loading ? (
                            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', py: 8 }}>
                                <CircularProgress size={64} sx={{ mb: 2 }} />
                                <Typography color="text.secondary">
                                    Searching for the best content...
                                </Typography>
                            </Box>
                        ) : filteredResults.length > 0 ? (
                            <Box
                                sx={{
                                    display: 'grid',
                                    gridTemplateColumns: {
                                        xs: '1fr',
                                        md: 'repeat(2, 1fr)',
                                        lg: 'repeat(3, 1fr)',
                                    },
                                    gap: 3,
                                }}
                            >
                                {filteredResults.map((result) => (
                                    <ContentCard key={result.content.id} result={result} />
                                ))}
                            </Box>
                        ) : results.length > 0 ? (
                            <Box sx={{ textAlign: 'center', py: 8 }}>
                                <Typography variant="h2" sx={{ mb: 2 }}>🔍</Typography>
                                <Typography variant="h5" fontWeight="bold" gutterBottom>
                                    No results match your filters
                                </Typography>
                                <Typography color="text.secondary">
                                    Try adjusting your filters to see more results
                                </Typography>
                            </Box>
                        ) : (
                            <Box sx={{ textAlign: 'center', py: 8 }}>
                                <Typography variant="h2" sx={{ mb: 2 }}>📭</Typography>
                                <Typography variant="h5" fontWeight="bold" gutterBottom>
                                    No results found
                                </Typography>
                                <Typography color="text.secondary">
                                    Try a different search query or browse our recommendations below
                                </Typography>
                            </Box>
                        )}
                    </Box>
                )}

                {/* Recommendations Section */}
                {!hasSearched && recommendations.length > 0 && (
                    <Box>
                        <Box sx={{ mb: 3 }}>
                            <Typography variant="h4" fontWeight="bold" gutterBottom>
                                Recommended for You
                            </Typography>
                            <Typography color="text.secondary">
                                Curated content to boost your learning journey
                            </Typography>
                        </Box>
                        <Box
                            sx={{
                                display: 'grid',
                                gridTemplateColumns: {
                                    xs: '1fr',
                                    md: 'repeat(2, 1fr)',
                                    lg: 'repeat(3, 1fr)',
                                },
                                gap: 3,
                            }}
                        >
                            {recommendations.map((content) => (
                                <ContentCard
                                    key={content.id}
                                    result={{
                                        content,
                                        score: 0,
                                        relevance_score: 0.85,
                                        personalization_boost: 0,
                                    }}
                                />
                            ))}
                        </Box>
                    </Box>
                )}

                {/* Empty State - No recommendations */}
                {!hasSearched && recommendations.length === 0 && !loading && (
                    <Box sx={{ textAlign: 'center', py: 8 }}>
                        <RocketIcon sx={{ fontSize: 64, mb: 2, color: 'text.secondary' }} />
                        <Typography variant="h5" fontWeight="bold" gutterBottom>
                            Start Your Learning Journey
                        </Typography>
                        <Typography color="text.secondary" sx={{ mb: 3 }}>
                            Search for topics you want to learn and discover amazing content
                        </Typography>
                    </Box>
                )}
            </Container>
        </Box>
    );
}
