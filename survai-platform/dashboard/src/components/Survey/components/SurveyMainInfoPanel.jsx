import { Box, Typography, Button, useMediaQuery, Chip } from "@mui/material";
import SurveyInfoField from "./SurveyInfoField";
import { getStatusStyle } from "../../../utils/Surveys/surveyHelpers";

const SurveyMainInfoPanel = ({ 
  surveyInfo, 
  isCompleted, 
  isDeleting, 
  onBack, 
  onDeleteSurvey,
  onSendSurvey
}) => {
  const isMobile = useMediaQuery("(max-width: 600px)");

  return (
    <Box
      sx={{
        width: isMobile ? "100%" : "30%",
        backgroundColor: "#fff",
        borderRadius: "20px",
        p: isMobile ? 2 : 4,
        boxShadow: "0px 4px 20px 0px #0000000D",
        overflowY: "auto",
        maxHeight: "100%",
      }}
    >
      <Typography
        sx={{
          fontFamily: "Poppins, sans-serif",
          fontWeight: 500,
          fontSize: "18px",
          lineHeight: "100%",
          color: "#1E1E1E",
          mb: 3,
        }}
      >
        Main Information
      </Typography>

      {/* Survey ID */}
      <SurveyInfoField
        label="Survey ID"
        value={surveyInfo.surveyId}
      />

      {/* Template Name */}
      <SurveyInfoField
        label="Template Name"
        value={surveyInfo.templateName}
      />

      {/* Status with custom styling */}
      <Box
        sx={{
          mb: 2,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <Box sx={{ display: "flex", alignItems: "center" }}>
          <Typography
            sx={{
              fontFamily: "Poppins, sans-serif",
              fontSize: "14px",
              color: "#9E9E9E",
              mr: 1,
            }}
          >
            📋
          </Typography>
          <Typography
            sx={{
              fontFamily: "Poppins, sans-serif",
              fontSize: "14px",
              color: "#9E9E9E",
            }}
          >
            Status
          </Typography>
        </Box>
        <Chip
          label={surveyInfo.status}
          sx={{
            ...getStatusStyle(surveyInfo.status),
            fontFamily: "Poppins, sans-serif",
            fontSize: "12px",
            fontWeight: 500,
            height: "28px",
            borderRadius: "8px",
            '& .MuiChip-label': {
              padding: '0 8px',
            },
          }}
        />
      </Box>

      {/* Recipient Name */}
      <SurveyInfoField
        label="Recipient Name"
        value={surveyInfo.recipientName}
      />

      {/* Survey URL */}
      <SurveyInfoField
        icon="🔗"
        label="Survey Url"
        value={surveyInfo.surveyUrl}
        isLink={true}
        onClick={() => window.open(surveyInfo.surveyUrl, "_blank")}
      />

      {/* Recipient Biodata */}
      <Box sx={{ mb: 3 }}>
        <Typography
          sx={{
            fontFamily: "Poppins, sans-serif",
            fontWeight: 500,
            fontSize: "14px",
            lineHeight: "100%",
            color: "#1E1E1E",
            mb: 1,
          }}
        >
          Recipient Biodata
        </Typography>
        <Box
          sx={{
            p: 2,
            backgroundColor: "#F8F9FA",
            borderRadius: "10px",
            border: "1px solid #E9ECEF",
          }}
        >
          <Typography
            sx={{
              fontFamily: "Poppins, sans-serif",
              fontWeight: 400,
              fontSize: "12px",
              lineHeight: "140%",
              color: "#6C757D",
            }}
          >
            {surveyInfo.recipientBiodata}
          </Typography>
        </Box>
      </Box>

      {/* Timeline */}
      <Box sx={{ mb: 4 }}>
        <Typography
          sx={{
            fontFamily: "Poppins, sans-serif",
            fontWeight: 500,
            fontSize: "14px",
            lineHeight: "100%",
            color: "#1E1E1E",
            mb: 2,
          }}
        >
          Timeline
        </Typography>

        {/* Creation Date */}
        <SurveyInfoField
          label="Creation Date"
          value={surveyInfo.launchDate || "Not available"}
        />

        {/* Completion Date */}
        <SurveyInfoField
          label="Completion Date"
          value={surveyInfo.completionDate || "-"}
        />
      </Box>

      {/* Send Survey Button */}
      {!isCompleted && <Box sx={{ mb: 1 }}>
        <Button
          variant="outlined"
          onClick={() => onSendSurvey && onSendSurvey(surveyInfo)}
          fullWidth
          sx={{
            textTransform: "none",
            fontFamily: "Poppins",
            fontWeight: 400,
            fontSize: "14px",
            textAlign: "center",
            color: "#1958F7",
            backgroundColor: "#EFEFFD",
            border: "1px solid #F0F0F0",
            borderRadius: "15px",
            pt: "13px",
            pr: "16px",
            pb: "13px",
            pl: "16px",
            height: "45px",
            "&:hover": {
              backgroundColor: "#EFEFFD",
              borderColor: "#F0F0F0",
            },
          }}
        >
          Send Survey
        </Button>
      </Box>}

      {/* Bottom Buttons */}
      <Box
        sx={{ 
          display: "flex", 
          justifyContent: isCompleted ? "stretch" : "space-between", 
          gap: 2 
        }}
      >
        <Button
          variant="outlined"
          onClick={onBack}
          disabled={isDeleting}
          sx={{
            textTransform: "none",
            color: "#1E1E1E",
            flex: 1,
            height: "40px",
            borderColor: "#F0F0F0",
            borderRadius: "15px",
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

        {/* Only show delete button if not completed */}
        {!isCompleted && (
          <Button
            variant="outlined"
            onClick={onDeleteSurvey}
            disabled={isDeleting}
            sx={{
              textTransform: "none",
              color: "#000",
              flex: 1,
              height: "40px",
              borderColor: "#F0F0F0",
              borderRadius: "15px",
              fontFamily: "Poppins, sans-serif",
              fontWeight: 400,
              fontSize: "14px",
              "&:hover": {},
            }}
          >
            {isDeleting ? "Deleting..." : "Delete Survey"}
          </Button>
        )}
      </Box>
    </Box>
  );
};

export default SurveyMainInfoPanel;