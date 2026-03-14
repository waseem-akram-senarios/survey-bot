import React from 'react';
import {
  Box,
  Typography,
  TextField,
} from '@mui/material';

const DateQuestion = ({ question, preview = false, questionNumber, onUpdateQuestion }) => {
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
          type={question.includeTime ? 'datetime-local' : 'date'}
          placeholder={question.includeTime ? 'Select date and time' : 'Select date'}
          variant="outlined"
          disabled={preview}
        />
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
        type={question.includeTime ? 'datetime-local' : 'date'}
        placeholder={question.includeTime ? 'Select date and time' : 'Select date'}
        variant="outlined"
        disabled={preview}
      />
    </Box>
  );
};

export default DateQuestion;
