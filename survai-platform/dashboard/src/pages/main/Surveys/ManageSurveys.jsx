import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  useMediaQuery,
  CircularProgress,
  Snackbar,
  Alert,
} from '@mui/material';
import { UploadFile } from '@mui/icons-material';
import Cards from '../../../components/Cards';
import DashboardTable from '../../../components/SurveyTable/SurveyTable';
import { useManageSurveys } from '../../../hooks/Surveys/useSurveyTable';
import SurveyService from '../../../services/Surveys/surveyService';

const ManageSurveys = () => {
  const navigate = useNavigate();
  const isMobile = useMediaQuery('(max-width: 600px)');
  const [cloneMsg, setCloneMsg] = useState("");
  const [showCloneMsg, setShowCloneMsg] = useState(false);
  const {
    statsData,
    tableData,
    statsLoading,
    tableLoading,
    statsError,
    tableError,
    globalLoading,
  } = useManageSurveys();

  const handleSurveyClick = (surveyData) => {
    navigate(`/surveys/status/${surveyData.SurveyId}`, {
      state: { surveyData }
    });
  };

  const handleEditSurvey = (surveyData) => {
    navigate(`/surveys/edit/${surveyData.SurveyId}`, {
      state: { surveyData }
    });
  };

  const handleCloneSurvey = async (surveyData) => {
    try {
      const result = await SurveyService.cloneSurvey(surveyData);
      setCloneMsg(`Survey "${surveyData.Name || surveyData.Recipient}" cloned successfully`);
      setShowCloneMsg(true);
      window.location.reload();
    } catch (error) {
      setCloneMsg(`Failed to clone: ${error.message}`);
      setShowCloneMsg(true);
    }
  };

  if (globalLoading) {
    return (
      <Box sx={{
        backgroundColor: '#F9FBFC',
        flexGrow: 1,
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        ...(isMobile && {
          minHeight: 'calc(100vh - 64px)',
        })
      }}>
        <CircularProgress size={60} sx={{ color: '#1958F7' }} />
      </Box>
    );
  }

  return (
    <Box sx={{
      backgroundColor: '#F9FBFC', 
      flexGrow: 1, 
      display: 'flex', 
      flexDirection: 'column', 
      p: isMobile ? 2 : 4,
      ...(isMobile && {
        minHeight: 'calc(100vh - 64px)',
        overflow: 'auto'
      })
    }}>
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
        <Button
          variant="outlined"
          startIcon={<UploadFile />}
          onClick={() => navigate('/surveys/import')}
          sx={{
            textTransform: 'none',
            borderRadius: '12px',
            borderColor: '#1958F7',
            color: '#1958F7',
            fontFamily: 'Poppins, sans-serif',
            fontSize: '14px',
            fontWeight: 400,
            px: 2,
            '&:hover': { backgroundColor: '#EEF3FF', borderColor: '#1958F7' },
          }}
        >
          Import Rider Data
        </Button>
      </Box>

      <Cards 
        headerTitle='Manage Surveys'
        statsData={statsData} 
        loading={statsLoading} 
        error={statsError} 
      />
      <DashboardTable 
        tableData={tableData} 
        loading={tableLoading} 
        error={tableError}
        onRowClick={handleSurveyClick}
        onEditSurvey={handleEditSurvey}
        onCloneSurvey={handleCloneSurvey}
      />

      <Snackbar
        open={showCloneMsg}
        autoHideDuration={4000}
        onClose={() => setShowCloneMsg(false)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={() => setShowCloneMsg(false)} severity="success" variant="filled"
          sx={{ background: "#EFEFFD", color: "#1958F7" }}>
          {cloneMsg}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default ManageSurveys;