import React from 'react';
import { Box, Typography, Button, Paper, Stack } from '@mui/material';
import { useNavigate } from 'react-router-dom';

const SurveyBuilderWorking = () => {
  const navigate = useNavigate();

  return (
    <Box sx={{ p: 3, minHeight: '100vh', bgcolor: '#F5F6FA' }}>
      {/* Header */}
      <Paper sx={{ p: 2, mb: 3, bgcolor: 'white', borderRadius: 2 }}>
        <Stack direction="row" alignItems="center" justifyContent="space-between">
          <Box>
            <Typography variant="h5" sx={{ fontWeight: 700, color: '#1F2937' }}>
              Survey Builder
            </Typography>
            <Typography variant="body2" color="text.secondary">
              ITCurves — Rider Voice
            </Typography>
          </Box>
          <Stack direction="row" spacing={2}>
            <Button variant="outlined" onClick={() => navigate('/dashboard')}>
              Back to Dashboard
            </Button>
            <Button variant="contained" sx={{ bgcolor: '#7B61FF' }}>
              Save Survey
            </Button>
          </Stack>
        </Stack>
      </Paper>

      {/* Main Content */}
      <Stack direction="row" spacing={3}>
        {/* Left Sidebar */}
        <Paper sx={{ width: 280, p: 2, bgcolor: 'white', borderRadius: 2 }}>
          <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
            Question Types
          </Typography>
          <Stack spacing={1}>
            {['Multiple Choice', 'Text Input', 'Rating Scale', 'Yes/No'].map((type) => (
              <Paper key={type} sx={{ p: 1.5, cursor: 'pointer', '&:hover': { bgcolor: '#F3F4F6' } }}>
                <Typography variant="body2">{type}</Typography>
              </Paper>
            ))}
          </Stack>
        </Paper>

        {/* Center Canvas */}
        <Box sx={{ flex: 1 }}>
          <Paper sx={{ p: 3, bgcolor: 'white', borderRadius: 2, minHeight: 400 }}>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
              Create Survey
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Start building your survey by adding questions from the sidebar.
            </Typography>
            
            <Box sx={{ mt: 4, p: 4, border: '2px dashed #CBD5F5', borderRadius: 2, textAlign: 'center' }}>
              <Typography variant="h6" color="text.secondary" sx={{ mb: 2 }}>
                No questions yet
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Add your first question to get started
              </Typography>
            </Box>
          </Paper>
        </Box>

        {/* Right Panel */}
        <Paper sx={{ width: 300, p: 2, bgcolor: 'white', borderRadius: 2 }}>
          <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
            Properties
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Select a question to edit its properties
          </Typography>
        </Paper>
      </Stack>
    </Box>
  );
};

export default SurveyBuilderWorking;
