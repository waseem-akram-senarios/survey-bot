import React from 'react';
import {
  Box,
  Typography,
  TextField,
  Switch,
  FormControlLabel,
} from '@mui/material';

const TextQuestion = ({ question, preview = false, questionNumber, onUpdateQuestion }) => {
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
          multiline={question.multiline}
          rows={question.multiline ? 4 : 1}
          placeholder={question.placeholder || 'Enter your answer'}
          variant="outlined"
          disabled={preview}
          inputProps={{
            maxLength: question.maxLength,
          }}
        />
        
        {question.maxLength && (
          <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
            Maximum {question.maxLength} characters
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
        multiline={question.multiline}
        rows={question.multiline ? 4 : 1}
        placeholder={question.placeholder || 'Enter your answer'}
        variant="outlined"
        disabled={preview}
        inputProps={{
          maxLength: question.maxLength,
        }}
      />
      
      {question.maxLength && (
        <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
          Maximum {question.maxLength} characters
        </Typography>
      )}
    </Box>
  );
};

export default TextQuestion;
