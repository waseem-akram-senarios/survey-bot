import React from "react";
import { Box, Typography } from "@mui/material";

const ConversationItem = ({ item, index }) => {
  return (
    <Box
      sx={{
        mt: index === 0 ? 0 : 3,
        mb: 3,
        border: "none",
        borderRadius: 2,
        pb: 2,
        animation: "fadeIn 0.5s ease-in",
        "@keyframes fadeIn": {
          from: { opacity: 0, transform: "translateY(10px)" },
          to: { opacity: 1, transform: "translateY(0)" },
        },
      }}
    >
      {item.type === 'question' && (
        <Typography
          sx={{
            fontFamily: "Poppins, sans-serif",
            fontWeight: 400,
            fontSize: { xs: "14px", sm: "16px" },
            lineHeight: "100%",
            color: "#4B4B4B",
            mb: 2,
          }}
        >
          <span style={{ marginRight: "10px", fontWeight: 500 }}>
            Question {item.questionNumber}:
          </span>
          {item.text}
        </Typography>
      )}
      
      {item.type === 'user_answer' && (
        <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
          <Box
            sx={{
              backgroundColor: "#1958F7",
              color: "white",
              borderRadius: "15px 15px 5px 15px",
              padding: "12px 16px",
              maxWidth: "70%",
              wordBreak: "break-word"
            }}
          >
            <Typography
              sx={{
                fontFamily: "Poppins, sans-serif",
                fontWeight: 400,
                fontSize: { xs: "14px", sm: "16px" },
              }}
            >
              {item.text}
            </Typography>
          </Box>
        </Box>
      )}
      
      {item.type === 'sympathy_response' && (
        <Box sx={{ display: 'flex', justifyContent: 'flex-start', mb: 2 }}>
          <Box
            sx={{
              backgroundColor: "#f4f4f4",
              color: "#4B4B4B",
              borderRadius: "15px 15px 15px 5px",
              padding: "12px 16px",
              maxWidth: "70%",
              wordBreak: "break-word"
            }}
          >
            <Typography
              sx={{
                fontFamily: "Poppins, sans-serif",
                fontWeight: 400,
                fontSize: { xs: "14px", sm: "16px" },
              }}
            >
              {item.text}
            </Typography>
          </Box>
        </Box>
      )}
      
      {(item.type === 'completion' || item.type === 'message') && (
        <Typography
          sx={{
            fontFamily: "Poppins, sans-serif",
            fontWeight: 400,
            fontSize: { xs: "14px", sm: "16px" },
            lineHeight: "100%",
            color: "#4B4B4B",
            textAlign: "center",
            fontStyle: "italic",
            mb: 2,
          }}
        >
          {item.text}
        </Typography>
      )}
    </Box>
  );
};

export default ConversationItem;