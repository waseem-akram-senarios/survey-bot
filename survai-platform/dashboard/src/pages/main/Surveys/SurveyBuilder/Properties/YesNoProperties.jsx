import React from 'react';
import {
  Box,
  Typography,
  Switch,
  FormControlLabel,
  TextField,
} from '@mui/material';

const YesNoProperties = ({ question, onUpdateQuestion }) => {
  return (
    <Box>
      <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600 }}>
        Yes/No Settings
      </Typography>

      <TextField
        fullWidth
        label="Yes Label"
        value={question.yesLabel || 'Yes'}
        onChange={(e) => onUpdateQuestion(question.id, { yesLabel: e.target.value })}
        sx={{ mb: 2 }}
        size="small"
      />

      <TextField
        fullWidth
        label="No Label"
        value={question.noLabel || 'No'}
        onChange={(e) => onUpdateQuestion(question.id, { noLabel: e.target.value })}
        sx={{ mb: 2 }}
        size="small"
      />

      <FormControlLabel
        control={
          <Switch
            checked={question.showNA || false}
            onChange={(e) => onUpdateQuestion(question.id, { showNA: e.target.checked })}
          />
        }
        label="Show 'N/A' option"
        sx={{ display: 'flex', flexDirection: 'row-reverse', justifyContent: 'space-between' }}
      />
    </Box>
  );
};

export default YesNoProperties;
