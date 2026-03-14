import React from 'react';
import {
  Box,
  Typography,
  TextField,
} from '@mui/material';

const NumberQuestion = ({ question, preview = false, questionNumber, onUpdateQuestion }) => {
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
        
        <TextField
          fullWidth
          type="number"
          placeholder={question.placeholder || 'Enter a number'}
          variant="outlined"
          disabled={preview}
          inputProps={{
            min: question.min,
            max: question.max,
            step: question.step || 1,
          }}
        />
        
        {(question.min !== undefined || question.max !== undefined) && (
          <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
            {question.min !== undefined && `Min: ${question.min}`}
            {question.min !== undefined && question.max !== undefined && ' | '}
            {question.max !== undefined && `Max: ${question.max}`}
          </Typography>
        )}
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
      
      <TextField
        fullWidth
        type="number"
        placeholder={question.placeholder || 'Enter a number'}
        variant="outlined"
        disabled={preview}
        inputProps={{
          min: question.min,
          max: question.max,
          step: question.step || 1,
        }}
      />
      
      {(question.min !== undefined || question.max !== undefined) && (
        <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
          {question.min !== undefined && `Min: ${question.min}`}
          {question.min !== undefined && question.max !== undefined && ' | '}
          {question.max !== undefined && `Max: ${question.max}`}
        </Typography>
      )}
    </Box>
  );
};

export default NumberQuestion;
