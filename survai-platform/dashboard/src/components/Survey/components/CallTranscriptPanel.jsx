import { useState, useEffect } from "react";
import {
  Box,
  Typography,
  Paper,
  CircularProgress,
  Chip,
  IconButton,
  Collapse,
} from "@mui/material";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import ExpandLessIcon from "@mui/icons-material/ExpandLess";
import PhoneIcon from "@mui/icons-material/Phone";
import AccessTimeIcon from "@mui/icons-material/AccessTime";
import GraphicEqIcon from "@mui/icons-material/GraphicEq";
import SurveyService from "../../../services/Surveys/surveyService";

const CallTranscriptPanel = ({ surveyId }) => {
  const [transcript, setTranscript] = useState(null);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(true);

  useEffect(() => {
    if (!surveyId) return;
    let cancelled = false;
    (async () => {
      setLoading(true);
      const data = await SurveyService.fetchTranscript(surveyId);
      if (!cancelled) {
        setTranscript(data);
        setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [surveyId]);

  if (loading) {
    return (
      <Paper sx={{ p: 2, mb: 2, borderRadius: 2 }}>
        <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
          <CircularProgress size={18} />
          <Typography variant="body2" color="text.secondary">Loading call data...</Typography>
        </Box>
      </Paper>
    );
  }

  if (!transcript) return null;

  const durationMin = Math.floor((transcript.call_duration_seconds || 0) / 60);
  const durationSec = (transcript.call_duration_seconds || 0) % 60;
  const lines = (transcript.full_transcript || "").split("\n").filter(Boolean);

  const answersIdx = lines.findIndex((l) => l.includes("--- RECORDED ANSWERS ---"));
  const conversationLines = answersIdx >= 0 ? lines.slice(0, answersIdx) : lines;

  const statusColor =
    transcript.call_status === "completed" ? "success" :
    transcript.call_status === "disconnected" ? "warning" : "default";

  return (
    <Paper
      elevation={0}
      sx={{
        mb: 2,
        borderRadius: 2,
        border: "1px solid #e0e0e0",
        overflow: "hidden",
      }}
    >
      {/* Header */}
      <Box
        onClick={() => setExpanded((v) => !v)}
        sx={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          px: 2.5,
          py: 1.5,
          cursor: "pointer",
          bgcolor: "#f8f9fc",
          "&:hover": { bgcolor: "#f0f2f8" },
        }}
      >
        <Box sx={{ display: "flex", alignItems: "center", gap: 1.5 }}>
          <PhoneIcon sx={{ fontSize: 20, color: "#1958F7" }} />
          <Typography sx={{ fontWeight: 600, fontSize: 15, fontFamily: "Poppins" }}>
            Call Transcript
          </Typography>
          <Chip
            label={transcript.call_status || "unknown"}
            size="small"
            color={statusColor}
            sx={{ fontSize: 11, height: 22, textTransform: "capitalize" }}
          />
          <Box sx={{ display: "flex", alignItems: "center", gap: 0.5, ml: 1 }}>
            <AccessTimeIcon sx={{ fontSize: 14, color: "#888" }} />
            <Typography variant="caption" color="text.secondary">
              {durationMin}m {durationSec}s
            </Typography>
          </Box>
        </Box>
        <IconButton size="small">
          {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
        </IconButton>
      </Box>

      <Collapse in={expanded}>
        {/* Audio Player */}
        {transcript.audio_url && (
          <Box sx={{ px: 2.5, pt: 2, pb: 1 }}>
            <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1 }}>
              <GraphicEqIcon sx={{ fontSize: 18, color: "#1958F7" }} />
              <Typography sx={{ fontSize: 13, fontWeight: 600, fontFamily: "Poppins" }}>
                Call Recording
              </Typography>
            </Box>
            <audio
              controls
              preload="metadata"
              style={{ width: "100%", borderRadius: 8 }}
              src={transcript.audio_url}
            />
          </Box>
        )}

        {/* Conversation */}
        <Box
          sx={{
            px: 2.5,
            py: 2,
            maxHeight: 400,
            overflowY: "auto",
            "&::-webkit-scrollbar": { width: 5 },
            "&::-webkit-scrollbar-thumb": { bgcolor: "#ccc", borderRadius: 3 },
          }}
        >
          {conversationLines.length === 0 ? (
            <Typography variant="body2" color="text.secondary" sx={{ fontStyle: "italic" }}>
              No conversation transcript available.
            </Typography>
          ) : (
            conversationLines.map((line, i) => {
              const isAgent = line.includes("AGENT:");
              const isCaller = line.includes("CALLER:");
              const tsMatch = line.match(/^\[([^\]]+)\]\s*/);
              const displayText = tsMatch ? line.slice(tsMatch[0].length) : line;
              const roleText = isAgent ? displayText.replace(/^AGENT:\s*/, "") :
                               isCaller ? displayText.replace(/^CALLER:\s*/, "") : displayText;

              return (
                <Box
                  key={i}
                  sx={{
                    display: "flex",
                    flexDirection: "column",
                    alignItems: isAgent ? "flex-start" : isCaller ? "flex-end" : "flex-start",
                    mb: 1.2,
                  }}
                >
                  <Box
                    sx={{
                      maxWidth: "85%",
                      px: 1.8,
                      py: 1,
                      borderRadius: isAgent ? "12px 12px 12px 2px" : "12px 12px 2px 12px",
                      bgcolor: isAgent ? "#e8edf8" : isCaller ? "#dcedc8" : "#f5f5f5",
                      border: `1px solid ${isAgent ? "#c5d0e8" : isCaller ? "#c5e1a5" : "#e0e0e0"}`,
                    }}
                  >
                    <Typography
                      sx={{
                        fontSize: 11,
                        fontWeight: 700,
                        color: isAgent ? "#1958F7" : isCaller ? "#388E3C" : "#666",
                        mb: 0.3,
                        fontFamily: "Poppins",
                      }}
                    >
                      {isAgent ? "Agent" : isCaller ? "Caller" : ""}
                    </Typography>
                    <Typography sx={{ fontSize: 13, lineHeight: 1.5, color: "#333" }}>
                      {roleText}
                    </Typography>
                  </Box>
                  {tsMatch && (
                    <Typography variant="caption" sx={{ color: "#aaa", fontSize: 10, mt: 0.2, px: 0.5 }}>
                      {new Date(tsMatch[1]).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })}
                    </Typography>
                  )}
                </Box>
              );
            })
          )}
        </Box>
      </Collapse>
    </Paper>
  );
};

export default CallTranscriptPanel;
