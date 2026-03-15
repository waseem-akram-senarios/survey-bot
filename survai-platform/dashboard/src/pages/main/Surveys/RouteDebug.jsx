import React from 'react';
import { Box, Typography, Button } from '@mui/material';
import { useLocation, useNavigate } from 'react-router-dom';

const RouteDebug = () => {
  const location = useLocation();
  const navigate = useNavigate();

  return (
    <Box sx={{ p: 3, minHeight: '100vh', bgcolor: '#f5f5f5' }}>
      <Typography variant="h4" sx={{ mb: 2, color: '#ff5722' }}>
        🐛 Route Debug Information
      </Typography>
      
      <Box sx={{ mb: 3, p: 2, bgcolor: 'white', borderRadius: 1 }}>
        <Typography variant="h6" sx={{ mb: 1 }}>
          Current Location:
        </Typography>
        <Typography variant="body2" sx={{ fontFamily: 'monospace', bgcolor: '#f5f5f5', p: 1 }}>
          {location.pathname}
        </Typography>
      </Box>
      
      <Box sx={{ mb: 3, p: 2, bgcolor: 'white', borderRadius: 1 }}>
        <Typography variant="h6" sx={{ mb: 1 }}>
          Full Location Object:
        </Typography>
        <Typography variant="body2" sx={{ fontFamily: 'monospace', bgcolor: '#f5f5f5', p: 1, fontSize: '0.8rem' }}>
          {JSON.stringify(location, null, 2)}
        </Typography>
      </Box>
      
      <Box sx={{ mb: 3 }}>
        <Button variant="contained" onClick={() => navigate('/dashboard')} sx={{ mr: 2 }}>
          Go to Dashboard
        </Button>
        <Button variant="outlined" onClick={() => navigate('/surveys/launch')} sx={{ mr: 2 }}>
          Go to Create Survey
        </Button>
        <Button variant="outlined" onClick={() => navigate('/surveys/builder')}>
          Go to Survey Builder
        </Button>
      </Box>
    </Box>
  );
};

export default RouteDebug;
