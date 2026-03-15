import { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  TextField,
  Button,
  Card,
  CardContent,
  Grid,
  Alert,
  Snackbar,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  IconButton,
  Paper,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  ArrowBack,
  Add,
  Delete,
  Edit,
  Save,
  Send,
  ExpandMore,
  DragIndicator,
  Settings,
} from '@mui/icons-material';

const SurveyBuilderDirect = () => {
  const [templates, setTemplates] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [surveyTitle, setSurveyTitle] = useState('');
  const [surveyDescription, setSurveyDescription] = useState('');
  const [questions, setQuestions] = useState([]);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    fetchTemplates();
  }, []);

  const fetchTemplates = async () => {
    try {
      const response = await fetch('/api/templates/list');
      if (response.ok) {
        const data = await response.json();
        setTemplates(data);
      }
    } catch (error) {
      console.error('Error fetching templates:', error);
    }
  };

  const showNotification = (message, severity = 'success') => {
    setNotification({ open: true, message, severity });
  };

  const handleCloseNotification = () => {
    setNotification({ ...notification, open: false });
  };

  const handleTemplateChange = async (templateId) => {
    setSelectedTemplate(templateId);
    
    if (templateId) {
      try {
        const response = await fetch(`/api/templates/getquestions?template_id=${templateId}`);
        if (response.ok) {
          const data = await response.json();
          setQuestions(data.Questions || []);
          setSurveyTitle(data.TemplateName || '');
          setSurveyDescription(data.Description || '');
        }
      } catch (error) {
        console.error('Error loading template questions:', error);
      }
    }
  };

  const addQuestion = () => {
    const newQuestion = {
      id: `q_${Date.now()}`,
      QuestionText: '',
      QuestionType: 'text',
      Options: [],
      Required: false,
    };
    setQuestions([...questions, newQuestion]);
  };

  const updateQuestion = (index, field, value) => {
    const updatedQuestions = [...questions];
    updatedQuestions[index] = { ...updatedQuestions[index], [field]: value };
    setQuestions(updatedQuestions);
  };

  const deleteQuestion = (index) => {
    const updatedQuestions = questions.filter((_, i) => i !== index);
    setQuestions(updatedQuestions);
  };

  const addOption = (questionIndex) => {
    const updatedQuestions = [...questions];
    const question = updatedQuestions[questionIndex];
    const newOption = `Option ${question.Options.length + 1}`;
    question.Options = [...question.Options, newOption];
    setQuestions(updatedQuestions);
  };

  const updateOption = (questionIndex, optionIndex, value) => {
    const updatedQuestions = [...questions];
    updatedQuestions[questionIndex].Options[optionIndex] = value;
    setQuestions(updatedQuestions);
  };

  const deleteOption = (questionIndex, optionIndex) => {
    const updatedQuestions = [...questions];
    const question = updatedQuestions[questionIndex];
    question.Options = question.Options.filter((_, i) => i !== optionIndex);
    setQuestions(updatedQuestions);
  };

  const saveSurvey = async () => {
    if (!surveyTitle || questions.length === 0) {
      showNotification('Please add a title and at least one question', 'error');
      return;
    }

    setIsProcessing(true);
    try {
      const surveyData = {
        TemplateName: surveyTitle,
        Description: surveyDescription,
        Questions: questions,
        Status: 'draft',
      };

      const response = await fetch('/api/templates/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(surveyData),
      });

      if (response.ok) {
        showNotification('Survey saved successfully!', 'success');
      } else {
        const errorData = await response.json();
        showNotification(`Error saving survey: ${errorData.detail || 'Unknown error'}`, 'error');
      }
    } catch (error) {
      console.error('Error saving survey:', error);
      showNotification('Error saving survey. Please try again.', 'error');
    } finally {
      setIsProcessing(false);
    }
  };

  const launchSurvey = async () => {
    if (!surveyTitle || questions.length === 0) {
      showNotification('Please add a title and at least one question', 'error');
      return;
    }

    setIsProcessing(true);
    try {
      const surveyId = `survey_${Date.now()}`;
      const surveyData = {
        SurveyId: surveyId,
        template_name: surveyTitle,
        Recipient: 'Survey Builder User',
        RiderName: 'Test Rider',
        RideId: 'builder_test',
        TenantId: 'demo_tenant',
        Phone: '+1234567890',
        URL: `http://54.86.65.150:8080/survey/${surveyId}`,
        Bilingual: false,
        Name: surveyTitle,
      };

      const response = await fetch('/api/surveys/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(surveyData),
      });

      if (response.ok) {
        const result = await response.json();
        showNotification(`Survey launched successfully! Generated ${result.QuestionswithAns?.length || 0} questions.`, 'success');
      } else {
        const errorData = await response.json();
        showNotification(`Error launching survey: ${errorData.detail || 'Unknown error'}`, 'error');
      }
    } catch (error) {
      console.error('Error launching survey:', error);
      showNotification('Error launching survey. Please try again.', 'error');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleBack = () => {
    window.history.back();
  };

  const getQuestionTypeIcon = (type) => {
    switch (type) {
      case 'text': return '📝';
      case 'multiple_choice': return '🔘';
      case 'rating': return '⭐';
      case 'yes_no': return '✅';
      default: return '❓';
    }
  };

  return (
    <Box sx={{ p: 3, minHeight: '100vh', bgcolor: '#f5f5f5' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <Button onClick={handleBack} sx={{ mr: 2 }}>
          <ArrowBack />
        </Button>
        <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#1976d2' }}>
          Survey Builder
        </Typography>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card sx={{ mb: 3 }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold' }}>
                Survey Details
              </Typography>
              
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth sx={{ mb: 2 }}>
                    <InputLabel>Load from Template (Optional)</InputLabel>
                    <Select
                      value={selectedTemplate}
                      onChange={(e) => handleTemplateChange(e.target.value)}
                      label="Load from Template"
                    >
                      <MenuItem value="">Create New Survey</MenuItem>
                      {templates.map((template, index) => (
                        <MenuItem key={index} value={template.TemplateName || template.name}>
                          {template.TemplateName || template.name}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>

                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Survey Title *"
                    value={surveyTitle}
                    onChange={(e) => setSurveyTitle(e.target.value)}
                    sx={{ mb: 2 }}
                    placeholder="Enter your survey title"
                  />
                </Grid>

                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Survey Description"
                    value={surveyDescription}
                    onChange={(e) => setSurveyDescription(e.target.value)}
                    sx={{ mb: 2 }}
                    multiline
                    rows={3}
                    placeholder="Describe your survey purpose"
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>

          <Card sx={{ mb: 3 }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                  Questions ({questions.length})
                </Typography>
                <Button
                  variant="contained"
                  onClick={addQuestion}
                  startIcon={<Add />}
                >
                  Add Question
                </Button>
              </Box>

              {questions.length === 0 ? (
                <Box sx={{ textAlign: 'center', py: 4, color: '#666' }}>
                  <Typography variant="body1">
                    No questions yet. Click "Add Question" to get started.
                  </Typography>
                </Box>
              ) : (
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  {questions.map((question, index) => (
                    <Accordion key={question.id} sx={{ bgcolor: 'white' }}>
                      <AccordionSummary expandIcon={<ExpandMore />}>
                        <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                          <DragIndicator sx={{ mr: 2, color: '#666' }} />
                          <Typography sx={{ mr: 2 }}>
                            {getQuestionTypeIcon(question.QuestionType)} Question {index + 1}
                          </Typography>
                          <Typography variant="body2" sx={{ color: '#666', flexGrow: 1, textAlign: 'left' }}>
                            {question.QuestionText || 'Untitled Question'}
                          </Typography>
                          <Chip 
                            label={question.Required ? 'Required' : 'Optional'} 
                            size="small" 
                            color={question.Required ? 'primary' : 'default'}
                            sx={{ mr: 2 }}
                          />
                          <IconButton
                            size="small"
                            onClick={(e) => {
                              e.stopPropagation();
                              deleteQuestion(index);
                            }}
                          >
                            <Delete />
                          </IconButton>
                        </Box>
                      </AccordionSummary>
                      <AccordionDetails>
                        <Grid container spacing={2}>
                          <Grid item xs={12} md={6}>
                            <TextField
                              fullWidth
                              label="Question Text"
                              value={question.QuestionText}
                              onChange={(e) => updateQuestion(index, 'QuestionText', e.target.value)}
                              placeholder="Enter your question"
                            />
                          </Grid>
                          <Grid item xs={12} md={3}>
                            <FormControl fullWidth>
                              <InputLabel>Question Type</InputLabel>
                              <Select
                                value={question.QuestionType}
                                onChange={(e) => updateQuestion(index, 'QuestionType', e.target.value)}
                                label="Question Type"
                              >
                                <MenuItem value="text">Text</MenuItem>
                                <MenuItem value="multiple_choice">Multiple Choice</MenuItem>
                                <MenuItem value="rating">Rating</MenuItem>
                                <MenuItem value="yes_no">Yes/No</MenuItem>
                              </Select>
                            </FormControl>
                          </Grid>
                          <Grid item xs={12} md={3}>
                            <FormControl fullWidth>
                              <InputLabel>Required</InputLabel>
                              <Select
                                value={question.Required ? 'true' : 'false'}
                                onChange={(e) => updateQuestion(index, 'Required', e.target.value === 'true')}
                                label="Required"
                              >
                                <MenuItem value="true">Required</MenuItem>
                                <MenuItem value="false">Optional</MenuItem>
                              </Select>
                            </FormControl>
                          </Grid>

                          {question.QuestionType === 'multiple_choice' && (
                            <Grid item xs={12}>
                              <Typography variant="subtitle2" sx={{ mb: 2 }}>
                                Options:
                              </Typography>
                              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                                {question.Options.map((option, optionIndex) => (
                                  <Box key={optionIndex} sx={{ display: 'flex', gap: 1 }}>
                                    <TextField
                                      fullWidth
                                      size="small"
                                      value={option}
                                      onChange={(e) => updateOption(index, optionIndex, e.target.value)}
                                      placeholder={`Option ${optionIndex + 1}`}
                                    />
                                    <IconButton
                                      size="small"
                                      onClick={() => deleteOption(index, optionIndex)}
                                    >
                                      <Delete />
                                    </IconButton>
                                  </Box>
                                ))}
                                <Button
                                  variant="outlined"
                                  size="small"
                                  onClick={() => addOption(index)}
                                  startIcon={<Add />}
                                >
                                  Add Option
                                </Button>
                              </Box>
                            </Grid>
                          )}
                        </Grid>
                      </AccordionDetails>
                    </Accordion>
                  ))}
                </Box>
              )}
            </CardContent>
          </Card>

          <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
            <Button
              variant="contained"
              onClick={saveSurvey}
              disabled={isProcessing}
              startIcon={<Save />}
              sx={{ px: 4 }}
            >
              {isProcessing ? 'Saving...' : 'Save as Template'}
            </Button>
            <Button
              variant="contained"
              color="success"
              onClick={launchSurvey}
              disabled={isProcessing}
              startIcon={<Send />}
              sx={{ px: 4 }}
            >
              {isProcessing ? 'Launching...' : 'Launch Survey'}
            </Button>
            <Button
              variant="outlined"
              onClick={handleBack}
              startIcon={<ArrowBack />}
            >
              Cancel
            </Button>
          </Box>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
                Survey Builder Guide
              </Typography>
              <Typography variant="body2" sx={{ mb: 2 }}>
                1. Enter a title for your survey
              </Typography>
              <Typography variant="body2" sx={{ mb: 2 }}>
                2. Add questions using the "Add Question" button
              </Typography>
              <Typography variant="body2" sx={{ mb: 2 }}>
                3. Configure question types and options
              </Typography>
              <Typography variant="body2" sx={{ mb: 2 }}>
                4. Mark questions as required or optional
              </Typography>
              <Typography variant="body2" sx={{ mb: 2 }}>
                5. Save as template or launch directly
              </Typography>
              
              <Divider sx={{ my: 2 }} />
              
              <Typography variant="subtitle2" sx={{ mb: 1, color: '#1976d2' }}>
                Question Types:
              </Typography>
              <Typography variant="body2" sx={{ mb: 1 }}>
                • 📝 Text: Open-ended responses
              </Typography>
              <Typography variant="body2" sx={{ mb: 1 }}>
                • 🔘 Multiple Choice: Select from options
              </Typography>
              <Typography variant="body2" sx={{ mb: 1 }}>
                • ⭐ Rating: Scale ratings
              </Typography>
              <Typography variant="body2" sx={{ mb: 2 }}>
                • ✅ Yes/No: Binary responses
              </Typography>
              
              <Box sx={{ mt: 2, p: 2, bgcolor: '#e3f2fd', borderRadius: 1 }}>
                <Typography variant="body2" sx={{ color: '#1976d2' }}>
                  💡 Pro Tip: Load from existing templates to get started quickly!
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Snackbar
        open={notification.open}
        autoHideDuration={6000}
        onClose={handleCloseNotification}
      >
        <Alert onClose={handleCloseNotification} severity={notification.severity}>
          {notification.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default SurveyBuilderDirect;
