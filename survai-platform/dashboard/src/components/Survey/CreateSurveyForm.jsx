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
} from "@mui/material";

import { useAlert } from "../../hooks/useAlert";
import { useSurvey, useTemplates } from "../../hooks/Surveys/useSurvey";

const CreateSurveyForm = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const isMobile = useMediaQuery("(max-width: 600px)");
  const { alert, showSuccess, showError, closeAlert } = useAlert();

  // Survey and template hooks
  const { generateSurvey, isGenerating, generateSurveyId, validateSurveyForm } = useSurvey();
  const { availableTemplates, isLoadingTemplates, fetchTemplates } = useTemplates();

  // Form state
  const [selectedTemplate, setSelectedTemplate] = useState("");
  const [recipientName, setRecipientName] = useState("");
  const [riderName, setRiderName] = useState("");
  const [rideId, setRideId] = useState("");
  const [tenantId, setTenantId] = useState("");
  const [recipientBiodata, setRecipientBiodata] = useState("");

  // Load templates on component mount and handle pre-selected template
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
    const validation = validateSurveyForm(selectedTemplate, recipientName, riderName, rideId, tenantId);
    
    if (!validation.isValid) {
      showError(validation.error);
      return;
    }

    try {
      const surveyId = generateSurveyId();
      
      const surveyData = {
        surveyId: surveyId,
        template: selectedTemplate,
        recipient: recipientName.trim(),
        riderName: riderName.trim(),
        rideId: rideId.trim(),
        tenantId: tenantId.trim(),
        biodata: recipientBiodata.trim()
      };
      
      const generatedSurveyData = await generateSurvey(surveyData);
      
      showSuccess("Survey generated successfully!");
      
      navigate('/surveys/generated', { 
        state: { surveyData: generatedSurveyData } 
      });
      
    } catch (error) {
      console.error("Failed to generate survey:", error);
      showError(error.message || "Failed to generate survey. Please try again.");
    }
  };

  return (
    <>
      <Box
        sx={{
          p: isMobile ? 2 : 4,
          backgroundColor: "#fff",
          width: isMobile ? "90%" : "750px",
          maxHeight: "750px",
          borderRadius: "20px",
          overflowY: "auto",
          overflowX: isMobile ? "auto" : "hidden",
          ...(isMobile && {
            scrollbarWidth: "none",
            "&::-webkit-scrollbar": { display: "none" },
          }),
        }}
      >
        <Box>
          {/* Header */}
          <Box sx={{ mb: 4 }}>
            <Typography
              sx={{
                fontFamily: "Poppins, sans-serif",
                fontWeight: 500,
                fontSize: "18px",
                lineHeight: "100%",
                color: "#1E1E1E",
                mb: 1,
              }}
            >
              Launch New Survey
            </Typography>
          </Box>

          {/* Select Template */}
          <Box sx={{ mb: 4 }}>
            <Typography
              sx={{
                fontFamily: "Poppins, sans-serif",
                fontWeight: 400,
                fontSize: "14px",
                lineHeight: "100%",
                color: "#1E1E1E",
                mb: 1.5,
              }}
            >
              Select Template
            </Typography>
            <Typography
              sx={{
                fontFamily: "Poppins, sans-serif",
                fontWeight: 400,
                fontSize: "12px",
                lineHeight: "100%",
                color: "#7D7D7D",
                mb: 2,
              }}
            >
              This template will serve as the base for this survey
            </Typography>
            
            <FormControl fullWidth>
              <Select
                value={selectedTemplate}
                onChange={(e) => setSelectedTemplate(e.target.value)}
                displayEmpty
                disabled={isLoadingTemplates}
                sx={{
                  backgroundColor: "#fff",
                  borderRadius: "15px",
                  boxShadow: "0px 4px 20px 0px #0000000D",
                  "& fieldset": {
                    border: "none",
                  },
                  "& .MuiSelect-select": {
                    fontFamily: "Poppins, sans-serif",
                    fontWeight: 400,
                    fontSize: "14px",
                    lineHeight: "100%",
                    color: selectedTemplate ? "#1E1E1E" : "#7D7D7D",
                    padding: "12px 14px",
                  },
                }}
              >
                <MenuItem value="" disabled>
                  <Typography sx={{ color: "#7D7D7D", fontFamily: "Poppins, sans-serif" }}>
                    {isLoadingTemplates ? "Loading templates..." : "Select a template"}
                  </Typography>
                </MenuItem>
                {availableTemplates.map((template) => (
                  <MenuItem 
                    key={template} 
                    value={template}
                    sx={{
                      fontFamily: "Poppins, sans-serif",
                      fontSize: "14px",
                    }}
                  >
                    {template}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>

          {/* Recipient Name and Rider Name - Side by side */}
          <Box sx={{ display: "flex", gap: 2, mb: 4 }}>
            <Box sx={{ flex: 1 }}>
              <Typography
                sx={{
                  fontFamily: "Poppins, sans-serif",
                  fontWeight: 400,
                  fontSize: "14px",
                  lineHeight: "100%",
                  color: "#1E1E1E",
                  mb: 1.5,
                }}
              >
                Recipient Name
              </Typography>
              <TextField
                fullWidth
                required
                value={recipientName}
                onChange={(e) => setRecipientName(e.target.value)}
                placeholder="Enter recipient name"
                variant="outlined"
                sx={{
                  "& .MuiOutlinedInput-root": {
                    backgroundColor: "#fff",
                    borderRadius: "15px",
                    boxShadow: "0px 4px 20px 0px #0000000D",
                    "& fieldset": {
                      border: "none",
                    },
                    "& .MuiInputBase-input": {
                      fontFamily: "Poppins, sans-serif",
                      fontWeight: 400,
                      fontSize: "14px",
                      lineHeight: "100%",
                      color: "#1E1E1E",
                      "&::placeholder": {
                        color: "#7D7D7D",
                        opacity: 1,
                      },
                    },
                  },
                }}
              />
            </Box>

            <Box sx={{ flex: 1 }}>
              <Typography
                sx={{
                  fontFamily: "Poppins, sans-serif",
                  fontWeight: 400,
                  fontSize: "14px",
                  lineHeight: "100%",
                  color: "#1E1E1E",
                  mb: 1.5,
                }}
              >
                Rider Name
              </Typography>
              <TextField
                fullWidth
                required
                value={riderName}
                onChange={(e) => setRiderName(e.target.value)}
                placeholder="Enter rider name"
                variant="outlined"
                sx={{
                  "& .MuiOutlinedInput-root": {
                    backgroundColor: "#fff",
                    borderRadius: "15px",
                    boxShadow: "0px 4px 20px 0px #0000000D",
                    "& fieldset": {
                      border: "none",
                    },
                    "& .MuiInputBase-input": {
                      fontFamily: "Poppins, sans-serif",
                      fontWeight: 400,
                      fontSize: "14px",
                      lineHeight: "100%",
                      color: "#1E1E1E",
                      "&::placeholder": {
                        color: "#7D7D7D",
                        opacity: 1,
                      },
                    },
                  },
                }}
              />
            </Box>
          </Box>

          {/* Ride ID and Tenant ID - Side by side */}
          <Box sx={{ display: "flex", gap: 2, mb: 4 }}>
            <Box sx={{ flex: 1 }}>
              <Typography
                sx={{
                  fontFamily: "Poppins, sans-serif",
                  fontWeight: 400,
                  fontSize: "14px",
                  lineHeight: "100%",
                  color: "#1E1E1E",
                  mb: 1.5,
                }}
              >
                Ride ID
              </Typography>
              <TextField
                fullWidth
                required
                value={rideId}
                onChange={(e) => setRideId(e.target.value)}
                placeholder="Enter ride id"
                variant="outlined"
                sx={{
                  "& .MuiOutlinedInput-root": {
                    backgroundColor: "#fff",
                    borderRadius: "15px",
                    boxShadow: "0px 4px 20px 0px #0000000D",
                    "& fieldset": {
                      border: "none",
                    },
                    "& .MuiInputBase-input": {
                      fontFamily: "Poppins, sans-serif",
                      fontWeight: 400,
                      fontSize: "14px",
                      lineHeight: "100%",
                      color: "#1E1E1E",
                      "&::placeholder": {
                        color: "#7D7D7D",
                        opacity: 1,
                      },
                    },
                  },
                }}
              />
            </Box>

            <Box sx={{ flex: 1 }}>
              <Typography
                sx={{
                  fontFamily: "Poppins, sans-serif",
                  fontWeight: 400,
                  fontSize: "14px",
                  lineHeight: "100%",
                  color: "#1E1E1E",
                  mb: 1.5,
                }}
              >
                Tenant ID
              </Typography>
              <TextField
                fullWidth
                required
                value={tenantId}
                onChange={(e) => setTenantId(e.target.value)}
                placeholder="Enter tenant id"
                variant="outlined"
                sx={{
                  "& .MuiOutlinedInput-root": {
                    backgroundColor: "#fff",
                    borderRadius: "15px",
                    boxShadow: "0px 4px 20px 0px #0000000D",
                    "& fieldset": {
                      border: "none",
                    },
                    "& .MuiInputBase-input": {
                      fontFamily: "Poppins, sans-serif",
                      fontWeight: 400,
                      fontSize: "14px",
                      lineHeight: "100%",
                      color: "#1E1E1E",
                      "&::placeholder": {
                        color: "#7D7D7D",
                        opacity: 1,
                      },
                    },
                  },
                }}
              />
            </Box>
          </Box>

          {/* Recipient Biodata */}
          <Box sx={{ mb: 4 }}>
            <Typography
              sx={{
                fontFamily: "Poppins, sans-serif",
                fontWeight: 400,
                fontSize: "14px",
                lineHeight: "100%",
                color: "#1E1E1E",
                mb: 1.5,
              }}
            >
              Recipient Biodata
            </Typography>
            <Typography
              sx={{
                fontFamily: "Poppins, sans-serif",
                fontWeight: 400,
                fontSize: "12px",
                lineHeight: "16px",
                color: "#7D7D7D",
                mb: 2,
              }}
            >
              Describe the recipient that will receive this survey. Our AI will automatically select the relevant questions from the template to create the perfect survey for them
            </Typography>
            <TextField
              fullWidth
              multiline
              rows={4}
              value={recipientBiodata}
              onChange={(e) => setRecipientBiodata(e.target.value)}
              placeholder="Enter recipient data"
              variant="outlined"
              sx={{
                "& .MuiOutlinedInput-root": {
                  backgroundColor: "#fff",
                  borderRadius: "15px",
                  boxShadow: "0px 4px 20px 0px #0000000D",
                  "& fieldset": {
                    border: "none",
                  },
                  "& .MuiInputBase-input": {
                    fontFamily: "Poppins, sans-serif",
                    fontWeight: 400,
                    fontSize: "14px",
                    lineHeight: "140%",
                    color: "#1E1E1E",
                    "&::placeholder": {
                      color: "#7D7D7D",
                      opacity: 1,
                    },
                  },
                },
              }}
            />
          </Box>

          {/* Footer Buttons */}
          <Box sx={{ display: "flex", justifyContent: "flex-end", gap: 2, pt: 3 }}>
            <Button
              variant="outlined"
              onClick={handleBack}
              disabled={isGenerating}
              sx={{
                textTransform: "none",
                color: "#1E1E1E",
                width: "134px",
                height: "48px",
                borderColor: "#F0F0F0",
                borderRadius: "17px",
                fontFamily: "Poppins, sans-serif",
                fontWeight: 400,
                fontSize: "14px",
                "&:hover": {
                  borderColor: "#E0E0E0",
                  backgroundColor: "#F5F5F5",
                },
              }}
            >
              Back
            </Button>

            <Button
              variant="contained"
              onClick={handleGenerateClick}
              disabled={isGenerating}
              sx={{
                textTransform: "none",
                color: "#fff",
                width: "134px",
                height: "48px",
                backgroundColor: isGenerating ? "#ccc" : "#1958F7",
                borderRadius: "17px",
                fontFamily: "Poppins, sans-serif",
                fontWeight: 400,
                fontSize: "14px",
                "&:hover": {
                  backgroundColor: isGenerating ? "#ccc" : "#1443D1",
                },
                "&:disabled": {
                  backgroundColor: "#ccc",
                },
              }}
            >
              {isGenerating ? "Generating..." : "Generate"}
            </Button>
          </Box>
        </Box>
      </Box>

      {/* Alert Snackbar */}
      <Snackbar
        open={alert.open}
        autoHideDuration={4000}
        onClose={closeAlert}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert 
          onClose={closeAlert}
          severity={alert.severity}
          sx={{ width: '100%' }}
        >
          {alert.message}
        </Alert>
      </Snackbar>
    </>
  );
};

export default CreateSurveyForm;