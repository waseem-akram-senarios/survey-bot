import React from 'react';
import {
  Box,
  Typography,
  Container,
  Card,
  CardContent,
  Button
} from '@mui/material';
import { useNavigate } from 'react-router-dom';

const DashboardSimple = () => {
  const navigate = useNavigate();

  return (
    <Box sx={{ 
      minHeight: '100vh',
      bgcolor: '#f8fafc',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
    }}>
      <Container maxWidth="md">
        <Card sx={{ 
          p: 4, 
          textAlign: 'center',
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
        }}>
          <CardContent>
            <Typography variant="h4" sx={{ mb: 2, color: '#1f2937', fontWeight: 600 }}>
              🎉 Survey Bot Dashboard
            </Typography>
            <Typography variant="body1" sx={{ mb: 3, color: '#6b7280' }}>
              Your dashboard is working! This is a simple test page.
            </Typography>
            <Typography variant="body2" sx={{ mb: 4, color: '#9ca3af' }}>
              If you can see this page, the routing is working correctly.
            </Typography>
            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
              <Button 
                variant="contained" 
                onClick={() => navigate('/surveys')}
                sx={{ mr: 2 }}
              >
                View Surveys
              </Button>
              <Button 
                variant="outlined"
                onClick={() => navigate('/templates')}
              >
                View Templates
              </Button>
            </Box>
          </CardContent>
        </Card>
      </Container>
    </Box>
  );
};

export default DashboardSimple;
