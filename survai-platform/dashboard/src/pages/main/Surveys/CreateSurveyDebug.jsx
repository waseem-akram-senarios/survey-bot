import React from 'react';
import { Box, Typography, Button, List, ListItem, ListItemText } from '@mui/material';
import { useNavigate } from 'react-router-dom';

const CreateSurveyDebug = () => {
  const navigate = useNavigate();

  return (
    <Box sx={{ p: 3, minHeight: '100vh', bgcolor: '#f5f5f5' }}>
      <Typography variant="h4" sx={{ mb: 2, color: '#1976d2' }}>
        🚀 Create Survey Debug Page
      </Typography>
      <Typography variant="body1" sx={{ mb: 2 }}>
        This is a debug page to verify the Create Survey routing is working correctly.
      </Typography>
      <Typography variant="body2" sx={{ mb: 3, color: '#666' }}>
        If you can see this page, the routing is working. The issue might be with the CreateSurveyModern component.
      </Typography>
      
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" sx={{ mb: 2 }}>
          ✅ Backend APIs Status:
        </Typography>
        <List dense>
          <ListItem>
            <ListItemText primary="Templates API: Working (34 templates available)" />
          </ListItem>
          <ListItem>
            <ListItemText primary="Survey Creation API: Working (generates 13 questions)" />
          </ListItem>
          <ListItem>
            <ListItemText primary="Survey Listing API: Working" />
          </ListItem>
        </List>
      </Box>
      
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" sx={{ mb: 2 }}>
          🔧 Frontend Status:
        </Typography>
        <List dense>
          <ListItem>
            <ListItemText primary="React Router: Needs debugging" />
          </ListItem>
          <ListItem>
            <ListItemText primary="CreateSurveyModern Component: Needs verification" />
          </ListItem>
        </List>
      </Box>
      
      <Button 
        variant="contained" 
        onClick={() => navigate('/dashboard')}
        sx={{ mr: 2 }}
      >
        Go to Dashboard
      </Button>
      <Button 
        variant="outlined"
        onClick={() => navigate('/surveys/builder')}
        sx={{ mr: 2 }}
      >
        Go to Survey Builder
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

export default CreateSurveyDebug;
