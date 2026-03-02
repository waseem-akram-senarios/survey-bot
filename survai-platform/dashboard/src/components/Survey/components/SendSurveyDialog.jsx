import { ContentCopy } from "@mui/icons-material";
import {
  Box,
  Button,
  Dialog,
  DialogContent,
  IconButton,
  TextField,
  Typography,
  useMediaQuery,
} from "@mui/material";
import React, { useState } from "react";
import AddIcon from '../../../assets/Add.svg';
import EmailIcon from '../../../assets/Email.svg';
import PhoneIcon from "../../../assets/Phone.svg";
import SendIcon from '../../../assets/Send.svg';

const SendSurveyDialog = ({
  open,
  onClose,
  onConfirmEmail,
  onConfirmPhone,
  surveyId,
  isSendingEmail,
  isSendingPhone,
  surveyStatus,
}) => {
  const isCompleted = surveyStatus?.toLowerCase() === "completed";
  const isMobile = useMediaQuery("(max-width: 600px)");
  const [currentState, setCurrentState] = useState("default"); // "default", "email", "phone"
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [emailError, setEmailError] = useState("");
  const [phoneError, setPhoneError] = useState("");
  const [voiceProvider, setVoiceProvider] = useState("livekit");

  const surveyLink = `${import.meta.env.VITE_RECIPIENT_URL}/survey/${surveyId}`;

  const [emailTouched, setEmailTouched] = useState(false);
  const [phoneTouched, setPhoneTouched] = useState(false);

  const validateEmail = (value) => {
    if (!value.trim()) return "Email is required";
    const emailRegex = /^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$/;
    if (!emailRegex.test(value)) return "Please enter a valid email (e.g. name@example.com)";
    return "";
  };

  const validatePhone = (value) => {
    if (!value.trim()) return "Phone number is required";
    if (!value.startsWith('+')) return "Phone number must start with + and country code (e.g. +1 for US)";
    const digits = value.replace(/[^\d]/g, '');
    if (digits.length < 10) return "Phone number must have at least 10 digits (including country code)";
    if (digits.length > 15) return "Phone number cannot exceed 15 digits";
    if (!/^\+[\d\s\-()]+$/.test(value)) return "Only digits, +, spaces, hyphens and parentheses allowed";
    return "";
  };

  const handleEmailChange = (e) => {
    const value = e.target.value;
    setEmail(value);
    if (emailTouched) {
      setEmailError(validateEmail(value));
    }
  };

  const handleEmailBlur = () => {
    setEmailTouched(true);
    if (email.trim()) {
      setEmailError(validateEmail(email));
    }
  };

  const formatPhoneForApi = (value) => value.replace(/[\s\-()]/g, '');

  const handlePhoneChange = (e) => {
    const value = e.target.value.replace(/[^\d\s\-+()]/g, '');
    setPhone(value);
    if (phoneTouched) {
      setPhoneError(validatePhone(value));
    }
  };

  const handlePhoneBlur = () => {
    setPhoneTouched(true);
    if (phone.trim()) {
      setPhoneError(validatePhone(phone));
    }
  };

  const handleSendViaEmail = () => {
    setCurrentState("email");
  };

  const handleSendViaPhone = () => {
    setCurrentState("phone");
  };

  const handleEmailSend = () => {
    setEmailTouched(true);
    const error = validateEmail(email);
    setEmailError(error);
    if (error) return;
    onConfirmEmail(email.trim());
  };

  const handlePhoneSend = () => {
    setPhoneTouched(true);
    const error = validatePhone(phone);
    setPhoneError(error);
    if (error) return;
    const cleanNumber = formatPhoneForApi(phone.trim());
    onConfirmPhone(cleanNumber, voiceProvider);
  };

  const [copied, setCopied] = useState(false);

  const handleCopyLink = async () => {
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(surveyLink);
        setCopied(true);
      } else {
        const textArea = document.createElement("textarea");
        textArea.value = surveyLink;
        textArea.style.position = "fixed";
        textArea.style.left = "-9999px";
        textArea.style.top = "-9999px";
        textArea.style.opacity = "0";
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        textArea.setSelectionRange(0, textArea.value.length);
        const success = document.execCommand("copy");
        document.body.removeChild(textArea);
        if (success) {
          setCopied(true);
        } else {
          window.prompt("Copy this link:", surveyLink);
          setCopied(true);
        }
      }
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      window.prompt("Copy this link:", surveyLink);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleClose = () => {
    if (!isSendingEmail && !isSendingPhone) {
      setCurrentState("default");
      setEmail("");
      setPhone("");
      setEmailError("");
      setPhoneError("");
      setEmailTouched(false);
      setPhoneTouched(false);
      setVoiceProvider("livekit");
      onClose();
    }
  };

  const isLoading = isSendingEmail || isSendingPhone;
  const loadingText = isSendingEmail ? "Sending..." : isSendingPhone ? "Sending..." : "Send Survey";

  return (
    <Dialog
      open={open}
      onClose={!isLoading ? handleClose : undefined}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: "20px",
          width: isMobile ? "90%" : "500px",
          maxWidth: isMobile ? "90%" : "500px",
          m: 2,
        },
      }}
    >
      <DialogContent sx={{ p: isMobile ? 3 : 4, position: "relative" }}>
        <Box sx={{ pt: 2 }}>
          {/* Header */}
          <Box sx={{ display: "flex", alignItems: "center", mb: 3 }}>
            <img src={SendIcon} alt="Send Icon" style={{ marginRight: '10px'}} />
            <Typography
              sx={{
                fontFamily: "Poppins, sans-serif",
                fontWeight: 500,
                fontSize: "20px",
                lineHeight: "100%",
                color: "#1E1E1E",
              }}
            >
              Send Survey
            </Typography>
          </Box>

          {/* Completed Survey Warning */}
          {isCompleted && (
            <Box
              sx={{
                mb: 3,
                p: 2,
                backgroundColor: "#FFF3E0",
                borderRadius: "12px",
                border: "1px solid #FF9800",
              }}
            >
              <Typography sx={{ fontFamily: "Poppins, sans-serif", fontSize: "13px", color: "#E65100", fontWeight: 500, mb: 0.5 }}>
                Survey Already Completed
              </Typography>
              <Typography sx={{ fontFamily: "Poppins, sans-serif", fontSize: "12px", color: "#BF360C" }}>
                This survey was already completed on the dashboard. Sending the link via email will show the recipient that it's already done. To collect new responses, please create a new survey.
              </Typography>
            </Box>
          )}

          {/* Copy Link Section */}
          <Box sx={{ mb: 4 }}>
            <Typography
              sx={{
                fontFamily: "Poppins, sans-serif",
                fontWeight: 500,
                fontSize: "16px",
                color: "#1E1E1E",
                mb: 2,
              }}
            >
              Copy link
            </Typography>
            <Box
              sx={{
                display: "flex",
                alignItems: "center",
                backgroundColor: "#F8F9FA",
                borderRadius: "12px",
                p: 2,
                border: "1px solid #E9ECEF",
              }}
            >
              <Typography
                sx={{
                  fontFamily: "Poppins, sans-serif",
                  fontWeight: 400,
                  fontSize: "14px",
                  color: "#1958F7",
                  flex: 1,
                  wordBreak: "break-all",
                }}
              >
                {surveyLink}
              </Typography>
              <IconButton
                onClick={handleCopyLink}
                sx={{ ml: 1, color: copied ? "#4CAF50" : "#666" }}
                title={copied ? "Copied!" : "Copy link"}
              >
                {copied ? (
                  <Typography sx={{ fontSize: "12px", fontFamily: "Poppins, sans-serif", color: "#4CAF50", fontWeight: 500 }}>
                    Copied!
                  </Typography>
                ) : (
                  <ContentCopy />
                )}
              </IconButton>
            </Box>
          </Box>

          {/* Dynamic Content Based on State */}
          {currentState === "email" && (
            <Box sx={{ mb: 4 }}>
              <Typography
                sx={{
                  fontFamily: "Poppins, sans-serif",
                  fontWeight: 500,
                  fontSize: "16px",
                  color: "#1E1E1E",
                  mb: 2,
                }}
              >
                Enter Email
              </Typography>
              <Box
                sx={{
                  mb: 2,
                  p: 1.5,
                  backgroundColor: "#FFF8E7",
                  borderRadius: "10px",
                  border: "1px solid #FFD700",
                }}
              >
                <Typography sx={{ fontFamily: "Poppins, sans-serif", fontSize: "12px", color: "#7A5C00" }}>
                  <strong>Note:</strong> If no email arrives, check your spam folder. Free-tier email providers may only deliver to verified addresses. Contact your admin to set up a custom sender domain.
                </Typography>
              </Box>
              <Box sx={{ display: "flex", alignItems: "center" }}>
                <img src={EmailIcon} alt="Email-Icon" style={{ marginRight: '7.5px' }} />
                <TextField
                  fullWidth
                  placeholder="name@example.com"
                  type="email"
                  value={email}
                  onChange={handleEmailChange}
                  onBlur={handleEmailBlur}
                  error={!!emailError}
                  helperText={emailError || (emailTouched && email && !validateEmail(email) ? "" : "e.g. john@company.com")}
                  disabled={isLoading}
                  color={emailTouched && email && !emailError ? "success" : undefined}
                  sx={{
                    "& .MuiOutlinedInput-root": {
                      borderRadius: "12px",
                      fontFamily: "Poppins, sans-serif",
                      fontSize: "14px",
                    },
                    "& .MuiFormHelperText-root": {
                      fontFamily: "Poppins, sans-serif",
                      fontSize: "12px",
                    },
                  }}
                />
              </Box>
            </Box>
          )}

          {currentState === "phone" && (
            <Box sx={{ mb: 4 }}>
              <Typography
                sx={{
                  fontFamily: "Poppins, sans-serif",
                  fontWeight: 500,
                  fontSize: "16px",
                  color: "#1E1E1E",
                  mb: 2,
                }}
              >
                Enter Phone Number
              </Typography>
              <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
                <img src={PhoneIcon} alt="Phone-Icon" style={{ marginRight: '7.5px' }} />
                <TextField
                  fullWidth
                  placeholder="+12345678901"
                  type="tel"
                  value={phone}
                  onChange={handlePhoneChange}
                  onBlur={handlePhoneBlur}
                  error={!!phoneError}
                  helperText={phoneError || "Format: +[country code][number] e.g. +12345678901"}
                  disabled={isLoading}
                  color={phoneTouched && phone && !phoneError ? "success" : undefined}
                  inputProps={{ maxLength: 20 }}
                  sx={{
                    "& .MuiOutlinedInput-root": {
                      borderRadius: "12px",
                      fontFamily: "Poppins, sans-serif",
                      fontSize: "14px",
                    },
                    "& .MuiFormHelperText-root": {
                      fontFamily: "Poppins, sans-serif",
                      fontSize: "12px",
                    },
                  }}
                />
              </Box>
              {phone && !phoneError && (
                <Typography sx={{ fontFamily: "Poppins, sans-serif", fontSize: "12px", color: "#4CAF50", ml: 4.5 }}>
                  Will call: {formatPhoneForApi(phone.trim())}
                </Typography>
              )}
              
            </Box>
          )}

          {/* Action Buttons - Always Visible */}
          <Box sx={{ mb: 4 }}>
            <Box sx={{ display: "flex", gap: 2, mb: 2 }}>
              <Button
                variant="outlined"
                startIcon={<img src={AddIcon} alt="Email" />}
                onClick={handleSendViaEmail}
                disabled={isLoading}
                sx={{
                  flex: 1,
                  textTransform: "none",
                  fontSize: "14px",
                  fontFamily: "Poppins, sans-serif",
                  fontWeight: 400,
                  border: 'none',
                  backgroundColor: currentState === "email" ? "#f0f0f0f" : "#f9f9f9",
                  color: "#4B4B4B",
                  borderRadius: "12px",
                  height: "48px",
                }}
              >
                Send via Email
              </Button>
              <Button
                variant="outlined"
                startIcon={<img src={AddIcon} alt="Phone" />}
                onClick={handleSendViaPhone}
                disabled={isLoading}
                sx={{
                  flex: 1,
                  textTransform: "none",
                  fontSize: "14px",
                  fontFamily: "Poppins, sans-serif",
                  fontWeight: 400,
                  border: 'none',
                  backgroundColor: currentState === "phone" ? "#f0f0f0f" : "#f9f9f9",
                  color: "#4B4B4B",
                  borderRadius: "12px",
                  height: "48px",
                }}
              >
                Send via Phone
              </Button>
            </Box>
            <Typography
              sx={{
                fontFamily: "Poppins, sans-serif",
                fontWeight: 400,
                fontSize: "12px",
                color: "#999",
                textAlign: "center",
              }}
            >
              Choose only one
            </Typography>
          </Box>

          {/* Bottom Action Buttons */}
          <Box sx={{ display: "flex", gap: 2, justifyContent: "flex-end" }}>
            <Button
              variant="outlined"
              onClick={handleClose}
              disabled={isLoading}
              sx={{
                textTransform: "none",
                color: "#1E1E1E",
                width: "120px",
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
              Cancel
            </Button>
            {currentState !== "default" && (
              <Button
                variant="contained"
                onClick={currentState === "email" ? handleEmailSend : handlePhoneSend}
                disabled={isLoading || (currentState === "email" ? (!email.trim() || !!validateEmail(email)) : (!phone.trim() || !!validatePhone(phone)))}
                sx={{
                  textTransform: "none",
                  color: "#fff",
                  width: "140px",
                  height: "48px",
                  backgroundColor: "#1958F7",
                  borderRadius: "17px",
                  fontFamily: "Poppins, sans-serif",
                  fontWeight: 400,
                  fontSize: "14px",
                  "&:hover": {
                    backgroundColor: "#1958F7",
                  },
                  "&:disabled": {
                    backgroundColor: "#ccc",
                  },
                }}
              >
                {loadingText}
              </Button>
            )}
          </Box>
        </Box>
      </DialogContent>
    </Dialog>
  );
};

export default SendSurveyDialog;