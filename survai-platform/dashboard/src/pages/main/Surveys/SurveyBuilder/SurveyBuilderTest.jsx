import React from 'react';
import { Box, Typography, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';

const SurveyBuilderTest = () => {
  const navigate = useNavigate();

  return (
    <Box sx={{ p: 4, textAlign: 'center' }}>
      <Typography variant="h4" sx={{ mb: 2 }}>
        Survey Builder Test Page
      </Typography>
      <Typography variant="body1" sx={{ mb: 3 }}>
        If you can see this page, the routing is working correctly.
      </Typography>
      <Button variant="contained" onClick={() => navigate('/dashboard')}>
        Go to Dashboard
      </Button>
    </Box>
  );
};

export default SurveyBuilderTest;
