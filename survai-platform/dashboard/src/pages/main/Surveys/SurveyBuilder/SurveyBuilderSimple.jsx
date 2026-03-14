import React from 'react';
import {
  Box,
  Typography,
  Button,
  IconButton,
  Paper,
} from '@mui/material';
import {
  ArrowBack,
  Add,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const SurveyBuilderSimple = () => {
  const navigate = useNavigate();

  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column', bgcolor: '#F8FAFC' }}>
      {/* Header */}
      <Box
        sx={{
          bgcolor: 'white',
          borderBottom: '1px solid',
          borderColor: 'divider',
          px: 3,
          py: 2,
          display: 'flex',
          alignItems: 'center',
          gap: 2,
        }}
      >
        <IconButton onClick={() => navigate('/surveys')} sx={{ color: 'text.secondary' }}>
          <ArrowBack />
        </IconButton>
        
        <Typography variant="h5" sx={{ fontWeight: 600, flex: 1 }}>
          Survey Builder
        </Typography>
        
        <Button variant="contained" sx={{ borderRadius: 2 }}>
          Save
        </Button>
      </Box>

      {/* Main Content */}
      <Box sx={{ flex: 1, display: 'flex', p: 3, gap: 3 }}>
        {/* Left Sidebar - Question Types */}
        <Box
          sx={{
            width: 280,
            bgcolor: 'white',
            borderRight: '1px solid',
            borderColor: 'divider',
            borderRadius: 2,
            p: 2,
          }}
        >
          <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
            Question Types
          </Typography>
          
          <Paper sx={{ p: 2, mb: 2, cursor: 'pointer', '&:hover': { bgcolor: 'action.hover' } }}>
            <Typography>Multiple Choice</Typography>
          </Paper>
          
          <Paper sx={{ p: 2, mb: 2, cursor: 'pointer', '&:hover': { bgcolor: 'action.hover' } }}>
            <Typography>Text Input</Typography>
          </Paper>
          
          <Paper sx={{ p: 2, cursor: 'pointer', '&:hover': { bgcolor: 'action.hover' } }}>
            <Typography>Rating Scale</Typography>
          </Paper>
        </Box>

        {/* Center Canvas - Survey Building Area */}
        <Box sx={{ flex: 1, bgcolor: 'white', borderRadius: 2, p: 3 }}>
          <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>
            Survey Questions
          </Typography>
          
          <Box sx={{ textAlign: 'center', py: 8 }}>
            <Typography variant="h6" color="text.secondary" sx={{ mb: 2 }}>
              Start Building Your Survey
            </Typography>
            
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Add questions from the sidebar to get started
            </Typography>
            
            <Button variant="outlined" startIcon={<Add />}>
              Add Your First Question
            </Button>
          </Box>
        </Box>

        {/* Right Panel - Properties */}
        <Box
          sx={{
            width: 320,
            bgcolor: 'white',
            borderLeft: '1px solid',
            borderColor: 'divider',
            borderRadius: 2,
            p: 3,
          }}
        >
          <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
            Properties
          </Typography>
          
          <Typography variant="body2" color="text.secondary">
            Select a question to edit its properties
          </Typography>
        </Box>
      </Box>
    </Box>
  );
};

export default SurveyBuilderSimple;
