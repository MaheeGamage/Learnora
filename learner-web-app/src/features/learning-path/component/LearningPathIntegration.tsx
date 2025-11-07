/**
 * Learning Path Integration Component
 * Allows users to select a learning path from a dropdown and visualize it
 */

import { useState } from "react";
import {
  Box,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  CircularProgress,
  Alert,
  Stack,
  Typography,
} from "@mui/material";
import LearningPathVisualization from "./LearningPathVisualization";
import { useLearningPaths, useLearningPath } from "../queries";
import type { JsonLdDocument } from "jsonld";
import type { LearningPathResponse } from "../types";

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
        <LearningPathVisualization
          jsonldData={selectedPath.kg_data as JsonLdDocument}
          height="600px"
          width="100%"
        />
      ) : (
        <Alert severity="info">No knowledge graph data available for this learning path</Alert>
      )}
    </Stack>
  );
}

const LearningPathIntegration: React.FC<LearningPathIntegrationProps> = ({
  initialPathId,
}) => {
  const [selectedPathId, setSelectedPathId] = useState<number | null>(
    initialPathId || null
  );

  const {
    data: learningPaths,
    isLoading: isLoadingPaths,
    error: pathsError,
  } = useLearningPaths(0, 100);

  const {
    data: selectedPath,
    isLoading: isLoadingPath,
    error: pathError,
  } = useLearningPath(selectedPathId, true);

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

  if (!learningPaths || learningPaths.length === 0) {
    return <Alert severity="info">No learning paths available</Alert>;
  }

  return (
    <Box>
      <FormControl fullWidth sx={{ mb: 2 }}>
        <InputLabel>Select Learning Path</InputLabel>
        <Select
          value={selectedPathId || ""}
          label="Select Learning Path"
          onChange={(e) => setSelectedPathId(Number(e.target.value))}
        >
          {learningPaths.map((path) => (
            <MenuItem key={path.id} value={path.id}>
              <Box>
                <Typography variant="body2" fontWeight="600">
                  {path.topic}
                </Typography>
                <Typography variant="caption" display="block">
                  ID: {path.id} • {new Date(path.created_at).toLocaleDateString()}
                </Typography>
              </Box>
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      {renderContent(selectedPathId, selectedPath, isLoadingPath, pathError)}
    </Box>
  );
};

export default LearningPathIntegration;
