import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  IconButton,
  Tooltip,
  Divider,
  Paper,
  useMediaQuery,
  Snackbar,
  Alert,
} from '@mui/material';
import {
  ArrowBack,
  Save,
  Preview,
  Publish,
  Settings,
  Add,
  DragIndicator,
  Delete,
  Edit,
  Visibility,
  VisibilityOff,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../../../context/AuthContext';

// Import components
import SurveyBuilderSidebar from './SurveyBuilderSidebar';
import SurveyBuilderCanvas from './SurveyBuilderCanvas';
import SurveyBuilderProperties from './SurveyBuilderProperties';
import SurveyBuilderHeader from './SurveyBuilderHeader';

const SurveyBuilder = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const isMobile = useMediaQuery('(max-width: 768px)');

  // State management
  const [survey, setSurvey] = useState({
    id: '',
    title: 'Untitled Survey',
    description: '',
    questions: [],
    settings: {
      allowAnonymous: true,
      showProgress: true,
      randomizeQuestions: false,
      requireAuthentication: false,
    },
  });

  const [selectedQuestion, setSelectedQuestion] = useState(null);
  const [previewMode, setPreviewMode] = useState(false);
  const [isDirty, setIsDirty] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [notification, setNotification] = useState({
    open: false,
    message: '',
    severity: 'success',
  });

  // Auto-save functionality
  useEffect(() => {
    if (isDirty && survey.id) {
      const timer = setTimeout(() => {
        handleAutoSave();
      }, 2000); // Auto-save after 2 seconds of inactivity

      return () => clearTimeout(timer);
    }
  }, [isDirty, survey]);

  const handleAutoSave = async () => {
    try {
      setIsSaving(true);
      // API call to save survey
      await saveSurvey();
      setIsDirty(false);
      showNotification('Survey auto-saved', 'success');
    } catch (error) {
      showNotification('Failed to auto-save', 'error');
    } finally {
      setIsSaving(false);
    }
  };

  const saveSurvey = async () => {
    // API call to save survey
    const response = await fetch('/api/surveys/builder', {
      method: survey.id ? 'PUT' : 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        ...survey,
        tenantId: user?.tenantId,
        updatedAt: new Date().toISOString(),
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to save survey');
    }

    const savedSurvey = await response.json();
    setSurvey(savedSurvey);
    return savedSurvey;
  };

  const handleSave = async () => {
    try {
      setIsSaving(true);
      await saveSurvey();
      setIsDirty(false);
      showNotification('Survey saved successfully', 'success');
    } catch (error) {
      showNotification('Failed to save survey', 'error');
    } finally {
      setIsSaving(false);
    }
  };

  const handlePublish = async () => {
    try {
      setIsSaving(true);
      const publishedSurvey = await saveSurvey();
      
      // API call to publish survey
      const response = await fetch(`/api/surveys/builder/${publishedSurvey.id}/publish`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to publish survey');
      }

      showNotification('Survey published successfully', 'success');
      navigate(`/surveys/preview/${publishedSurvey.id}`);
    } catch (error) {
      showNotification('Failed to publish survey', 'error');
    } finally {
      setIsSaving(false);
    }
  };

  const handlePreview = () => {
    setPreviewMode(!previewMode);
  };

  const showNotification = (message, severity) => {
    setNotification({
      open: true,
      message,
      severity,
    });
  };

  const closeNotification = () => {
    setNotification(prev => ({ ...prev, open: false }));
  };

  const updateSurvey = (updates) => {
    setSurvey(prev => ({ ...prev, ...updates }));
    setIsDirty(true);
  };

  const updateQuestion = (questionId, updates) => {
    setSurvey(prev => ({
      ...prev,
      questions: prev.questions.map(q =>
        q.id === questionId ? { ...q, ...updates } : q
      ),
    }));
    setIsDirty(true);
  };

  const addQuestion = (questionType) => {
    const newQuestion = {
      id: `q-${Date.now()}`,
      type: questionType,
      title: 'New Question',
      required: false,
      order: survey.questions.length + 1,
      // Add type-specific properties
      ...(questionType === 'multiple_choice' && {
        options: [
          { id: 'opt-1', text: 'Option 1' },
          { id: 'opt-2', text: 'Option 2' },
        ],
        allowMultiple: false,
      }),
      ...(questionType === 'rating' && {
        scale: 5,
        labels: {
          1: 'Poor',
          5: 'Excellent',
        },
      }),
      ...(questionType === 'text' && {
        placeholder: 'Enter your answer',
        maxLength: 500,
      }),
    };

    setSurvey(prev => ({
      ...prev,
      questions: [...prev.questions, newQuestion],
    }));
    setSelectedQuestion(newQuestion);
    setIsDirty(true);
  };

  const deleteQuestion = (questionId) => {
    setSurvey(prev => ({
      ...prev,
      questions: prev.questions.filter(q => q.id !== questionId),
    }));
    if (selectedQuestion?.id === questionId) {
      setSelectedQuestion(null);
    }
    setIsDirty(true);
  };

  const reorderQuestions = (fromIndex, toIndex) => {
    const newQuestions = [...survey.questions];
    const [movedQuestion] = newQuestions.splice(fromIndex, 1);
    newQuestions.splice(toIndex, 0, movedQuestion);
    
    // Update order numbers
    newQuestions.forEach((q, index) => {
      q.order = index + 1;
    });

    setSurvey(prev => ({
      ...prev,
      questions: newQuestions,
    }));
    setIsDirty(true);
  };

  if (isMobile) {
    return (
      <Box sx={{ p: 2 }}>
        <Typography variant="h6" sx={{ mb: 2 }}>
          Survey Builder
        </Typography>
        <Typography color="error">
          Survey Builder is not available on mobile devices. Please use a desktop or tablet.
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column', bgcolor: '#F8FAFC' }}>
      {/* Header */}
      <SurveyBuilderHeader
        survey={survey}
        updateSurvey={updateSurvey}
        onSave={handleSave}
        onPublish={handlePublish}
        onPreview={handlePreview}
        previewMode={previewMode}
        isSaving={isSaving}
        isDirty={isDirty}
        onBack={() => navigate('/surveys')}
      />

      {/* Main Content */}
      <Box sx={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        {/* Left Sidebar - Question Types */}
        {!previewMode && (
          <SurveyBuilderSidebar
            onAddQuestion={addQuestion}
            disabled={previewMode}
          />
        )}

        {/* Center Canvas - Survey Building Area */}
        <SurveyBuilderCanvas
          survey={survey}
          selectedQuestion={selectedQuestion}
          onSelectQuestion={setSelectedQuestion}
          onUpdateQuestion={updateQuestion}
          onDeleteQuestion={deleteQuestion}
          onReorderQuestions={reorderQuestions}
          previewMode={previewMode}
        />

        {/* Right Panel - Properties or Preview */}
        <SurveyBuilderProperties
          survey={survey}
          selectedQuestion={selectedQuestion}
          onUpdateSurvey={updateSurvey}
          onUpdateQuestion={updateQuestion}
          previewMode={previewMode}
          showSettings={showSettings}
          onToggleSettings={() => setShowSettings(!showSettings)}
        />
      </Box>

      {/* Notification Snackbar */}
      <Snackbar
        open={notification.open}
        autoHideDuration={3000}
        onClose={closeNotification}
        anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
      >
        <Alert onClose={closeNotification} severity={notification.severity}>
          {notification.message}
        </Alert>
      </Snackbar>

      {/* Auto-save indicator */}
      {isSaving && (
        <Box
          sx={{
            position: 'fixed',
            bottom: 20,
            right: 20,
            bgcolor: 'background.paper',
            px: 2,
            py: 1,
            borderRadius: 1,
            boxShadow: 2,
            display: 'flex',
            alignItems: 'center',
            gap: 1,
          }}
        >
          <Typography variant="body2" color="text.secondary">
            {isDirty ? 'Saving...' : 'Saved'}
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default SurveyBuilder;
