import React from 'react';
import {
  Box,
  Typography,
  Button,
  TextField,
} from '@mui/material';
import { CloudUpload } from '@mui/icons-material';

const FileUploadQuestion = ({ question, preview = false, questionNumber, onUpdateQuestion }) => {
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
        
        <Button
          variant="outlined"
          component="label"
          startIcon={<CloudUpload />}
          sx={{ mb: 2 }}
        >
          Choose File
          <input type="file" hidden />
        </Button>
        
        <Typography variant="body2" color="text.secondary">
          {question.fileTypes ? `Accepted formats: ${question.fileTypes.join(', ')}` : 'All file types accepted'}
          {question.maxSize && ` • Max size: ${question.maxSize}MB`}
        </Typography>
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
      
      <Button
        variant="outlined"
        component="label"
        startIcon={<CloudUpload />}
        sx={{ mb: 2 }}
      >
        Choose File
        <input type="file" hidden />
      </Button>
      
      <Typography variant="body2" color="text.secondary">
        {question.fileTypes ? `Accepted formats: ${question.fileTypes.join(', ')}` : 'All file types accepted'}
        {question.maxSize && ` • Max size: ${question.maxSize}MB`}
      </Typography>
    </Box>
  );
};

export default FileUploadQuestion;
