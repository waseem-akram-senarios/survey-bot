import React from 'react';
import {
  Box,
  Typography,
  TextField,
  Switch,
  FormControlLabel,
} from '@mui/material';

const MatrixProperties = ({ question, onUpdateQuestion }) => {
  return (
    <Box>
      <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600 }}>
        Matrix/Grid Settings
      </Typography>

      <TextField
        fullWidth
        label="Row labels (one per line)"
        multiline
        rows={3}
        value={(question.rows || []).map(r => r.text).join('\n')}
        onChange={(e) => {
          const rows = e.target.value.split('\n').map((text, index) => ({
            id: `row-${index}`,
            text: text.trim()
          })).filter(r => r.text);
          onUpdateQuestion(question.id, { rows });
        }}
        sx={{ mb: 2 }}
        size="small"
      />

      <TextField
        fullWidth
        label="Column labels (one per line)"
        multiline
        rows={3}
        value={(question.columns || []).map(c => c.text).join('\n')}
        onChange={(e) => {
          const columns = e.target.value.split('\n').map((text, index) => ({
            id: `col-${index}`,
            text: text.trim()
          })).filter(c => c.text);
          onUpdateQuestion(question.id, { columns });
        }}
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
        label="Allow multiple selections per row"
        sx={{ display: 'flex', flexDirection: 'row-reverse', justifyContent: 'space-between' }}
      />
    </Box>
  );
};

export default MatrixProperties;
