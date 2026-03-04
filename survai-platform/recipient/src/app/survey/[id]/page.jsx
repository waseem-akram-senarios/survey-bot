"use client";
import { Box, Typography, Button, CircularProgress, Card, Avatar, Chip, ToggleButton, ToggleButtonGroup } from "@mui/material";
import { AutoAwesome, RecordVoiceOver, TextFields, Language } from "@mui/icons-material";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import Background from '../../../../public/StartBackground.svg'
import { detectLanguage, t } from '../../../lib/i18n';
import { generatePersonalizedGreeting } from '../../../lib/aiService';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

export default function Survey() {
  const router = useRouter();
  const params = useParams();
  const id = params?.id;
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [recipientName, setRecipientName] = useState("");
  const [riderName, setRiderName] = useState("");
  const [surveyName, setSurveyName] = useState("");
  const [biodata, setBiodata] = useState("");
  const [lang, setLang] = useState("en");
  const [isBilingual, setIsBilingual] = useState(true);
  const [visibleLines, setVisibleLines] = useState(0);
  const [personalizedGreeting, setPersonalizedGreeting] = useState("");

  const getGreetingLines = (name, language) => [
    language === 'es' ? `¡Hola${name ? `, ${name}` : ''}! 👋` : `Hi${name ? `, ${name}` : ''}! 👋`,
    t('greetingIntro', language),
    t('greetingTime', language) + ' 🙏',
  ];

  const fetchRecipientInfo = async () => {
    if (!id) return;
    try {
      const response = await fetch(`${API_BASE_URL}/api/surveys/${id}/recipient`, {
        method: "GET",
        headers: { accept: "application/json" },
      });
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const result = await response.json();
      setRecipientName(result.Recipient || "");
      setRiderName(result.RiderName || "");
      setSurveyName(result.Name || "");
      setBiodata(result.Biodata || "");
      const bilingual = result.Bilingual !== false;
      setIsBilingual(bilingual);
      if (result.Name) {
        const detected = detectLanguage(result.Name);
        setLang(detected);
      }

      try {
        const greeting = await generatePersonalizedGreeting(
          result.Recipient || result.RiderName,
          result.Name,
          lang,
          result.Biodata || ""
        );
        setPersonalizedGreeting(greeting);
      } catch (error) {
        console.error("Failed to generate AI greeting:", error);
      }
    } catch (error) {
      console.error("Error fetching recipient info:", error);
    }
  };

  const checkSurveyStatus = async () => {
    if (!id) return;
    try {
      const response = await fetch(`${API_BASE_URL}/api/surveys/${id}/status`, {
        method: "GET",
        headers: { accept: "application/json" },
      });
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const result = await response.json();
      if (result.Status === "Completed") {
        router.push(`/survey/${id}/complete`);
        return;
      }
      setIsLoading(false);
    } catch (error) {
      console.error("Error checking survey status:", error);
      setError(t('errorLoading', lang));
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const initializePage = async () => {
      await Promise.all([fetchRecipientInfo(), checkSurveyStatus()]);
    };
    initializePage();
  }, [id, router]);

  useEffect(() => {
    if (isLoading || error) return;
    setVisibleLines(0);
    const greetingLines = getGreetingLines(recipientName || riderName, lang);
    const timers = greetingLines.map((_, i) =>
      setTimeout(() => setVisibleLines(v => Math.max(v, i + 1)), i * 900)
    );
    return () => timers.forEach(clearTimeout);
  }, [isLoading, error, lang]);

  const handleStart = () => {
    if (id) router.push(`/survey/${id}/start?lang=${lang}`);
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh"
        sx={{ background: "linear-gradient(135deg, #EEF3FF 0%, #F8F9FF 100%)" }}>
        <Box textAlign="center">
          <CircularProgress sx={{ color: "#1958F7", mb: 2 }} />
          <Typography sx={{ fontFamily: "Poppins, sans-serif", color: "#7D7D7D", fontSize: "14px" }}>
            {t('loadingSurvey', lang)}
          </Typography>
        </Box>
      </Box>
    );
  }

  if (error) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh"
        sx={{ background: "linear-gradient(135deg, #EEF3FF 0%, #F8F9FF 100%)" }}>
        <Card sx={{ maxWidth: 420, p: 4, borderRadius: "24px", textAlign: "center" }}>
          <Typography sx={{ fontFamily: "Poppins, sans-serif", fontWeight: 600, fontSize: "20px", mb: 1 }}>
            {t('surveyNotFound', lang)}
          </Typography>
          <Typography color="text.secondary" sx={{ fontFamily: "Poppins, sans-serif", fontSize: "14px", mb: 3 }}>
            {error}
          </Typography>
          <Button onClick={() => window.location.reload()} variant="outlined"
            sx={{ borderRadius: "12px", textTransform: "none", fontFamily: "Poppins, sans-serif" }}>
            {t('retry', lang)}
          </Button>
        </Card>
      </Box>
    );
  }

  const greetingLines = getGreetingLines(recipientName || riderName, lang);

  return (
    <Box
      sx={{
        minHeight: "100vh",
        backgroundImage: `url(${Background.src})`,
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "24px",
      }}
    >
      {/* Language Selector - only shown for bilingual surveys */}
      {isBilingual && <Box sx={{ position: "absolute", top: 20, right: 20, zIndex: 10 }}>
        <ToggleButtonGroup
          value={lang}
          exclusive
          onChange={(_, newLang) => { if (newLang) setLang(newLang); }}
          size="small"
          sx={{
            backgroundColor: "rgba(255,255,255,0.9)",
            borderRadius: "12px",
            boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
            "& .MuiToggleButton-root": {
              fontFamily: "Poppins, sans-serif",
              fontSize: "12px",
              fontWeight: 500,
              textTransform: "none",
              border: "none",
              borderRadius: "12px !important",
              px: 2,
              py: 0.5,
              color: "#666",
              "&.Mui-selected": {
                backgroundColor: "#1958F7",
                color: "#fff",
                "&:hover": { backgroundColor: "#1443D1" },
              },
            },
          }}
        >
          <ToggleButton value="en">EN</ToggleButton>
          <ToggleButton value="es">ES</ToggleButton>
        </ToggleButtonGroup>
      </Box>}

      {/* Branding */}
      <Box textAlign="center" mb={4}>
        <Typography sx={{ fontFamily: "Saira, sans-serif", fontSize: "40px", fontWeight: 400, color: "#000" }}>
          SurvAI
        </Typography>
        <Chip
          icon={<AutoAwesome sx={{ fontSize: 14 }} />}
          label={t('aiPoweredSurvey', lang)}
          size="small"
          sx={{
            fontFamily: "Poppins, sans-serif",
            fontSize: "11px",
            backgroundColor: "#EEF3FF",
            color: "#1958F7",
            border: "1px solid #C5D5FF",
            mt: 0.5,
          }}
        />
      </Box>

      {/* Main Greeting Card */}
      <Card
        sx={{
          maxWidth: "520px",
          width: "100%",
          p: { xs: 3, md: 5 },
          borderRadius: "28px",
          background: "rgba(255, 255, 255, 0.85)",
          border: "1px solid #EAEAEA",
          backdropFilter: "blur(40px)",
          boxShadow: "0 8px 40px rgba(25, 88, 247, 0.08)",
        }}
      >
        {/* AI Avatar */}
        <Box display="flex" alignItems="center" gap={2} mb={3}>
          <Avatar
            sx={{
              width: 48,
              height: 48,
              background: "linear-gradient(135deg, #1958F7 0%, #6B8FF7 100%)",
              boxShadow: "0 4px 12px rgba(25, 88, 247, 0.3)",
            }}
          >
            <AutoAwesome sx={{ fontSize: 22, color: "#fff" }} />
          </Avatar>
          <Box>
            <Typography sx={{ fontFamily: "Poppins, sans-serif", fontWeight: 600, fontSize: "14px", color: "#1E1E1E" }}>
              {t('survaiAssistant', lang)}
            </Typography>
            <Box display="flex" alignItems="center" gap={0.5}>
              <Box sx={{ width: 7, height: 7, borderRadius: "50%", backgroundColor: "#00C853", animation: "pulse 1.5s infinite" }} />
              <Typography sx={{ fontFamily: "Poppins, sans-serif", fontSize: "11px", color: "#7D7D7D" }}>
                {t('online', lang)}
              </Typography>
            </Box>
          </Box>
        </Box>

        {/* Animated greeting lines */}
        {greetingLines.map((line, i) => (
          visibleLines > i && (
            <Box
              key={`${lang}-${i}`}
              sx={{
                mb: 2,
                p: "12px 16px",
                backgroundColor: i === 0 ? "#EEF3FF" : "#F8F9FA",
                borderRadius: "4px 18px 18px 18px",
                border: i === 0 ? "1px solid #C5D5FF" : "1px solid #F0F0F0",
                animation: "fadeSlideIn 0.4s ease",
                "@keyframes fadeSlideIn": {
                  from: { opacity: 0, transform: "translateY(8px)" },
                  to: { opacity: 1, transform: "translateY(0)" },
                },
              }}
            >
              <Typography
                sx={{
                  fontFamily: "Poppins, sans-serif",
                  fontSize: i === 0 ? "20px" : "14px",
                  fontWeight: i === 0 ? 600 : 400,
                  color: i === 0 ? "#1958F7" : "#333",
                  lineHeight: 1.5,
                }}
              >
                {personalizedGreeting ? (personalizedGreeting.split('\n')[i] || line) : line}
              </Typography>
            </Box>
          )
        ))}

        {/* Survey name badge */}
        {visibleLines >= greetingLines.length && surveyName && (
          <Box
            sx={{
              mb: 3,
              p: "10px 14px",
              backgroundColor: "#FFF8E7",
              borderRadius: "12px",
              border: "1px solid #FFD700",
              animation: "fadeSlideIn 0.4s ease",
            }}
          >
            <Typography sx={{ fontFamily: "Poppins, sans-serif", fontSize: "12px", color: "#7A5C00", mb: 0.3 }}>
              {t('todaysSurvey', lang)}
            </Typography>
            <Typography sx={{ fontFamily: "Poppins, sans-serif", fontSize: "14px", fontWeight: 600, color: "#1E1E1E" }}>
              {surveyName}
            </Typography>
          </Box>
        )}

        {/* Mode selection */}
        {visibleLines >= greetingLines.length && (
          <Box sx={{ display: "flex", gap: 1.5, mb: 3, animation: "fadeSlideIn 0.4s ease" }}>
            <Button
              variant="contained"
              startIcon={<TextFields />}
              onClick={() => router.push(`/survey/${id}/text?lang=${lang}`)}
              sx={{
                flex: 1,
                textTransform: "none",
                borderRadius: "14px",
                height: "48px",
                backgroundColor: "#1958F7",
                fontFamily: "Poppins, sans-serif",
                fontSize: "13px",
                fontWeight: 500,
                boxShadow: "0 4px 12px rgba(25, 88, 247, 0.25)",
                "&:hover": { backgroundColor: "#1443D1" },
              }}
            >
              {t('textSurvey', lang)}
            </Button>
            <Button
              variant="outlined"
              startIcon={<RecordVoiceOver />}
              onClick={handleStart}
              sx={{
                flex: 1,
                textTransform: "none",
                borderRadius: "14px",
                height: "48px",
                borderColor: "#1958F7",
                color: "#1958F7",
                fontFamily: "Poppins, sans-serif",
                fontSize: "13px",
                fontWeight: 500,
                "&:hover": { backgroundColor: "#EEF3FF", borderColor: "#1443D1" },
              }}
            >
              {t('voiceSurvey', lang)}
            </Button>
          </Box>
        )}

        <Typography sx={{ fontFamily: "Poppins, sans-serif", fontSize: "11px", color: "#AAA", textAlign: "center" }}>
          {t('confidential', lang)}
        </Typography>
      </Card>

      <style jsx global>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.4; }
        }
      `}</style>
    </Box>
  );
}
