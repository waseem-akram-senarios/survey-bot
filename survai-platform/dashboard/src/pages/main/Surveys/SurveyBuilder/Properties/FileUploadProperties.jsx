import React from 'react';
import {
  Box,
  Typography,
  TextField,
  Switch,
  FormControlLabel,
} from '@mui/material';

const FileUploadProperties = ({ question, onUpdateQuestion }) => {
  return (
    <Box>
      <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600 }}>
        File Upload Settings
      </Typography>

      <TextField
        fullWidth
        label="Maximum file size (MB)"
        type="number"
        value={question.maxSize || 5}
        onChange={(e) => onUpdateQuestion(question.id, { maxSize: parseInt(e.target.value) || 5 })}
        sx={{ mb: 2 }}
        size="small"
        inputProps={{ min: 1, max: 100 }}
      />

      <TextField
        fullWidth
        label="Accepted file types"
        value={(question.fileTypes || []).join(', ')}
        onChange={(e) => {
          const types = e.target.value.split(',').map(t => t.trim()).filter(t => t);
          onUpdateQuestion(question.id, { fileTypes: types });
        }}
        sx={{ mb: 2 }}
        size="small"
        placeholder="e.g., pdf, doc, jpg, png"
      />

      <TextField
        fullWidth
        label="Help text"
        value={question.helpText || ''}
        onChange={(e) => onUpdateQuestion(question.id, { helpText: e.target.value })}
        sx={{ mb: 2 }}
        size="small"
        multiline
        rows={2}
        placeholder="Instructions for file upload"
      />

      <FormControlLabel
        control={
          <Switch
            checked={question.multipleFiles || false}
            onChange={(e) => onUpdateQuestion(question.id, { multipleFiles: e.target.checked })}
          />
        }
        label="Allow multiple files"
        sx={{ display: 'flex', flexDirection: 'row-reverse', justifyContent: 'space-between' }}
      />
    </Box>
  );
};

export default FileUploadProperties;
