import React from 'react';
import {
  Box,
  Typography,
  Switch,
  FormControlLabel,
  TextField,
  Button,
  IconButton,
  Divider,
} from '@mui/material';
import {
  Add,
  Delete,
} from '@mui/icons-material';

const MultipleChoiceProperties = ({ question, onUpdateQuestion }) => {
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
      <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600 }}>
        Multiple Choice Options
      </Typography>

      <FormControlLabel
        control={
          <Switch
            checked={question.allowMultiple || false}
            onChange={(e) => onUpdateQuestion(question.id, { allowMultiple: e.target.checked })}
          />
        }
        label="Allow multiple selections"
        sx={{ mb: 3, display: 'flex', flexDirection: 'row-reverse', justifyContent: 'space-between' }}
      />

      <FormControlLabel
        control={
          <Switch
            checked={question.randomizeOptions || false}
            onChange={(e) => onUpdateQuestion(question.id, { randomizeOptions: e.target.checked })}
          />
        }
        label="Randomize option order"
        sx={{ mb: 3, display: 'flex', flexDirection: 'row-reverse', justifyContent: 'space-between' }}
      />

      <Divider sx={{ mb: 2 }} />

      <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600 }}>
        Answer Options
      </Typography>

      {question.options?.map((option, index) => (
        <Box key={option.id} sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Typography variant="body2" sx={{ mr: 1, minWidth: 20 }}>
            {index + 1}.
          </Typography>
          <TextField
            value={option.text}
            onChange={(e) => handleOptionTextChange(option.id, e.target.value)}
            variant="outlined"
            size="small"
            sx={{ flex: 1, mr: 1 }}
            placeholder="Option text"
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

      <Button
        startIcon={<Add />}
        onClick={handleAddOption}
        sx={{ mt: 1, borderRadius: 2 }}
        variant="outlined"
        fullWidth
      >
        Add Option
      </Button>

      <Typography variant="caption" color="text.secondary" sx={{ mt: 2, display: 'block' }}>
        Minimum 2 options required. Maximum 10 options recommended.
      </Typography>
    </Box>
  );
};

export default MultipleChoiceProperties;
