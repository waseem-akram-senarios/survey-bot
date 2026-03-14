import React from 'react';
import {
  Box,
  Typography,
  TextField,
  Switch,
  FormControlLabel,
  Slider,
} from '@mui/material';

const TextProperties = ({ question, onUpdateQuestion }) => {
  return (
    <Box>
      <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600 }}>
        Text Input Settings
      </Typography>

      <TextField
        fullWidth
        label="Placeholder Text"
        value={question.placeholder || ''}
        onChange={(e) => onUpdateQuestion(question.id, { placeholder: e.target.value })}
        sx={{ mb: 2 }}
        size="small"
      />

      <FormControlLabel
        control={
          <Switch
            checked={question.multiline || false}
            onChange={(e) => onUpdateQuestion(question.id, { multiline: e.target.checked })}
          />
        }
        label="Multi-line text"
        sx={{ mb: 2, display: 'flex', flexDirection: 'row-reverse', justifyContent: 'space-between' }}
      />

      <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
        Maximum Length
      </Typography>
      
      <TextField
        fullWidth
        type="number"
        label="Character limit"
        value={question.maxLength || ''}
        onChange={(e) => onUpdateQuestion(question.id, { maxLength: e.target.value ? parseInt(e.target.value) : null })}
        sx={{ mb: 2 }}
        size="small"
        inputProps={{ min: 1, max: 10000 }}
      />

      <FormControlLabel
        control={
          <Switch
            checked={question.allowNumbers || false}
            onChange={(e) => onUpdateQuestion(question.id, { allowNumbers: e.target.checked })}
          />
        }
        label="Allow numbers only"
        sx={{ mb: 2, display: 'flex', flexDirection: 'row-reverse', justifyContent: 'space-between' }}
      />

      <FormControlLabel
        control={
          <Switch
            checked={question.allowEmail || false}
            onChange={(e) => onUpdateQuestion(question.id, { allowEmail: e.target.checked })}
          />
        }
        label="Email format validation"
        sx={{ mb: 2, display: 'flex', flexDirection: 'row-reverse', justifyContent: 'space-between' }}
      />

      <FormControlLabel
        control={
          <Switch
            checked={question.allowPhone || false}
            onChange={(e) => onUpdateQuestion(question.id, { allowPhone: e.target.checked })}
          />
        }
        label="Phone format validation"
        sx={{ display: 'flex', flexDirection: 'row-reverse', justifyContent: 'space-between' }}
      />
    </Box>
  );
};

export default TextProperties;
