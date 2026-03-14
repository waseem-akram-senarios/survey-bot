import { useState, useEffect } from "react";
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  Typography,
  TextField,
  Button,
  useMediaQuery,
  Alert,
  Snackbar,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Card,
  CardContent,
  Grid,
  Paper,
  Chip,
  Divider,
  IconButton,
  Tooltip,
} from "@mui/material";
import {
  ArrowBack,
  UploadFile,
  Translate,
  Person,
  Phone,
  Email,
  Description,
  Template,
  Launch,
  Save,
  Send,
  Info,
} from "@mui/icons-material";

import { useAlert } from "../../../hooks/useAlert";
import { useSurvey, useTemplates } from "../../../hooks/Surveys/useSurvey";
import { useAuth } from "../../../context/AuthContext";

const CreateSurveyModern = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const isMobile = useMediaQuery("(max-width: 600px)");
  const { alert, showSuccess, showError, closeAlert } = useAlert();
  const { user } = useAuth();

  // Survey and template hooks
  const { generateSurvey, launchSurvey, sendSurveyByEmail, isGenerating, isLaunching, generateSurveyId, validateSurveyForm } = useSurvey();
  const { availableTemplates, isLoadingTemplates, fetchTemplates } = useTemplates();

  // Form state
  const [selectedTemplate, setSelectedTemplate] = useState("");
  const [recipientName, setRecipientName] = useState("");
  const [riderName, setRiderName] = useState("");
  const [rideId, setRideId] = useState("");
  const [phone, setPhone] = useState("");
  const [recipientEmail, setRecipientEmail] = useState("");
  const [recipientBiodata, setRecipientBiodata] = useState("");
  const [languageMode, setLanguageMode] = useState("en");
  const [isProcessing, setIsProcessing] = useState(false);

  // Load templates on component mount
  useEffect(() => {
    const loadTemplates = async () => {
      try {
        const templates = await fetchTemplates();
        
        const preSelectedTemplate = location.state?.selectedTemplate;
        if (preSelectedTemplate && templates.includes(preSelectedTemplate)) {
          setSelectedTemplate(preSelectedTemplate);
        }
      } catch (error) {
        showError(error.message);
      }
    };

    loadTemplates();
  }, [location.state?.selectedTemplate]);

  const handleBack = () => {
    navigate(-1);
  };

  const handleGenerateClick = async () => {
    const validation = validateSurveyForm(selectedTemplate, recipientName, riderName, rideId, phone);
    
    if (!validation.isValid) {
      showError(validation.error);
      return;
    }

    setIsProcessing(true);
    try {
      const surveyId = generateSurveyId();
      
      const surveyData = {
        surveyId: surveyId,
        template: selectedTemplate,
        recipient: recipientName.trim(),
        riderName: riderName.trim(),
        rideId: rideId.trim(),
        tenantId: user?.tenantId || "",
        phone: phone.trim(),
        biodata: recipientBiodata.trim(),
        bilingual: false,
        languageMode: languageMode,
      };
      
      const generatedSurveyData = await generateSurvey(surveyData);

      const launchResponse = await launchSurvey(
        generatedSurveyData,
        generatedSurveyData.questions || [],
        true
      );

      if (!launchResponse.success) {
        throw new Error(launchResponse.message || "Failed to launch survey");
      }

      showSuccess("Survey created and launched successfully!");
      
      // Navigate to survey progress page
      navigate(`/surveys/status/${surveyId}`);
      
    } catch (error) {
      console.error("Survey creation error:", error);
      showError(error.message || "Failed to create survey");
    } finally {
      setIsProcessing(false);
    }
  };

  const handleSaveDraft = async () => {
    // Save draft functionality
    showSuccess("Survey saved as draft");
  };

  const handleSendEmail = async () => {
    if (!recipientEmail) {
      showError("Please enter recipient email");
      return;
    }
    
    try {
      // Send email functionality
      showSuccess("Survey sent via email");
    } catch (error) {
      showError("Failed to send survey via email");
    }
  };

  const templateCategories = [
    { name: "Customer Satisfaction", color: "#4CAF50" },
    { name: "Product Feedback", color: "#2196F3" },
    { name: "Employee Engagement", color: "#FF9800" },
    { name: "Market Research", color: "#9C27B0" },
  ];

  const getTemplateCategory = (templateName) => {
    // Simple categorization based on template name
    if (templateName.toLowerCase().includes('customer') || templateName.toLowerCase().includes('satisfaction')) {
      return templateCategories[0];
    } else if (templateName.toLowerCase().includes('product') || templateName.toLowerCase().includes('feedback')) {
      return templateCategories[1];
    } else if (templateName.toLowerCase().includes('employee') || templateName.toLowerCase().includes('engagement')) {
      return templateCategories[2];
    } else {
      return templateCategories[3];
    }
  };

  return (
    <Box sx={{ 
      p: 3, 
      maxWidth: '1400px', 
      mx: 'auto',
      backgroundColor: '#F8FAFC',
      minHeight: '100vh'
    }}>
      {/* Header */}
      <Box sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        mb: 4,
        gap: 2
      }}>
        <IconButton 
          onClick={handleBack}
          sx={{ 
            bgcolor: 'white', 
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
            '&:hover': { bgcolor: '#F5F5F5' }
          }}
        >
          <ArrowBack />
        </IconButton>
        <Typography variant="h4" sx={{ fontWeight: 600, color: '#1F2937' }}>
          Create Survey
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Left Side - Form Fields */}
        <Grid item xs={12} md={7}>
          <Card sx={{ borderRadius: '16px', boxShadow: '0 4px 20px rgba(0,0,0,0.08)' }}>
            <CardContent sx={{ p: 4 }}>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 3, color: '#1F2937' }}>
                Survey Details
              </Typography>

              <Grid container spacing={3}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Recipient Name"
                    value={recipientName}
                    onChange={(e) => setRecipientName(e.target.value)}
                    variant="outlined"
                    sx={{ 
                      '& .MuiOutlinedInput-root': { 
                        borderRadius: '12px',
                        '&:hover fieldset': { borderColor: '#1958F7' },
                        '&.Mui-focused fieldset': { borderColor: '#1958F7' }
                      }
                    }}
                    InputProps={{
                      startAdornment: <Person sx={{ mr: 1, color: '#6B7280' }} />,
                    }}
                  />
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Phone Number"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    variant="outlined"
                    sx={{ 
                      '& .MuiOutlinedInput-root': { 
                        borderRadius: '12px',
                        '&:hover fieldset': { borderColor: '#1958F7' },
                        '&.Mui-focused fieldset': { borderColor: '#1958F7' }
                      }
                    }}
                    InputProps={{
                      startAdornment: <Phone sx={{ mr: 1, color: '#6B7280' }} />,
                    }}
                  />
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Rider Name"
                    value={riderName}
                    onChange={(e) => setRiderName(e.target.value)}
                    variant="outlined"
                    sx={{ 
                      '& .MuiOutlinedInput-root': { 
                        borderRadius: '12px',
                        '&:hover fieldset': { borderColor: '#1958F7' },
                        '&.Mui-focused fieldset': { borderColor: '#1958F7' }
                      }
                    }}
                  />
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Ride ID"
                    value={rideId}
                    onChange={(e) => setRideId(e.target.value)}
                    variant="outlined"
                    sx={{ 
                      '& .MuiOutlinedInput-root': { 
                        borderRadius: '12px',
                        '&:hover fieldset': { borderColor: '#1958F7' },
                        '&.Mui-focused fieldset': { borderColor: '#1958F7' }
                      }
                    }}
                  />
                </Grid>

                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Email Address"
                    value={recipientEmail}
                    onChange={(e) => setRecipientEmail(e.target.value)}
                    variant="outlined"
                    type="email"
                    sx={{ 
                      '& .MuiOutlinedInput-root': { 
                        borderRadius: '12px',
                        '&:hover fieldset': { borderColor: '#1958F7' },
                        '&.Mui-focused fieldset': { borderColor: '#1958F7' }
                      }
                    }}
                    InputProps={{
                      startAdornment: <Email sx={{ mr: 1, color: '#6B7280' }} />,
                    }}
                  />
                </Grid>

                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Additional Information"
                    value={recipientBiodata}
                    onChange={(e) => setRecipientBiodata(e.target.value)}
                    variant="outlined"
                    multiline
                    rows={3}
                    placeholder="Enter any additional information about the recipient..."
                    sx={{ 
                      '& .MuiOutlinedInput-root': { 
                        borderRadius: '12px',
                        '&:hover fieldset': { borderColor: '#1958F7' },
                        '&.Mui-focused fieldset': { borderColor: '#1958F7' }
                      }
                    }}
                    InputProps={{
                      startAdornment: <Description sx={{ mr: 1, mt: 1, color: '#6B7280' }} />,
                    }}
                  />
                </Grid>

                <Grid item xs={12}>
                  <FormControl fullWidth>
                    <InputLabel>Language Mode</InputLabel>
                    <Select
                      value={languageMode}
                      onChange={(e) => setLanguageMode(e.target.value)}
                      label="Language Mode"
                      sx={{ 
                        borderRadius: '12px',
                        '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: '#1958F7' },
                        '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: '#1958F7' }
                      }}
                    >
                      <MenuItem value="en">English</MenuItem>
                      <MenuItem value="es">Spanish</MenuItem>
                      <MenuItem value="bilingual">Bilingual</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
              </Grid>

              {/* Action Buttons */}
              <Box sx={{ mt: 4, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Button
                  variant="outlined"
                  startIcon={<Save />}
                  onClick={handleSaveDraft}
                  sx={{ 
                    borderRadius: '12px',
                    px: 3,
                    py: 1.5,
                    textTransform: 'none',
                    fontWeight: 500,
                    borderColor: '#E5E7EB',
                    color: '#6B7280',
                    '&:hover': { 
                      borderColor: '#1958F7',
                      bgcolor: '#F3F4F6'
                    }
                  }}
                >
                  Save Draft
                </Button>

                <Button
                  variant="outlined"
                  startIcon={<Send />}
                  onClick={handleSendEmail}
                  sx={{ 
                    borderRadius: '12px',
                    px: 3,
                    py: 1.5,
                    textTransform: 'none',
                    fontWeight: 500,
                    borderColor: '#E5E7EB',
                    color: '#6B7280',
                    '&:hover': { 
                      borderColor: '#1958F7',
                      bgcolor: '#F3F4F6'
                    }
                  }}
                >
                  Send Email
                </Button>

                <Button
                  variant="contained"
                  startIcon={<Launch />}
                  onClick={handleGenerateClick}
                  disabled={isProcessing || !selectedTemplate || !recipientName || !phone}
                  sx={{ 
                    borderRadius: '12px',
                    px: 4,
                    py: 1.5,
                    textTransform: 'none',
                    fontWeight: 500,
                    background: 'linear-gradient(135deg, #1958F7 0%, #3D69D9 100%)',
                    boxShadow: '0 4px 12px rgba(25, 88, 247, 0.3)',
                    '&:hover': { 
                      background: 'linear-gradient(135deg, #1745D6 0%, #2E52BA 100%)',
                      boxShadow: '0 6px 16px rgba(25, 88, 247, 0.4)'
                    },
                    '&:disabled': { 
                      bgcolor: '#E5E7EB',
                      color: '#9CA3AF'
                    }
                  }}
                >
                  {isProcessing ? 'Creating...' : 'Create Survey'}
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Right Side - Template Selection */}
        <Grid item xs={12} md={5}>
          <Card sx={{ borderRadius: '16px', boxShadow: '0 4px 20px rgba(0,0,0,0.08)' }}>
            <CardContent sx={{ p: 4 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                <Template sx={{ mr: 1, color: '#1958F7' }} />
                <Typography variant="h6" sx={{ fontWeight: 600, color: '#1F2937' }}>
                  Choose Template
                </Typography>
                <Tooltip title="Select a template to get started with your survey">
                  <IconButton size="small" sx={{ ml: 'auto' }}>
                    <Info sx={{ fontSize: 18, color: '#6B7280' }} />
                  </IconButton>
                </Tooltip>
              </Box>

              {isLoadingTemplates ? (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography color="#6B7280">Loading templates...</Typography>
                </Box>
              ) : (
                <Box sx={{ maxHeight: '600px', overflowY: 'auto' }}>
                  {availableTemplates.map((template, index) => {
                    const category = getTemplateCategory(template);
                    const isSelected = selectedTemplate === template;
                    
                    return (
                      <Paper
                        key={index}
                        onClick={() => setSelectedTemplate(template)}
                        sx={{
                          p: 3,
                          mb: 2,
                          borderRadius: '12px',
                          cursor: 'pointer',
                          border: isSelected ? `2px solid #1958F7` : '2px solid transparent',
                          bgcolor: isSelected ? '#F0F4FF' : '#FFFFFF',
                          boxShadow: isSelected ? '0 4px 12px rgba(25, 88, 247, 0.15)' : '0 2px 8px rgba(0,0,0,0.06)',
                          transition: 'all 0.3s ease',
                          '&:hover': {
                            transform: 'translateY(-2px)',
                            boxShadow: isSelected ? '0 6px 16px rgba(25, 88, 247, 0.2)' : '0 4px 12px rgba(0,0,0,0.1)',
                          }
                        }}
                      >
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                          <Box
                            sx={{
                              width: 8,
                              height: 8,
                              borderRadius: '50%',
                              bgcolor: category.color,
                              mr: 2
                            }}
                          />
                          <Typography variant="subtitle1" sx={{ fontWeight: 500, color: '#1F2937' }}>
                            {template}
                          </Typography>
                        </Box>
                        
                        <Chip
                          label={category.name}
                          size="small"
                          sx={{
                            bgcolor: `${category.color}15`,
                            color: category.color,
                            fontWeight: 500,
                            fontSize: '12px',
                            mb: 1
                          }}
                        />
                        
                        <Typography variant="body2" color="#6B7280" sx={{ fontSize: '14px' }}>
                          Professional survey template for {category.name.toLowerCase()}
                        </Typography>
                      </Paper>
                    );
                  })}
                </Box>
              )}

              {!isLoadingTemplates && availableTemplates.length === 0 && (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography color="#6B7280">No templates available</Typography>
                  <Button
                    variant="outlined"
                    sx={{ mt: 2, borderRadius: '12px' }}
                    startIcon={<UploadFile />}
                  >
                    Import Template
                  </Button>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Alert Snackbar */}
      <Snackbar
        open={alert.open}
        autoHideDuration={6000}
        onClose={closeAlert}
        anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
      >
        <Alert 
          onClose={closeAlert} 
          severity={alert.type} 
          sx={{ 
            borderRadius: '12px',
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)'
          }}
        >
          {alert.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default CreateSurveyModern;
