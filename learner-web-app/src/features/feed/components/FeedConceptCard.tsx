import { Box, Card, CardContent, Typography, Button, Chip, Stack } from "@mui/material";
import { useNavigate } from "react-router";
import type { FeedConcept } from "../types";
import { generateEvaluateUrl } from "../../evaluate/utils/urlUtils";

interface FeedConceptCardProps {
  item: FeedConcept;
}

/**
 * Card component for displaying ready-to-learn concepts in the feed
 */
export default function FeedConceptCard({ item }: Readonly<FeedConceptCardProps>) {
  const navigate = useNavigate();
  const { concept, learningPathId } = item;

  const handleEvaluate = () => {
    const url = generateEvaluateUrl(learningPathId, concept.id);
    navigate(url);
  };

  const handleViewContent = () => {
    // TODO: Navigate to concept content/learning materials
    console.log("View content for concept:", concept.id);
  };

  return (
    <Card
      sx={{
        borderLeft: '4px solid #2196f3',
        '&:hover': {
          boxShadow: 3,
        },
      }}
    >
      <CardContent>
        <Stack spacing={2}>
          <Box display="flex" justifyContent="space-between" alignItems="flex-start">
            <Box flex={1}>
              <Stack direction="row" spacing={1} alignItems="center" mb={1}>
                <Chip
                  label="Ready to Learn"
                  size="small"
                  sx={{
                    backgroundColor: '#e3f2fd',
                    color: '#2196f3',
                    fontWeight: 600,
                  }}
                />
                <Typography variant="caption" color="text.secondary">
                  🔓 Prerequisites met
                </Typography>
              </Stack>

              <Typography variant="h6" component="h2" gutterBottom>
                {concept.label}
              </Typography>

              {concept.prerequisites.length > 0 && (
                <Typography variant="body2" color="text.secondary">
                  Building on {concept.prerequisites.length} prerequisite
                  {concept.prerequisites.length === 1 ? '' : 's'}
                </Typography>
              )}
            </Box>
          </Box>

          <Stack direction="row" spacing={2}>
            <Button
              variant="contained"
              color="primary"
              size="small"
              onClick={handleEvaluate}
            >
              Start Learning
            </Button>
            <Button
              variant="outlined"
              size="small"
              onClick={handleViewContent}
            >
              View Content
            </Button>
          </Stack>
        </Stack>
      </CardContent>
    </Card>
  );
}
