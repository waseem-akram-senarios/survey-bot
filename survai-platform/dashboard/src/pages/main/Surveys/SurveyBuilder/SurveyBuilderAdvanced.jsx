import React, { useState, useRef, useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  IconButton,
  TextField,
  Divider,
  Stack,
  Chip,
  Avatar,
  Menu,
  MenuItem,
  Switch,
  FormControlLabel,
  Slider,
  Select,
  FormControl,
  InputLabel,
  Snackbar,
  Alert as MuiAlert,
} from '@mui/material';
import {
  Add,
  DragIndicator,
  MoreVert,
  RadioButtonChecked,
  TextFields,
  Star,
  CheckCircle,
  InsertChartOutlined,
  ContentCopy,
  CalendarMonth,
  Phone as PhoneIcon,
  Public,
  QrCode2,
  Visibility,
  Save,
  ArrowBack,
  Delete,
  Edit,
  CopyAll,
  Settings,
  Launch,
  Share,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../../../context/AuthContext';
import ApiBaseHelper from '../../../../network/apiBaseHelper';
import ApiLinks, { RECIPIENT_BASE } from '../../../../network/apiLinks';
import { useTemplateAPI } from '../../../../hooks/Templates/useTemplates';
import { useSurvey } from '../../../../hooks/Surveys/useSurvey';

const QUESTION_TYPES = [
  { 
    label: 'Multiple Choice', 
    description: 'Choose one option', 
    icon: RadioButtonChecked, 
    color: '#7B61FF',
    type: 'multiple_choice',
    defaultOptions: ['Option 1', 'Option 2', 'Option 3']
  },
  { 
    label: 'Open Ended', 
    description: 'Free text response', 
    icon: TextFields, 
    color: '#FF7AB2',
    type: 'open_ended'
  },
  { 
    label: 'Yes / No', 
    description: 'Binary choice', 
    icon: CheckCircle, 
    color: '#00C4B8',
    type: 'yes_no'
  },
  { 
    label: 'Rating Scale', 
    description: '1-5 star rating', 
    icon: Star, 
    color: '#FFCF4A',
    type: 'rating_scale',
    defaultOptions: ['1', '2', '3', '4', '5']
  },
  { 
    label: 'NPS Score', 
    description: '0-10 promoter score', 
    icon: InsertChartOutlined, 
    color: '#F97316',
    type: 'nps',
    defaultOptions: ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
  },
  { 
    label: 'Route / Stop', 
    description: 'Transit information', 
    icon: ContentCopy, 
    color: '#38BDF8',
    type: 'route_stop'
  },
  { 
    label: 'Date / Time', 
    description: 'Schedule preference', 
    icon: CalendarMonth, 
    color: '#6366F1',
    type: 'date_time'
  },
];

const SurveyBuilderAdvanced = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { createTemplate, saveMultipleQuestions, updateTemplateStatus } = useTemplateAPI();
  const { generateSurvey, launchSurvey } = useSurvey();
  
  // Survey state
  const [surveyTitle, setSurveyTitle] = useState('Untitled Survey');
  const [surveyDescription, setSurveyDescription] = useState('');
  const [questions, setQuestions] = useState([]);
  const [selectedQuestion, setSelectedQuestion] = useState(null);
  const [draggedQuestion, setDraggedQuestion] = useState(null);
  const [draggedType, setDraggedType] = useState(null);
  
  // UI state
  const [saving, setSaving] = useState(false);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });
  const [showPreview, setShowPreview] = useState(false);
  const [distributionMenu, setDistributionMenu] = useState(null);
  
  const dragCounter = useRef(0);
  const canvasRef = useRef(null);

  const showNotification = (message, severity = 'success') =>
    setNotification({ open: true, message, severity });

  // Question management
  const addQuestion = (type, index = null) => {
    const questionType = QUESTION_TYPES.find(q => q.type === type);
    const newQuestion = {
      id: Date.now(),
      type: type,
      label: questionType?.label || type,
      text: '',
      required: false,
      options: questionType?.defaultOptions || [],
      order: index !== null ? index : questions.length,
    };
    
    if (index !== null) {
      setQuestions(prev => [
        ...prev.slice(0, index),
        newQuestion,
        ...prev.slice(index).map(q => ({ ...q, order: q.order + 1 }))
      ]);
    } else {
      setQuestions(prev => [...prev, newQuestion]);
    }
    
    setSelectedQuestion(newQuestion);
    showNotification(`${questionType?.label} question added`);
  };

  const updateQuestion = (id, updates) => {
    setQuestions(prev => prev.map(q => q.id === id ? { ...q, ...updates } : q));
    if (selectedQuestion?.id === id) {
      setSelectedQuestion(prev => ({ ...prev, ...updates }));
    }
  };

  const deleteQuestion = (id) => {
    setQuestions(prev => prev.filter(q => q.id !== id));
    if (selectedQuestion?.id === id) {
      setSelectedQuestion(null);
    }
    showNotification('Question deleted', 'info');
  };

  const duplicateQuestion = (id) => {
    const question = questions.find(q => q.id === id);
    if (question) {
      const newQuestion = {
        ...question,
        id: Date.now(),
        text: question.text + ' (Copy)',
        order: question.order + 1,
      };
      setQuestions(prev => [...prev, newQuestion]);
      showNotification('Question duplicated', 'success');
    }
  };

  // Drag and drop handlers
  const handleDragStart = (e, questionType = null, question = null) => {
    if (questionType) {
      setDraggedType(questionType);
      e.dataTransfer.effectAllowed = 'copy';
    } else if (question) {
      setDraggedQuestion(question);
      e.dataTransfer.effectAllowed = 'move';
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = draggedQuestion ? 'move' : 'copy';
  };

  const handleDragEnter = (e) => {
    e.preventDefault();
    dragCounter.current++;
    if (canvasRef.current) {
      canvasRef.current.style.backgroundColor = '#f0f4ff';
      canvasRef.current.style.borderColor = '#7B61FF';
    }
  };

  const handleDragLeave = (e) => {
    dragCounter.current--;
    if (dragCounter.current === 0 && canvasRef.current) {
      canvasRef.current.style.backgroundColor = '';
      canvasRef.current.style.borderColor = '';
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    dragCounter.current = 0;
    
    if (canvasRef.current) {
      canvasRef.current.style.backgroundColor = '';
      canvasRef.current.style.borderColor = '';
    }

    if (draggedType) {
      addQuestion(draggedType);
      setDraggedType(null);
    } else if (draggedQuestion) {
      // Reordering logic would go here
      setDraggedQuestion(null);
    }
  };

  // Save survey
  const handleSaveSurvey = async () => {
    if (!surveyTitle.trim()) {
      showNotification('Please enter a survey title', 'warning');
      return;
    }
    
    setSaving(true);
    try {
      // 1. Create Template
      const templateRes = await createTemplate(surveyTitle);
      
      // 2. Save Questions to Template
      if (questions.length > 0) {
        const formattedQuestions = questions.map((q, i) => {
          let type = 'category';
          if (q.type === 'open_ended' || q.type === 'date_time' || q.type === 'route_stop') type = 'open';
          if (q.type === 'rating_scale' || q.type === 'nps') type = 'rating';
          
          let options = q.options || [];
          if (q.type === 'yes_no') options = ['Yes', 'No'];
          
          let maxRange = null;
          if (q.type === 'rating_scale') maxRange = 5;
          if (q.type === 'nps') maxRange = 10;
          
          return {
            id: q.id,
            queId: null,
            isSaved: false,
            question: q.text || `Question ${i + 1}`,
            type: type,
            options: options,
            maxRange: maxRange,
            autofill: 'No'
          };
        });
        
        await saveMultipleQuestions(surveyTitle, formattedQuestions);
      }

      // 3. Generate Survey from Template
      const surveyId = crypto.randomUUID();
      const surveyData = {
        surveyId: surveyId,
        template: surveyTitle,
        recipient: 'General',
        biodata: surveyDescription,
        tenantId: user?.tenantId || '',
        phone: '',
        riderName: '',
        rideId: '',
      };
      
      const generatedSurvey = await generateSurvey(surveyData);

      // 4. Update Status & Launch if not Draft
      // Since advanced builder hardcodes Status: 'Draft' initially in original code
      await updateTemplateStatus(surveyTitle, 'Draft');

      showNotification('Survey saved successfully!');
      
      setTimeout(() => {
        navigate('/dashboard');
      }, 1500);
    } catch (err) {
      console.error('Error saving survey:', err);
      showNotification(err.message || 'Failed to save survey. Please try again.', 'error');
    } finally {
      setSaving(false);
    }
  };

  // Left Sidebar - Question Types
  const QuestionTypesSidebar = () => (
    <Paper elevation={0} sx={{ 
      height: '100%', 
      borderRadius: 0, 
      borderRight: '1px solid #E5E7EB',
      bgcolor: '#FAFAFA',
      overflow: 'hidden'
    }}>
      <Box sx={{ p: 3, borderBottom: '1px solid #E5E7EB' }}>
        <Typography variant="h6" sx={{ fontWeight: 700, mb: 1 }}>Question Types</Typography>
        <Typography variant="caption" color="text.secondary">
          Drag to add questions
        </Typography>
      </Box>
      
      <Box sx={{ p: 2, maxHeight: 'calc(100vh - 200px)', overflowY: 'auto' }}>
        <Stack spacing={1.5}>
          {QUESTION_TYPES.map((type) => {
            const Icon = type.icon;
            return (
              <Paper
                key={type.type}
                draggable
                onDragStart={(e) => handleDragStart(e, type.type)}
                elevation={0}
                sx={{
                  p: 2,
                  border: '1px solid #E5E7EB',
                  borderRadius: 2,
                  cursor: 'grab',
                  transition: 'all 0.2s',
                  '&:hover': {
                    borderColor: type.color,
                    bgcolor: `${type.color}08`,
                    transform: 'translateX(4px)',
                  },
                  '&:active': {
                    cursor: 'grabbing',
                  }
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Box sx={{
                    width: 40,
                    height: 40,
                    borderRadius: 2,
                    bgcolor: `${type.color}15`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: type.color,
                  }}>
                    <Icon fontSize="small" />
                  </Box>
                  <Box sx={{ flex: 1, minWidth: 0 }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600, lineHeight: 1.2 }}>
                      {type.label}
                    </Typography>
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
                      {type.description}
                    </Typography>
                  </Box>
                </Box>
              </Paper>
            );
          })}
        </Stack>
      </Box>
    </Paper>
  );

  // Center Canvas
  const SurveyCanvas = () => (
    <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Survey Header */}
      <Paper elevation={0} sx={{ p: 3, borderBottom: '1px solid #E5E7EB' }}>
        <TextField
          fullWidth
          value={surveyTitle}
          onChange={(e) => setSurveyTitle(e.target.value)}
          placeholder="Survey Title"
          variant="standard"
          InputProps={{
            disableUnderline: true,
            sx: { 
              fontSize: '1.5rem',
              fontWeight: 700,
              '& input': { 
                fontSize: '1.5rem',
                fontWeight: 700,
                bgcolor: 'transparent',
              }
            }
          }}
        />
        <TextField
          fullWidth
          value={surveyDescription}
          onChange={(e) => setSurveyDescription(e.target.value)}
          placeholder="Survey description (optional)"
          variant="standard"
          InputProps={{
            disableUnderline: true,
            sx: { 
              fontSize: '0.875rem',
              '& input': { 
                fontSize: '0.875rem',
                color: '#6B7280'
              }
            }
          }}
        />
      </Paper>

      {/* Questions Drop Zone */}
      <Box 
        ref={canvasRef}
        sx={{ 
          flex: 1,
          p: 3,
          overflowY: 'auto',
          transition: 'all 0.2s',
        }}
        onDragOver={handleDragOver}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        {questions.length === 0 ? (
          <Paper
            elevation={0}
            sx={{
              border: '2px dashed #CBD5F5',
              borderRadius: 3,
              minHeight: 300,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              textAlign: 'center',
              gap: 3,
              p: 6,
              bgcolor: '#FAFBFF',
            }}
          >
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h6" sx={{ fontWeight: 700, color: '#374151', mb: 1 }}>
                Start building your survey
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Drag question types from the sidebar to get started
              </Typography>
              
              <Stack direction="row" spacing={2} justifyContent="center" flexWrap="wrap">
                {QUESTION_TYPES.slice(0, 4).map((type) => {
                  const Icon = type.icon;
                  return (
                    <Button
                      key={type.type}
                      variant="outlined"
                      size="small"
                      startIcon={<Icon fontSize="small" />}
                      onClick={() => addQuestion(type.type)}
                      sx={{
                        textTransform: 'none',
                        borderRadius: 999,
                        borderColor: type.color,
                        color: type.color,
                        '&:hover': {
                          borderColor: type.color,
                          bgcolor: `${type.color}08`,
                        }
                      }}
                    >
                      {type.label}
                    </Button>
                  );
                })}
              </Stack>
            </Box>
          </Paper>
        ) : (
          <Stack spacing={2}>
            {questions.map((question, index) => {
              const questionType = QUESTION_TYPES.find(q => q.type === question.type);
              const Icon = questionType?.icon || TextFields;
              
              return (
                <Paper
                  key={question.id}
                  draggable
                  onDragStart={(e) => handleDragStart(e, null, question)}
                  elevation={0}
                  sx={{
                    border: selectedQuestion?.id === question.id 
                      ? `2px solid ${questionType?.color || '#7B61FF'}` 
                      : '1px solid #E5E7EB',
                    borderRadius: 2,
                    p: 3,
                    cursor: 'move',
                    transition: 'all 0.2s',
                    '&:hover': {
                      boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
                    }
                  }}
                  onClick={() => setSelectedQuestion(question)}
                >
                  <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
                    <DragIndicator sx={{ color: '#9CA3AF', mt: 1 }} />
                    
                    <Box sx={{ flex: 1 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                        <Box sx={{
                          width: 32,
                          height: 32,
                          borderRadius: 1.5,
                          bgcolor: `${questionType?.color || '#7B61FF'}15`,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          color: questionType?.color || '#7B61FF',
                        }}>
                          <Icon fontSize="small" />
                        </Box>
                        <Chip
                          label={questionType?.label || question.type}
                          size="small"
                          sx={{
                            bgcolor: `${questionType?.color || '#7B61FF'}15`,
                            color: questionType?.color || '#7B61FF',
                            fontWeight: 600,
                            fontSize: '11px',
                          }}
                        />
                        {question.required && (
                          <Chip label="Required" size="small" color="error" />
                        )}
                      </Box>
                      
                      <Typography variant="body1" sx={{ fontWeight: 500, mb: 2 }}>
                        {question.text || `Question ${index + 1}`}
                      </Typography>
                      
                      {question.options && question.options.length > 0 && (
                        <Stack spacing={1}>
                          {question.options.map((option, optIndex) => (
                            <Box key={optIndex} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              {question.type === 'multiple_choice' && (
                                <RadioButtonChecked sx={{ fontSize: 16, color: '#9CA3AF' }} />
                              )}
                              {question.type === 'yes_no' && (
                                <RadioButtonChecked sx={{ fontSize: 16, color: '#9CA3AF' }} />
                              )}
                              {question.type === 'rating_scale' && (
                                <Star sx={{ fontSize: 16, color: '#9CA3AF' }} />
                              )}
                              <Typography variant="body2" color="text.secondary">
                                {option}
                              </Typography>
                            </Box>
                          ))}
                        </Stack>
                      )}
                    </Box>
                    
                    <IconButton size="small" sx={{ color: '#9CA3AF' }}>
                      <MoreVert />
                    </IconButton>
                  </Box>
                </Paper>
              );
            })}
          </Stack>
        )}
      </Box>
    </Box>
  );

  // Right Properties Panel
  const PropertiesPanel = () => (
    <Paper elevation={0} sx={{ 
      width: 320, 
      height: '100%', 
      borderRadius: 0, 
      borderLeft: '1px solid #E5E7EB',
      overflow: 'hidden'
    }}>
      <Box sx={{ p: 3, borderBottom: '1px solid #E5E7EB' }}>
        <Typography variant="h6" sx={{ fontWeight: 700 }}>Properties</Typography>
      </Box>
      
      <Box sx={{ p: 3, maxHeight: 'calc(100vh - 200px)', overflowY: 'auto' }}>
        {selectedQuestion ? (
          <Stack spacing={3}>
            <Box>
              <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 2 }}>
                Question Settings
              </Typography>
              
              <TextField
                fullWidth
                size="small"
                label="Question Text"
                value={selectedQuestion.text}
                onChange={(e) => updateQuestion(selectedQuestion.id, { text: e.target.value })}
                multiline
                rows={3}
                sx={{ mb: 2 }}
              />
              
              <FormControlLabel
                control={
                  <Switch
                    checked={selectedQuestion.required}
                    onChange={(e) => updateQuestion(selectedQuestion.id, { required: e.target.checked })}
                  />
                }
                label="Required"
                sx={{ mb: 2 }}
              />
              
              {selectedQuestion.options && selectedQuestion.options.length > 0 && (
                <Box>
                  <Typography variant="caption" sx={{ fontWeight: 600, mb: 1, display: 'block' }}>
                    Options
                  </Typography>
                  <Stack spacing={1}>
                    {selectedQuestion.options.map((option, index) => (
                      <TextField
                        key={index}
                        fullWidth
                        size="small"
                        value={option}
                        onChange={(e) => {
                          const newOptions = [...selectedQuestion.options];
                          newOptions[index] = e.target.value;
                          updateQuestion(selectedQuestion.id, { options: newOptions });
                        }}
                      />
                    ))}
                  </Stack>
                </Box>
              )}
            </Box>
            
            <Divider />
            
            <Box>
              <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 2 }}>
                Actions
              </Typography>
              <Stack spacing={1}>
                <Button
                  size="small"
                  startIcon={<CopyAll />}
                  onClick={() => duplicateQuestion(selectedQuestion.id)}
                >
                  Duplicate
                </Button>
                <Button
                  size="small"
                  startIcon={<Delete />}
                  color="error"
                  onClick={() => deleteQuestion(selectedQuestion.id)}
                >
                  Delete
                </Button>
              </Stack>
            </Box>
          </Stack>
        ) : (
          <Box sx={{ textAlign: 'center', py: 8 }}>
            <Typography variant="body2" color="text.secondary">
              Select a question to edit its properties
            </Typography>
          </Box>
        )}
      </Box>
    </Paper>
  );

  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column', bgcolor: '#F5F6FA' }}>
      {/* Top Header */}
      <Paper elevation={0} sx={{ borderBottom: '1px solid #E5E7EB', zIndex: 10 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', p: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <IconButton onClick={() => navigate('/dashboard')} size="small">
              <ArrowBack />
            </IconButton>
            <Box>
              <Typography variant="h6" sx={{ fontWeight: 700, lineHeight: 1.2 }}>
                Survey Builder
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {questions.length} question{questions.length !== 1 ? 's' : ''}
              </Typography>
            </Box>
          </Box>
          
          <Stack direction="row" spacing={1.5} alignItems="center">
            <Button
              variant="outlined"
              size="small"
              startIcon={<Visibility />}
              onClick={() => setShowPreview(true)}
              sx={{ textTransform: 'none', borderRadius: 999 }}
            >
              Preview
            </Button>
            
            <Button
              variant="outlined"
              size="small"
              startIcon={<Share />}
              onClick={(e) => setDistributionMenu(e.currentTarget)}
              sx={{ textTransform: 'none', borderRadius: 999 }}
            >
              Distribute
            </Button>
            
            <Button
              variant="contained"
              size="small"
              startIcon={<Save />}
              onClick={handleSaveSurvey}
              disabled={saving}
              sx={{ 
                textTransform: 'none', 
                borderRadius: 999, 
                px: 3,
                bgcolor: '#7B61FF',
                '&:hover': { bgcolor: '#6B4FE0' }
              }}
            >
              {saving ? 'Saving...' : 'Save'}
            </Button>
          </Stack>
        </Box>
      </Paper>

      {/* Main Content */}
      <Box sx={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        <QuestionTypesSidebar />
        <SurveyCanvas />
        <PropertiesPanel />
      </Box>

      {/* Distribution Menu */}
      <Menu
        anchorEl={distributionMenu}
        open={Boolean(distributionMenu)}
        onClose={() => setDistributionMenu(null)}
      >
        <MenuItem onClick={() => setDistributionMenu(null)}>
          <PhoneIcon sx={{ mr: 2 }} /> Phone Survey
        </MenuItem>
        <MenuItem onClick={() => setDistributionMenu(null)}>
          <Public sx={{ mr: 2 }} /> Web Link
        </MenuItem>
        <MenuItem onClick={() => setDistributionMenu(null)}>
          <QrCode2 sx={{ mr: 2 }} /> QR Code
        </MenuItem>
      </Menu>

      {/* Notification */}
      <Snackbar
        open={notification.open}
        autoHideDuration={3000}
        onClose={() => setNotification(n => ({ ...n, open: false }))}
        anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
      >
        <MuiAlert
          onClose={() => setNotification(n => ({ ...n, open: false }))}
          severity={notification.severity}
          sx={{ width: '100%' }}
        >
          {notification.message}
        </MuiAlert>
      </Snackbar>
    </Box>
  );
};

export default SurveyBuilderAdvanced;
