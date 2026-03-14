import React from 'react';
import {
  Box,
  Typography,
  Switch,
  FormControlLabel,
} from '@mui/material';

const CheckboxProperties = ({ question, onUpdateQuestion }) => {
  return (
    <Box>
      <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600 }}>
        Checkbox Settings
      </Typography>

      <FormControlLabel
        control={
          <Switch
            checked={question.requireAll || false}
            onChange={(e) => onUpdateQuestion(question.id, { requireAll: e.target.checked })}
          />
        }
        label="Require all options to be checked"
        sx={{ mb: 2, display: 'flex', flexDirection: 'row-reverse', justifyContent: 'space-between' }}
      />

      <FormControlLabel
        control={
          <Switch
            checked={question.inline || false}
            onChange={(e) => onUpdateQuestion(question.id, { inline: e.target.checked })}
          />
        }
        label="Display inline"
        sx={{ display: 'flex', flexDirection: 'row-reverse', justifyContent: 'space-between' }}
      />
    </Box>
  );
};

export default CheckboxProperties;
