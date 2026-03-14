import React from 'react';
import {
  Box,
  Typography,
  TextField,
  Switch,
  FormControlLabel,
  Button,
  IconButton,
} from '@mui/material';
import { Add, Delete } from '@mui/icons-material';

const DropdownProperties = ({ question, onUpdateQuestion }) => {
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
    if (question.options.length <= 1) return; // Keep at least 1 option
    
    const updatedOptions = question.options.filter(option => option.id !== optionId);
    onUpdateQuestion(question.id, { options: updatedOptions });
  };

  return (
    <Box>
      <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600 }}>
        Dropdown Options
      </Typography>

      <TextField
        fullWidth
        label="Placeholder Text"
        value={question.placeholder || 'Select an option'}
        onChange={(e) => onUpdateQuestion(question.id, { placeholder: e.target.value })}
        sx={{ mb: 2 }}
        size="small"
      />

      <FormControlLabel
        control={
          <Switch
            checked={question.allowMultiple || false}
            onChange={(e) => onUpdateQuestion(question.id, { allowMultiple: e.target.checked })}
          />
        }
        label="Allow multiple selections"
        sx={{ mb: 2, display: 'flex', flexDirection: 'row-reverse', justifyContent: 'space-between' }}
      />

      <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600 }}>
        Options
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
            disabled={question.options.length <= 1}
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
    </Box>
  );
};

export default DropdownProperties;
