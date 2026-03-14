import React from 'react';
import {
  Box,
  Typography,
  Switch,
  FormControlLabel,
  TextField,
} from '@mui/material';

const DateProperties = ({ question, onUpdateQuestion }) => {
  return (
    <Box>
      <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600 }}>
        Date/Time Settings
      </Typography>

      <FormControlLabel
        control={
          <Switch
            checked={question.includeTime || false}
            onChange={(e) => onUpdateQuestion(question.id, { includeTime: e.target.checked })}
          />
        }
        label="Include time"
        sx={{ mb: 2, display: 'flex', flexDirection: 'row-reverse', justifyContent: 'space-between' }}
      />

      <TextField
        fullWidth
        type="date"
        label="Minimum date"
        value={question.minDate || ''}
        onChange={(e) => onUpdateQuestion(question.id, { minDate: e.target.value })}
        sx={{ mb: 2 }}
        size="small"
        InputLabelProps={{ shrink: true }}
      />

      <TextField
        fullWidth
        type="date"
        label="Maximum date"
        value={question.maxDate || ''}
        onChange={(e) => onUpdateQuestion(question.id, { maxDate: e.target.value })}
        sx={{ mb: 2 }}
        size="small"
        InputLabelProps={{ shrink: true }}
      />

      <FormControlLabel
        control={
          <Switch
            checked={question.disablePast || false}
            onChange={(e) => onUpdateQuestion(question.id, { disablePast: e.target.checked })}
          />
        }
        label="Disable past dates"
        sx={{ mb: 2, display: 'flex', flexDirection: 'row-reverse', justifyContent: 'space-between' }}
      />

      <FormControlLabel
        control={
          <Switch
            checked={question.disableFuture || false}
            onChange={(e) => onUpdateQuestion(question.id, { disableFuture: e.target.checked })}
          />
        }
        label="Disable future dates"
        sx={{ display: 'flex', flexDirection: 'row-reverse', justifyContent: 'space-between' }}
      />
    </Box>
  );
};

export default DateProperties;
