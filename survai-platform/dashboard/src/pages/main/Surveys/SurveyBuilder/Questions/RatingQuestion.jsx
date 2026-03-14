import React from 'react';
import {
  Box,
  Typography,
  Rating,
  Slider,
} from '@mui/material';
import {
  Star,
} from '@mui/icons-material';

const RatingQuestion = ({ question, preview = false, questionNumber, onUpdateQuestion }) => {
  const scale = question.scale || 5;
  const labels = question.labels || {};

  if (preview) {
    return (
      <Box>
        <Typography variant="h6" sx={{ mb: 2 }}>
          {questionNumber && `Q${questionNumber}. `}{question.title}
          {question.required && <span style={{ color: 'red' }}> *</span>}
        </Typography>
        
        {question.description && (
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            {question.description}
          </Typography>
        )}
        
        <Box sx={{ mb: 2 }}>
          <Rating
            name={`rating-${question.id}`}
            max={scale}
            size="large"
            disabled={preview}
          />
        </Box>
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
          <Typography variant="caption" color="text.secondary">
            {labels[1] || 'Poor'}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {labels[scale] || 'Excellent'}
          </Typography>
        </Box>
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h6" sx={{ mb: 2 }}>
        {questionNumber && `Q${questionNumber}. `}{question.title}
        {question.required && <span style={{ color: 'red' }}> *</span>}
      </Typography>
      
      {question.description && (
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          {question.description}
        </Typography>
      )}
      
      <Box sx={{ mb: 2 }}>
        <Rating
          name={`rating-${question.id}`}
          max={scale}
          size="large"
          disabled={preview}
        />
      </Box>
      
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
        <Typography variant="caption" color="text.secondary">
          {labels[1] || 'Poor'}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          {labels[scale] || 'Excellent'}
        </Typography>
      </Box>
    </Box>
  );
};

export default RatingQuestion;
