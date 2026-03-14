import React from 'react';
import {
  Box,
  Typography,
  RadioGroup,
  FormControlLabel,
  Radio,
  TextField,
  IconButton,
  Button,
  useTheme,
} from '@mui/material';
import {
  Add,
  Delete,
  DragIndicator,
} from '@mui/icons-material';

const MultipleChoiceQuestion = ({ question, preview = false, questionNumber, onUpdateQuestion }) => {
  const theme = useTheme();

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
        
        <RadioGroup>
          {question.options?.map((option, index) => (
            <FormControlLabel
              key={option.id}
              value={option.id}
              control={<Radio />}
              label={option.text}
              sx={{ mb: 1 }}
            />
          ))}
        </RadioGroup>
      </Box>
    );
  }

  const handleOptionTextChange = (optionId, newText) => {
    const updatedOptions = question.options.map(option =>
      option.id === optionId ? { ...option, text: newText } : option
    );
    onUpdateQuestion(question.id, { options: updatedOptions });
  };

  const handleAddOption = () => {
    const newOption = {
      id: `opt-${Date.now()}`,
      text: 'New Option',
    };
    const updatedOptions = [...(question.options || []), newOption];
    onUpdateQuestion(question.id, { options: updatedOptions });
  };

  const handleDeleteOption = (optionId) => {
    if (question.options.length <= 2) return; // Keep at least 2 options
    
    const updatedOptions = question.options.filter(option => option.id !== optionId);
    onUpdateQuestion(question.id, { options: updatedOptions });
  };

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
      
      <RadioGroup>
        {question.options?.map((option, index) => (
          <Box key={option.id} sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <DragIndicator sx={{ mr: 1, color: 'text.disabled' }} />
            <Radio disabled sx={{ mr: 1 }} />
            <TextField
              value={option.text}
              onChange={(e) => handleOptionTextChange(option.id, e.target.value)}
              variant="outlined"
              size="small"
              sx={{ flex: 1, mr: 1 }}
              placeholder={`Option ${index + 1}`}
            />
            <IconButton
              size="small"
              onClick={() => handleDeleteOption(option.id)}
              disabled={question.options.length <= 2}
              color="error"
            >
              <Delete />
            </IconButton>
          </Box>
        ))}
      </RadioGroup>
      
      <Button
        startIcon={<Add />}
        onClick={handleAddOption}
        sx={{ mt: 2, borderRadius: 2 }}
        variant="outlined"
      >
        Add Option
      </Button>
    </Box>
  );
};

export default MultipleChoiceQuestion;
