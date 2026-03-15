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
} from '@mui/material';
import { ArrowBack, Save, Send } from '@mui/icons-material';

const CreateSurveyDirect = () => {
  const [templates, setTemplates] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [recipientName, setRecipientName] = useState('');
  const [riderName, setRiderName] = useState('');
  const [rideId, setRideId] = useState('');
  const [phone, setPhone] = useState('');
  const [recipientEmail, setRecipientEmail] = useState('');
  const [languageMode, setLanguageMode] = useState('en');
  const [isProcessing, setIsProcessing] = useState(false);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });

  useEffect(() => {
    fetchTemplates();
  }, []);

  const fetchTemplates = async () => {
    try {
      const response = await fetch('/pg/api/templates/list');
      if (response.ok) {
        const data = await response.json();
        setTemplates(data);
        if (data.length > 0) {
          setSelectedTemplate(data[0].TemplateName || data[0].name);
        }
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

  const handleCreateSurvey = async () => {
    if (!selectedTemplate || !recipientName || !phone) {
      showNotification('Please fill in all required fields', 'error');
      return;
    }

    setIsProcessing(true);
    try {
      const surveyId = `survey_${Date.now()}`;
      const surveyData = {
        SurveyId: surveyId,
        template_name: selectedTemplate,
        Recipient: recipientName.trim(),
        RiderName: riderName.trim(),
        RideId: rideId.trim(),
        TenantId: 'demo_tenant',
        Phone: phone.trim(),
        URL: `http://54.86.65.150:8080/survey/${surveyId}`,
        Bilingual: languageMode === 'bilingual',
        Name: `${recipientName}'s Survey`
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
        showNotification(`Survey created successfully! Generated ${result.QuestionswithAns?.length || 0} questions.`, 'success');
        
        // Clear form
        setSelectedTemplate('');
        setRecipientName('');
        setRiderName('');
        setRideId('');
        setPhone('');
        setRecipientEmail('');
        setLanguageMode('en');
      } else {
        const errorData = await response.json();
        showNotification(`Error creating survey: ${errorData.detail || 'Unknown error'}`, 'error');
      }
    } catch (error) {
      console.error('Error creating survey:', error);
      showNotification('Error creating survey. Please try again.', 'error');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleBack = () => {
    window.history.back();
  };

  return (
    <Box sx={{ p: 3, minHeight: '100vh', bgcolor: '#f5f5f5' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <Button onClick={handleBack} sx={{ mr: 2 }}>
          <ArrowBack />
        </Button>
        <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#1976d2' }}>
          Create Survey
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
                    <InputLabel>Template</InputLabel>
                    <Select
                      value={selectedTemplate}
                      onChange={(e) => setSelectedTemplate(e.target.value)}
                      label="Template"
                    >
                      {templates.map((template, index) => (
                        <MenuItem key={index} value={template.TemplateName || template.name}>
                          {template.TemplateName || template.name}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>

                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Recipient Name *"
                    value={recipientName}
                    onChange={(e) => setRecipientName(e.target.value)}
                    sx={{ mb: 2 }}
                  />
                </Grid>

                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Phone Number *"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    sx={{ mb: 2 }}
                  />
                </Grid>

                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Rider Name"
                    value={riderName}
                    onChange={(e) => setRiderName(e.target.value)}
                    sx={{ mb: 2 }}
                  />
                </Grid>

                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Ride ID"
                    value={rideId}
                    onChange={(e) => setRideId(e.target.value)}
                    sx={{ mb: 2 }}
                  />
                </Grid>

                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Email (Optional)"
                    value={recipientEmail}
                    onChange={(e) => setRecipientEmail(e.target.value)}
                    sx={{ mb: 2 }}
                  />
                </Grid>

                <Grid item xs={12} md={6}>
                  <FormControl fullWidth sx={{ mb: 2 }}>
                    <InputLabel>Language Mode</InputLabel>
                    <Select
                      value={languageMode}
                      onChange={(e) => setLanguageMode(e.target.value)}
                      label="Language Mode"
                    >
                      <MenuItem value="en">English Only</MenuItem>
                      <MenuItem value="bilingual">Bilingual (English/Spanish)</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
              </Grid>

              <Box sx={{ display: 'flex', gap: 2, mt: 3 }}>
                <Button
                  variant="contained"
                  onClick={handleCreateSurvey}
                  disabled={isProcessing}
                  startIcon={<Save />}
                  sx={{ px: 4 }}
                >
                  {isProcessing ? 'Creating...' : 'Create Survey'}
                </Button>
                <Button
                  variant="outlined"
                  onClick={handleBack}
                  startIcon={<ArrowBack />}
                >
                  Cancel
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
                Quick Guide
              </Typography>
              <Typography variant="body2" sx={{ mb: 2 }}>
                1. Select a template from the dropdown
              </Typography>
              <Typography variant="body2" sx={{ mb: 2 }}>
                2. Enter recipient details (required fields marked with *)
              </Typography>
              <Typography variant="body2" sx={{ mb: 2 }}>
                3. Choose language mode (English or Bilingual)
              </Typography>
              <Typography variant="body2" sx={{ mb: 2 }}>
                4. Click "Create Survey" to generate
              </Typography>
              <Typography variant="body2" sx={{ color: '#666' }}>
                The survey will be created instantly and you can view the generated questions.
              </Typography>
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

export default CreateSurveyDirect;
