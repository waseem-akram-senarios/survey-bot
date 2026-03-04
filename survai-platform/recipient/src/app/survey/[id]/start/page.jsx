"use client"
import { Box, Typography, Grid, Button, Card, CardContent, styled } from '@mui/material';
import Header from '../../../../../components/Header';
import { useParams, useSearchParams } from "next/navigation";
import { useState, useEffect } from "react";
import { detectLanguage, t } from '../../../../lib/i18n';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

export default function StartPage() {
  const params = useParams();
  const searchParams = useSearchParams();
  const surveyId = params?.id || "101";
  const urlLang = searchParams.get("lang");
  const [lang, setLang] = useState(urlLang || "en");
  const [companyName, setCompanyName] = useState("");
  const [surveyTitle, setSurveyTitle] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/api/surveys/${surveyId}/recipient`);
        if (res.ok) {
          const data = await res.json();
          if (!urlLang && data.Name) setLang(detectLanguage(data.Name));
          if (data.CompanyName) setCompanyName(data.CompanyName);
          if (data.Name) setSurveyTitle(data.Name);
        }
      } catch (e) { /* fallback */ }
    };
    fetchData();
  }, [surveyId]);

  return (
    <Box p={{ xs: 2, md: 8 }}>
      <Header companyName={companyName} surveyTitle={surveyTitle} lang={lang} />

      <Box sx={{ display: "flex", justifyContent: "center" }}>
        <Box sx={{ width: { xs: "100%", sm: "90%", md: "75%" }, justifyContent: "left" }}>
          <Typography
            sx={{
              fontFamily: "Poppins, sans-serif",
              fontSize: "14px",
              fontWeight: "400",
              lineHeight: "20px",
              textAlign: "left",
            }}
          >
            {t('chooseMode', lang)}
          </Typography>
          <Typography
            sx={{
              fontFamily: "Poppins, sans-serif",
              fontSize: "14px",
              fontWeight: "400",
              lineHeight: "20px",
              textAlign: "left",
            }}
          >
            {t('chooseOption', lang)}
          </Typography>

          <Grid container spacing={4} alignItems="center" sx={{ marginTop: "50px" }}>
            <Grid item size={{ xs: 12, md: 6 }}>
              <Card sx={{ border: "1px solid #F0F0F0", borderRadius: "15px", padding: "24px 40px", boxShadow: "none" }}>
                <CardContent sx={{ p: 0, "&:last-child": { pb: 0 } }}>
                  <Typography sx={{ fontFamily: "Poppins, sans-serif", fontSize: "16px", fontWeight: "500", lineHeight: "28px", textAlign: "left" }}>
                    {t('textSurvey', lang)}
                  </Typography>
                  <Typography sx={{ fontFamily: "Poppins, sans-serif", fontSize: "14px", fontWeight: "500", color: "#929292", textAlign: "left", mb: 3 }}>
                    {t('textDesc', lang)}
                  </Typography>
                  <Button
                    variant="outlined"
                    href={`/survey/${surveyId}/text?lang=${lang}`}
                    sx={{
                      width: "220px", height: "47px", borderRadius: "15px", borderColor: "#f0f0f0",
                      padding: "13px 16px", color: "black", fontFamily: "Poppins, sans-serif",
                      fontSize: "14px", fontWeight: "400", textTransform: "none",
                      "&:hover": { borderColor: "#1976d2", backgroundColor: "rgba(25, 118, 210, 0.04)" },
                    }}
                  >
                    {t('startTextSurvey', lang)}
                  </Button>
                </CardContent>
              </Card>
            </Grid>
            <Grid item size={{ xs: 12, md: 6 }}>
              <Card sx={{ border: "1px solid #F0F0F0", borderRadius: "15px", padding: "24px 40px", boxShadow: "none" }}>
                <CardContent sx={{ p: 0, "&:last-child": { pb: 0 } }}>
                  <Typography sx={{ fontFamily: "Poppins, sans-serif", fontSize: "16px", fontWeight: "500", lineHeight: "28px", textAlign: "left" }}>
                    {t('voiceSurvey', lang)}
                  </Typography>
                  <Typography sx={{ fontFamily: "Poppins, sans-serif", fontSize: "14px", fontWeight: "500", color: "#929292", textAlign: "left", mb: 3 }}>
                    {t('voiceDesc', lang)}
                  </Typography>
                  <Button
                    variant="outlined"
                    href={`/survey/${surveyId}/voice?lang=${lang}`}
                    sx={{
                      width: "220px", height: "47px", borderRadius: "15px", borderColor: "#f0f0f0",
                      padding: "13px 16px", color: "black", fontFamily: "Poppins, sans-serif",
                      fontSize: "14px", fontWeight: "400", textTransform: "none",
                      "&:hover": { borderColor: "#1976d2", backgroundColor: "rgba(25, 118, 210, 0.04)" },
                    }}
                  >
                    {t('startVoiceSurvey', lang)}
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Box>
      </Box>
    </Box>
  );
}
