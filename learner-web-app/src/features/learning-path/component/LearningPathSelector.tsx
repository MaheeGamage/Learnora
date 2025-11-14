import React from "react";
import { Box, FormControl, InputLabel, MenuItem, Select, Typography } from "@mui/material";
import type { LearningPathResponse } from "../types";

interface LearningPathSelectorProps {
  learningPaths: LearningPathResponse[];
  selectedPathId: number | null;
  onChange: (id: number | null) => void;
}

const LearningPathSelector: React.FC<LearningPathSelectorProps> = ({
  learningPaths,
  selectedPathId,
  onChange,
}) => {
  return (
    <FormControl fullWidth sx={{ mb: 2 }}>
      <InputLabel id="learning-path-select-label">Select Learning Path</InputLabel>
      <Select
        labelId="learning-path-select-label"
        value={selectedPathId ?? ""}
        label="Select Learning Path"
        onChange={(e) => {
          const val = e.target.value as string | number;
          onChange(val === "" ? null : Number(val));
        }}
      >
        {learningPaths.map((path) => (
          <MenuItem key={path.id} value={path.id}>
            <Box>
              <Typography variant="body2" fontWeight={600}>
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
  );
};

export default LearningPathSelector;
