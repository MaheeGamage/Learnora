import { Box, Container, Typography, Stack, Alert, CircularProgress, Chip, Paper } from "@mui/material";
import React, { useMemo, useState, useEffect } from "react";
import { useLearningPathContext } from "../../../hooks/useLearningPathContext";
import { extractReadyConcepts, type ConceptWithStatus } from "../../learning-path/utils/conceptStatusUtils";
import { generateFeedFromConcepts, DEFAULT_FEED_CONFIG, type FeedSearchResultItem } from "../services/feedService";
import { useSession } from "../../../common/hooks/useSession";
import ContentCard from "../../content-discovery/ContentCard";
import FeedEvaluationCard from "./FeedEvaluationCard";
import type { JsonLdDocument } from "jsonld";

/**
 * Main feed component that displays content based on ready-to-learn concepts
 */
const Feed: React.FC = () => {
  const { activeLearningPath, isLoading: isLoadingPath, error: pathError } = useLearningPathContext();
  const { session } = useSession();
  const [selectedConcepts, setSelectedConcepts] = useState<Set<string>>(new Set());
  const [feedItems, setFeedItems] = useState<FeedSearchResultItem[]>([]);
  const [isLoadingFeed, setIsLoadingFeed] = useState(false);
  const [feedError, setFeedError] = useState<string | null>(null);

  // Extract ready concepts from the active learning path
  const readyConcepts = useMemo<ConceptWithStatus[]>(() => {
    if (!activeLearningPath?.kg_data) return [];

    const kgData = activeLearningPath.kg_data as JsonLdDocument | JsonLdDocument[];
    const jsonldArray = Array.isArray(kgData) ? kgData : [kgData];
    
    return extractReadyConcepts(jsonldArray);
  }, [activeLearningPath]);

  // Preselect first 2 ready concepts on mount or when ready concepts change
  useEffect(() => {
    if (readyConcepts.length > 0) {
      const firstTwoConceptIds = new Set(readyConcepts.slice(0, 2).map(c => c.id));
      setSelectedConcepts(firstTwoConceptIds);
    }
  }, [readyConcepts]);

  // Generate feed when selected concepts change
  useEffect(() => {
    async function loadFeed() {
      if (!session?.access_token || selectedConcepts.size === 0) {
        setFeedItems([]);
        return;
      }

      setIsLoadingFeed(true);
      setFeedError(null);

      try {
        // Get selected concept objects
        const selectedConceptObjects = readyConcepts.filter(c => 
          selectedConcepts.has(c.id)
        );

        // Generate feed from selected concepts
        const result = await generateFeedFromConcepts(
          selectedConceptObjects,
          DEFAULT_FEED_CONFIG,
          session.access_token
        );

        setFeedItems(result.items);

        // Show errors if any (but don't block the feed)
        if (result.errors.length > 0) {
          console.warn('Feed generation errors:', result.errors);
        }
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Failed to generate feed';
        setFeedError(errorMessage);
        setFeedItems([]);
      } finally {
        setIsLoadingFeed(false);
      }
    }

    loadFeed();
  }, [selectedConcepts, readyConcepts, session?.access_token]);

  const handleConceptToggle = (conceptId: string) => {
    setSelectedConcepts(prev => {
      const newSet = new Set(prev);
      if (newSet.has(conceptId)) {
        newSet.delete(conceptId);
      } else {
        newSet.add(conceptId);
      }
      return newSet;
    });
  };

  if (isLoadingPath) {
    return (
      <Container maxWidth="md">
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (pathError) {
    return (
      <Container maxWidth="md">
        <Box sx={{ mt: 4 }}>
          <Alert severity="error">
            Error loading learning path: {pathError instanceof Error ? pathError.message : 'Unknown error'}
          </Alert>
        </Box>
      </Container>
    );
  }

  if (!activeLearningPath) {
    return (
      <Container maxWidth="md">
        <Box sx={{ mt: 4 }}>
          <Alert severity="info">
            No learning path selected. Please select or create a learning path to see your personalized feed.
          </Alert>
        </Box>
      </Container>
    );
  }

  if (readyConcepts.length === 0) {
    return (
      <Container maxWidth="md">
        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
            Your Learning Feed
          </Typography>
          <Typography variant="body1" color="text.secondary" gutterBottom>
            Learning path: {activeLearningPath.topic}
          </Typography>
        </Box>

        <Alert severity="info">
          No ready concepts available at the moment. You may have completed all available concepts or need to mark some prerequisites as known.
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="md">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
          Your Learning Feed
        </Typography>
        <Typography variant="body1" color="text.secondary" gutterBottom>
          Learning path: {activeLearningPath.topic}
        </Typography>
      </Box>

      {/* Ready Concepts Filter */}
      <Paper 
        elevation={0} 
        sx={{ 
          p: 1.5, 
          mb: 3, 
          bgcolor: 'background.default',
          border: '1px solid',
          borderColor: 'divider',
        }}
      >
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, alignItems: 'center' }}>
          <Typography variant="caption" color="text.secondary" sx={{ mr: 1 }}>
            Ready concepts:
          </Typography>
          {readyConcepts.map((concept) => (
            <Chip
              key={concept.id}
              label={concept.label}
              size="small"
              onClick={() => handleConceptToggle(concept.id)}
              color={selectedConcepts.has(concept.id) ? 'primary' : 'default'}
              variant={selectedConcepts.has(concept.id) ? 'filled' : 'outlined'}
              sx={{ 
                '&:hover': { 
                  bgcolor: selectedConcepts.has(concept.id) ? 'primary.dark' : 'action.hover' 
                }
              }}
            />
          ))}
        </Box>
      </Paper>

      {/* Feed Content */}
      {isLoadingFeed ? (
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
          <CircularProgress />
        </Box>
      ) : feedError ? (
        <Alert severity="error" sx={{ mb: 2 }}>
          {feedError}
        </Alert>
      ) : feedItems.length === 0 ? (
        <Alert severity="info">
          {selectedConcepts.size === 0 
            ? 'Select concepts above to see personalized content recommendations.'
            : 'No content available for the selected concepts yet. Try selecting different concepts or check back later.'}
        </Alert>
      ) : (
        <Stack spacing={3}>
          {/* Group content by concept and intersperse with evaluation cards */}
          {(() => {
            // Group items by concept
            const groupedItems = feedItems.reduce((acc, item) => {
              const conceptLabel = item.concept_label;
              if (!acc[conceptLabel]) {
                acc[conceptLabel] = [];
              }
              acc[conceptLabel].push(item);
              return acc;
            }, {} as Record<string, FeedSearchResultItem[]>);

            // Build feed with content + evaluation for each concept
            return Object.entries(groupedItems).map(([conceptLabel, items]) => {
              // Find the concept object for evaluation card
              const concept = readyConcepts.find(c => c.label === conceptLabel);
              
              return (
                <React.Fragment key={conceptLabel}>
                  {/* Content cards for this concept */}
                  {items.map((item) => (
                    <ContentCard key={item.content.id} result={item} />
                  ))}
                  
                  {/* Evaluation card after content */}
                  {concept && session && activeLearningPath && (
                    <FeedEvaluationCard
                      conceptName={concept.label}
                      conceptId={concept.id}
                      learningPathId={activeLearningPath.id}
                      userId={Number(session.user.id)}
                      learningPathKg={activeLearningPath.kg_data as Record<string, unknown>[] | null}
                    />
                  )}
                </React.Fragment>
              );
            });
          })()}
        </Stack>
      )}
    </Container>
  );
};

export default Feed;
