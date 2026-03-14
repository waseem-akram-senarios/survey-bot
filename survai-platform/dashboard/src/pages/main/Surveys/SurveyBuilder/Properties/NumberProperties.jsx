import React from 'react';
import {
  Box,
  Typography,
  TextField,
  Switch,
  FormControlLabel,
} from '@mui/material';

const NumberProperties = ({ question, onUpdateQuestion }) => {
  return (
    <Box>
      <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600 }}>
        Number Input Settings
      </Typography>

      <TextField
        fullWidth
        label="Placeholder Text"
        value={question.placeholder || ''}
        onChange={(e) => onUpdateQuestion(question.id, { placeholder: e.target.value })}
        sx={{ mb: 2 }}
        size="small"
      />

      <TextField
        fullWidth
        type="number"
        label="Minimum Value"
        value={question.min || ''}
        onChange={(e) => onUpdateQuestion(question.id, { min: e.target.value ? parseInt(e.target.value) : null })}
        sx={{ mb: 2 }}
        size="small"
      />

      <TextField
        fullWidth
        type="number"
        label="Maximum Value"
        value={question.max || ''}
        onChange={(e) => onUpdateQuestion(question.id, { max: e.target.value ? parseInt(e.target.value) : null })}
        sx={{ mb: 2 }}
        size="small"
      />

      <TextField
        fullWidth
        type="number"
        label="Step Increment"
        value={question.step || 1}
        onChange={(e) => onUpdateQuestion(question.id, { step: e.target.value ? parseInt(e.target.value) : 1 })}
        sx={{ mb: 2 }}
        size="small"
        inputProps={{ min: 0.01, step: 0.01 }}
      />

      <FormControlLabel
        control={
          <Switch
            checked={question.allowDecimals || false}
            onChange={(e) => onUpdateQuestion(question.id, { allowDecimals: e.target.checked })}
          />
        }
        label="Allow decimal numbers"
        sx={{ display: 'flex', flexDirection: 'row-reverse', justifyContent: 'space-between' }}
      />
    </Box>
  );
};

export default NumberProperties;
