import React from 'react';
import {
  Box,
  Typography,
  Slider,
  TextField,
  Switch,
  FormControlLabel,
} from '@mui/material';

const RatingProperties = ({ question, onUpdateQuestion }) => {
  const handleScaleChange = (event, newValue) => {
    onUpdateQuestion(question.id, { scale: newValue });
  };

  const handleLabelChange = (scalePoint, label) => {
    const updatedLabels = {
      ...question.labels,
      [scalePoint]: label,
    };
    onUpdateQuestion(question.id, { labels: updatedLabels });
  };

  const scale = question.scale || 5;
  const labels = question.labels || {};

  return (
    <Box>
      <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600 }}>
        Rating Scale Settings
      </Typography>

      <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
        Scale Size
      </Typography>
      
      <Slider
        value={scale}
        onChange={handleScaleChange}
        min={3}
        max={10}
        step={1}
        marks={[
          { value: 3, label: '3' },
          { value: 5, label: '5' },
          { value: 7, label: '7' },
          { value: 10, label: '10' },
        ]}
        sx={{ mb: 3 }}
      />

      <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600 }}>
        Scale Labels
      </Typography>

      <TextField
        fullWidth
        label="Lowest Label (e.g., Poor)"
        value={labels[1] || ''}
        onChange={(e) => handleLabelChange(1, e.target.value)}
        sx={{ mb: 2 }}
        size="small"
      />

      <TextField
        fullWidth
        label="Highest Label (e.g., Excellent)"
        value={labels[scale] || ''}
        onChange={(e) => handleLabelChange(scale, e.target.value)}
        sx={{ mb: 2 }}
        size="small"
      />

      <FormControlLabel
        control={
          <Switch
            checked={question.showValues || false}
            onChange={(e) => onUpdateQuestion(question.id, { showValues: e.target.checked })}
          />
        }
        label="Show numeric values"
        sx={{ mb: 2, display: 'flex', flexDirection: 'row-reverse', justifyContent: 'space-between' }}
      />

      <FormControlLabel
        control={
          <Switch
            checked={question.allowHalfStars || false}
            onChange={(e) => onUpdateQuestion(question.id, { allowHalfStars: e.target.checked })}
          />
        }
        label="Allow half-star ratings"
        sx={{ display: 'flex', flexDirection: 'row-reverse', justifyContent: 'space-between' }}
      />
    </Box>
  );
};

export default RatingProperties;
