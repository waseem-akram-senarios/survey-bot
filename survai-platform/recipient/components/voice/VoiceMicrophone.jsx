import React from "react";
import { Box, Typography, CircularProgress, IconButton } from "@mui/material";
import Image from "next/image";

const VoiceMicrophone = ({
  isRecording,
  isProcessing,
  isGettingSympathize,
  isLoading,
  surveyData,
  surveyCompleted,
  onStartRecording,
  onStopRecording,
  isSpeaking,
}) => {
  const isDisabled = isProcessing || isLoading || !surveyData || isGettingSympathize || surveyCompleted || isSpeaking;
  const showSpinner = isProcessing || isGettingSympathize;

  const handleClick = () => {
    if (isDisabled) return;
    if (isRecording) {
      onStopRecording();
    } else {
      onStartRecording();
    }
  };

  return (
    <Box
      sx={{
        position: "fixed",
        bottom: "100px",
        left: "50%",
        transform: "translateX(-50%)",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        zIndex: 1000,
      }}
    >
      <IconButton
        onClick={handleClick}
        onContextMenu={(e) => e.preventDefault()}
        disabled={isDisabled}
        sx={{
          width: { xs: "120px", sm: "140px", md: "160px" },
          height: { xs: "120px", sm: "140px", md: "160px" },
          borderRadius: "50%",
          backgroundColor: isRecording
            ? "rgba(244, 67, 54, 0.1)"
            : isGettingSympathize
            ? "#E0E0E0"
            : "transparent",
          transition: "all 0.3s ease",
          userSelect: "none",
          WebkitUserSelect: "none",
          WebkitTouchCallout: "none",
          WebkitTapHighlightColor: "transparent",
          border: isRecording ? "3px solid #F44336" : "3px solid transparent",
          "&:hover": {
            backgroundColor: isRecording
              ? "rgba(244, 67, 54, 0.15)"
              : isGettingSympathize
              ? "#E0E0E0"
              : "rgba(25, 88, 247, 0.1)",
          },
          "&:disabled": {
            opacity: 0.6,
            pointerEvents: "none",
          },
        }}
      >
        {showSpinner ? (
          <CircularProgress size={40} color="inherit" />
        ) : isRecording ? (
          <Box
            sx={{
              width: 40,
              height: 40,
              borderRadius: "8px",
              backgroundColor: "#F44336",
              animation: "pulse-record 1.5s infinite",
              "@keyframes pulse-record": {
                "0%": { transform: "scale(1)", opacity: 1 },
                "50%": { transform: "scale(1.1)", opacity: 0.8 },
                "100%": { transform: "scale(1)", opacity: 1 },
              },
            }}
          />
        ) : (
          <Image
            src="/Mic.svg"
            alt="Mic"
            width={80}
            height={80}
            style={{
              transition: "filter 0.2s ease",
              cursor: "pointer",
            }}
          />
        )}
      </IconButton>

      {/* Status text */}
      <Typography
        sx={{
          mt: 2,
          fontFamily: "Poppins, sans-serif",
          fontSize: "14px",
          color: isRecording ? "#F44336" : "#666",
          textAlign: "center",
          minHeight: "21px",
          animation: isRecording || showSpinner || isSpeaking ? "pulse 1.5s infinite" : "none",
          "@keyframes pulse": {
            "0%": { opacity: 0.6 },
            "50%": { opacity: 1 },
            "100%": { opacity: 0.6 },
          },
        }}
      >
        {isRecording && "Listening... Tap to stop"}
        {isProcessing && "Processing your response..."}
        {isGettingSympathize && "Thinking..."}
        {isSpeaking && !isRecording && !isProcessing && !isGettingSympathize && "Please wait..."}
        {!isRecording && !isProcessing && !isGettingSympathize && !isSpeaking && "Tap microphone to speak"}
      </Typography>
    </Box>
  );
};

export default VoiceMicrophone;
