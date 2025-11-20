/**
 * Learning Path Integration Component
 * Allows users to select a learning path from a dropdown and visualize it
 */

import { Box, CircularProgress, Alert, Stack, Typography, Button } from "@mui/material";
import { useStartChat } from "../../agent/queries";
import { AgentMode } from "../../agent/types";
import { useChatContext } from "../../../hooks/useChatContext";
import type { JsonLdDocument } from "jsonld";
import type { LearningPathResponse } from "../types";
import LearningPathFlow from "./LearningPathFlow";
import { useLearningPathContext } from "../../../hooks/useLearningPathContext";

interface LearningPathIntegrationProps {
  initialPathId?: number;
}

function renderContent(
  selectedPathId: number | null,
  selectedPath: LearningPathResponse | undefined,
  isLoadingPath: boolean,
  pathError: Error | null
) {
  if (selectedPathId === null) {
    return <Alert severity="info">Select a learning path to visualize</Alert>;
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

  return (
    <Stack spacing={2}>
      <Box>
        <Typography variant="h5">{selectedPath.topic}</Typography>
        <Typography variant="body2" color="textSecondary">
          ID: {selectedPath.id} • User ID: {selectedPath.user_id}
        </Typography>
        {selectedPath.graph_uri && (
          <Typography variant="caption" display="block">
            Graph URI: {selectedPath.graph_uri}
          </Typography>
        )}
      </Box>
      {selectedPath.kg_data ? (
        <LearningPathFlow jsonldData={selectedPath.kg_data as JsonLdDocument} />
      ) : (
        <Alert severity="info">No knowledge graph data available for this learning path</Alert>
      )}
    </Stack>
  );
}

const LearningPathIntegration: React.FC<LearningPathIntegrationProps> = () => {
  const { clearActiveThread, setActiveThreadId } = useChatContext();
  const startChatMutation = useStartChat();
  const { learningPaths, activeLearningPath, isLoading: isLoadingPaths, error: pathsError } = useLearningPathContext();

  const handleCreateNewPath = () => {
    // Clear any existing thread to start fresh
    clearActiveThread();

    // Start a new chat session with LPP mode
    // User can type their learning topic in the chat window
    startChatMutation.mutate(
      {
        // message: "I want to create a new learning path",
        mode: AgentMode.LPP,
      },
      {
        onSuccess: (data) => {
          // Store the new thread ID in context
          setActiveThreadId(data.thread_id);
        },
      }
    );
  };

  if (isLoadingPaths) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="300px">
        <CircularProgress />
      </Box>
    );
  }

  if (pathsError) {
    return (
      <Alert severity="error">
        Error loading learning paths: {pathsError instanceof Error ? pathsError.message : "Unknown error"}
      </Alert>
    );
  }

  return (
    <Box>
      <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 2 }}>
        <Typography variant="h4" component="h1" gutterBottom>Learning Paths</Typography>
        <Button
          variant="contained"
          // startIcon={<AddIcon />}
          onClick={handleCreateNewPath}
        >
          Create New Path
        </Button>
      </Box>

      {!learningPaths || learningPaths.length === 0 ? (
        <Alert severity="info">No learning paths available</Alert>
      ) : (
        <>
          {renderContent(activeLearningPath?.id || null, activeLearningPath, !!isLoadingPaths, pathsError || null)}
        </>
      )}
    </Box>
  );
};

export default LearningPathIntegration;
