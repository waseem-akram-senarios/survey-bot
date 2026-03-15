import React from 'react';
import { Box, Typography, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';

const SurveyBuilderDebug = () => {
  const navigate = useNavigate();

  return (
    <Box sx={{ p: 3, minHeight: '100vh', bgcolor: '#f5f5f5' }}>
      <Typography variant="h4" sx={{ mb: 2, color: '#7B61FF' }}>
        🚀 Survey Builder Debug Page
      </Typography>
      <Typography variant="body1" sx={{ mb: 2 }}>
        This is a debug page to verify the Survey Builder routing is working correctly.
      </Typography>
      <Typography variant="body2" sx={{ mb: 3, color: '#666' }}>
        If you can see this page, the routing is working. The issue might be with the SurveyBuilderAdvanced component.
      </Typography>
      <Button 
        variant="contained" 
        onClick={() => navigate('/dashboard')}
        sx={{ mr: 2 }}
      >
        Go to Dashboard
      </Button>
      <Button 
        variant="outlined"
        onClick={() => window.location.reload()}
      >
        Reload Page
      </Button>
    </Box>
  );
};

export default SurveyBuilderDebug;
