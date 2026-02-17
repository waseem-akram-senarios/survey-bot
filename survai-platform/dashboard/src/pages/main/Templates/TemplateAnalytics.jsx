"use client";
import { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import {
  Box,
  Typography,
  Button,
  CircularProgress,
  Alert,
  Snackbar,
  useMediaQuery,
  Avatar
} from "@mui/material";
import Sidebar from "../../../components/Sidebar";
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { ChevronLeft, ChevronRight } from "lucide-react";
import QuestionRenderer from "../../../components/QuestionRenderer";
import Header from "../../../components/Header";

const PIE_COLORS = [
  "#1958F7",
  "#FFBB71",
  "#FFF99E",
  "#FF7284",
  "#9C88FF",
  "#FF6B6B",
];

const API_BASE_URL = import.meta.env.VITE_SERVER_URL;

export default function SurveyQuestionAnalytics() {
  const location = useLocation();
  const navigate = useNavigate();

  const [templateData, setTemplateData] = useState(null);
  const [flattenedQuestions, setFlattenedQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [currentResponseIndex, setCurrentResponseIndex] = useState(0);
  const [analyticsData, setAnalyticsData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [alert, setAlert] = useState({
    open: false,
    message: "",
    severity: "info",
  });

  // Function to flatten questions including child questions
  const flattenQuestions = (questions) => {
    const flattened = [];
    
    const processQuestion = (question, level = 0, parentContext = '') => {
      // Add the main question
      flattened.push({
        ...question,
        level,
        parentContext,
        displayTitle: parentContext ? `${parentContext} → ${question.question}` : question.question
      });
      
      // Process child questions if they exist
      if (question.childQuestions) {
        Object.entries(question.childQuestions).forEach(([categoryKey, childQuestions]) => {
          if (Array.isArray(childQuestions)) {
            childQuestions.forEach(childQuestion => {
              const newParentContext = parentContext ? 
                `${parentContext} → ${question.question} (${categoryKey})` : 
                `${question.question} (${categoryKey})`;
              processQuestion(childQuestion, level + 1, newParentContext);
            });
          }
        });
      }
    };
    
    questions.forEach(question => processQuestion(question));
    return flattened;
  };

  useEffect(() => {
    if (location.state?.templateData) {
      setTemplateData(location.state.templateData);
      // Flatten questions to include child questions
      const flattened = flattenQuestions(location.state.templateData.questions);
      setFlattenedQuestions(flattened);
    } else {
      setError(
        "No template data available. Please return to the template page."
      );
      setLoading(false);
    }
  }, [location.state]);

  useEffect(() => {
    const fetchAnalyticsData = async () => {
      if (!flattenedQuestions.length) return;

      try {
        setLoading(true);
        const analyticsPromises = flattenedQuestions.map((question) =>
          fetch(
            `${API_BASE_URL}api/questions/${question.queId}/answers`
          )
            .then((res) => {
              if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
              return res.json();
            })
            .catch((error) => {
              console.error(`Failed to fetch analytics for question ${question.queId}:`, error);
              return null;
            })
        );

        const results = await Promise.all(analyticsPromises);
        console.log("Analytics results:", results);
        setAnalyticsData(results);
      } catch (error) {
        console.error("Error fetching analytics:", error);
        setError("Failed to fetch analytics data");
        showAlert("Failed to load analytics data", "error");
      } finally {
        setLoading(false);
      }
    };

    fetchAnalyticsData();
  }, [flattenedQuestions]);

  const showAlert = (message, severity = "info") => {
    setAlert({ open: true, message, severity });
  };

  const closeAlert = () => {
    setAlert({ ...alert, open: false });
  };

  const processChartData = (question, analytics) => {
    if (!analytics || !analytics[0]) return [];

    const data = analytics[0];

    if (data.criteria === "categorical") {
      // Count occurrences of each category from answers
      const counts = {};
      data.categories.forEach(category => {
        counts[category] = 0;
      });
      
      data.answers.forEach(answer => {
        if (answer && counts.hasOwnProperty(answer)) {
          counts[answer]++;
        }
      });

      return Object.entries(counts).map(([name, value]) => ({
        name,
        value: value || 0,
      }));
    } else if (data.criteria === "scale") {
      const maxRange = parseInt(data.scales || 5);
      const ratings = {};
      for (let i = 1; i <= maxRange; i++) {
        ratings[i] = 0;
      }
      
      data.answers.forEach(answer => {
        const rating = parseInt(answer);
        if (rating >= 1 && rating <= maxRange) {
          ratings[rating]++;
        }
      });
      
      return Object.entries(ratings).map(([rating, count]) => ({
        name: `${rating} Star${rating !== "1" ? "s" : ""}`,
        value: count,
      }));
    }
    return [];
  };

  const calculatePercentages = (data) => {
    const total = data.reduce((sum, item) => sum + item.value, 0);
    return data.map((item) => ({
      ...item,
      percentage: total > 0 ? ((item.value / total) * 100).toFixed(1) : 0,
    }));
  };

  const hasResponses = (analytics) => {
    if (!analytics || !analytics[0]) return false;
    const data = analytics[0];
    if (data.answers) {
      return data.answers.some(answer => answer !== null && answer !== "" && answer !== undefined);
    }
    return false;
  };

  const isOpenQuestion = (question) => {
    console.log("question criteria:", question);
    return question.type === 'open';
  };

  const getTextResponses = (analytics) => {
    if (!analytics || !analytics[0]) return [];
    const data = analytics[0];
    return data.answers.filter(answer => answer && answer.trim() !== '');
  };

  const handlePrevQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex((prev) => prev - 1);
      setCurrentResponseIndex(0); // Reset response index when changing questions
    }
  };

  const handleNextQuestion = () => {
    if (currentQuestionIndex < flattenedQuestions.length - 1) {
      setCurrentQuestionIndex((prev) => prev + 1);
      setCurrentResponseIndex(0); // Reset response index when changing questions
    }
  };

  const handlePrevResponse = () => {
    if (currentResponseIndex > 0) {
      setCurrentResponseIndex((prev) => prev - 1);
    }
  };

  const handleNextResponse = () => {
    const currentQuestion = flattenedQuestions[currentQuestionIndex];
    const textResponses = isOpenQuestion(currentQuestion) ? getTextResponses(analyticsData[currentQuestionIndex]) : [];
    if (currentResponseIndex < textResponses.length - 1) {
      setCurrentResponseIndex((prev) => prev + 1);
    }
  };

  const calculateAverageRating = (analytics) => {
    if (!analytics || !analytics[0] || analytics[0].criteria !== "scale") return 0;
    const data = analytics[0];
    const maxRange = parseInt(data.scales || 5);
    const ratings = data.answers
      .map((answer) => parseInt(answer))
      .filter((rating) => !isNaN(rating) && rating >= 1 && rating <= maxRange);
    
    if (ratings.length === 0) return 0;
    const sum = ratings.reduce((acc, rating) => acc + rating, 0);
    return (sum / ratings.length).toFixed(1);
  };

  const isMobile = useMediaQuery('(max-width: 600px)');

  if (loading) {
    return (
      <Box
        sx={{
          display: "flex",
          flexDirection: isMobile ? 'column' : 'row',
          height: "100vh",
          bgcolor: "#F8FAFC",
          fontFamily: "Poppins, sans-serif",
        }}
      >
        {isMobile ? <Header /> : <Sidebar />}
        <Box
          sx={{
            flexGrow: 1,
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
          }}
        >
          <Box
            sx={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: 2,
              backgroundColor: "white",
              padding: 4,
              borderRadius: 2,
              boxShadow: "0px 4px 15px rgba(0, 0, 0, 0.08)",
            }}
          >
            <CircularProgress size={40} sx={{ color: "#1958F7" }} />
            <Typography>Loading analytics data...</Typography>
          </Box>
        </Box>
      </Box>
    );
  }

  if (error || !templateData || !flattenedQuestions.length) {
    return (
      <Box
        sx={{
          display: "flex",
          flexDirection: isMobile ? 'column' : 'row',
          height: "100vh",
          bgcolor: "#F8FAFC",
          fontFamily: "Poppins, sans-serif",
        }}
      >
        {isMobile ? <Header /> : <Sidebar />}
        <Box sx={{ flexGrow: 1, p: 4 }}>
          <Alert severity="error" sx={{ mb: 2 }}>
            {error || "No template data available"}
          </Alert>
          <Button variant="outlined" onClick={() => navigate(-1)}>
            Go Back
          </Button>
        </Box>
      </Box>
    );
  }

  const currentQuestion = flattenedQuestions[currentQuestionIndex];
  const currentAnalytics = analyticsData[currentQuestionIndex];
  const chartData = processChartData(currentQuestion, currentAnalytics);
  const chartDataWithPercentages = calculatePercentages(chartData);
  const totalResponses = chartData.reduce((sum, item) => sum + item.value, 0);
  
  // For open questions
  const textResponses = isOpenQuestion(currentQuestion) ? getTextResponses(currentAnalytics) : [];
  const openQuestionTotalResponses = textResponses.length;

  return (
    <Box
      sx={{
        display: "flex",
        width: "90%" ,
        flexDirection: isMobile ? 'column' : 'row',
        height: "100vh",
        bgcolor: "#F8FAFC",
        fontFamily: "Poppins, sans-serif",
      }}
    >
      <Box 
        sx={{
          backgroundColor: '#F9FBFC',
          flexGrow: 1,
          display: 'flex',
          flexDirection: 'column',
          p: isMobile ? 2 : 4,
        }}
        >
        <Box
          sx={{
            height: isMobile ? 'calc(90vh - 64px)' : '100vh',
            overflow: 'auto',
            backgroundColor: "#FFFFFF",
            borderRadius: "16px",
            boxShadow: "0px 4px 15px rgba(0, 0, 0, 0.08)",
            p: 4,
          }}
        >
          <Typography
            sx={{
              fontSize: "18px",
              fontFamily: "Poppins, sans-serif",
              fontWeight: 500,
              mb: 3,
            }}
          >
            {templateData.templateName}
          </Typography>

          <Box
            sx={{
              backgroundColor: "#F9F9F9",
              borderRadius: "8px",
              boxShadow: "0px 1px 4px rgba(0, 0, 0, 0.1)",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              px: 2,
              py: 1.5,
              mb: 4,
            }}
          >
            <ChevronLeft
              style={{
                cursor: currentQuestionIndex > 0 ? "pointer" : "not-allowed",
                opacity: currentQuestionIndex > 0 ? 1 : 0.3,
                color: "#4B5563",
              }}
              onClick={handlePrevQuestion}
            />
            <Typography
              sx={{ fontSize: "16px", fontWeight: 500, color: "#111827" }}
            >
              Question {currentQuestionIndex + 1} of{" "}
              {flattenedQuestions.length}
            </Typography>
            <ChevronRight
              style={{
                cursor:
                  currentQuestionIndex < flattenedQuestions.length - 1
                    ? "pointer"
                    : "not-allowed",
                opacity:
                  currentQuestionIndex < flattenedQuestions.length - 1
                    ? 1
                    : 0.3,
                color: "#4B5563",
              }}
              onClick={handleNextQuestion}
            />
          </Box>

          {/* Show hierarchy for child questions */}
          {currentQuestion.parentContext && (
            <Box
              sx={{
                mb: 2,
                p: 2,
                backgroundColor: "#F3F4F6",
                borderRadius: "8px",
                borderLeft: "4px solid #1958F7",
              }}
            >
              <Typography
                sx={{
                  fontSize: "14px",
                  color: "#6B7280",
                  fontStyle: "italic",
                }}
              >
                Context: {currentQuestion.parentContext}
              </Typography>
            </Box>
          )}

          <QuestionRenderer
            question={currentQuestion}
            hideEdit
            hideDelete
            readOnly
            hideChildQuestions={true}
          />

          <Box sx={{ mb: 3 }}>
            <Typography sx={{ fontSize: "14px", color: "#7D7D7D" }}>
              Total Responses: {isOpenQuestion(currentQuestion) ? openQuestionTotalResponses : totalResponses}
              {currentAnalytics && currentAnalytics[0]?.criteria === "scale" &&
                totalResponses > 0 && (
                  <span style={{ marginLeft: "16px" }}>
                    Average Rating: {calculateAverageRating(currentAnalytics)} /{" "}
                    {currentAnalytics[0].scales}
                  </span>
                )}
            </Typography>
          </Box>

          {!hasResponses(currentAnalytics) ? (
            <Alert severity="info" sx={{ mb: 2 }}>
              No responses yet for this question
            </Alert>
          ) : isOpenQuestion(currentQuestion) ? (
            <Box>
              {textResponses.length > 0 ? (
                <Box>
                  {/* Response Navigation Header */}
                  <Box
                    sx={{
                      backgroundColor: "#F9F9F9",
                      borderRadius: "8px",
                      boxShadow: "0px 1px 4px rgba(0, 0, 0, 0.1)",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      px: 2,
                      py: 1.5,
                      mb: 3,
                    }}
                  >
                    <ChevronLeft
                      style={{
                        cursor: currentResponseIndex > 0 ? "pointer" : "not-allowed",
                        opacity: currentResponseIndex > 0 ? 1 : 0.3,
                        color: "#4B5563",
                      }}
                      onClick={handlePrevResponse}
                    />
                    <Typography
                      sx={{ fontSize: "16px", fontWeight: 500, color: "#111827" }}
                    >
                      Response {currentResponseIndex + 1} of {textResponses.length}
                    </Typography>
                    <ChevronRight
                      style={{
                        cursor:
                          currentResponseIndex < textResponses.length - 1
                            ? "pointer"
                            : "not-allowed",
                        opacity:
                          currentResponseIndex < textResponses.length - 1
                            ? 1
                            : 0.3,
                        color: "#4B5563",
                      }}
                      onClick={handleNextResponse}
                    />
                  </Box>

                  {/* Single Response Display */}
                  <Box
                    sx={{
                      display: "flex",
                      gap: 2,
                      p: 3,
                      backgroundColor: "#fff",
                      minHeight: '100px',
                      borderRadius: "15px",
                      border: "1px solid #F0F0F0",
                      boxShadow: '0px 4px 20px 0px #0000000D'
                    }}
                  >
                    <Box sx={{ flex: 1 }}>
                      <Typography
                        sx={{
                          fontSize: "16px",
                          color: "#212529",
                          lineHeight: 1.6,
                          wordBreak: "break-word",
                        }}
                      >
                        {textResponses[currentResponseIndex]}
                      </Typography>
                    </Box>
                  </Box>
                </Box>
              ) : (
                <Typography
                  sx={{
                    textAlign: "center",
                    color: "#6C757D",
                    fontStyle: "italic",
                    py: 4,
                  }}
                >
                  No text responses available
                </Typography>
              )}
            </Box>
          ) : (
            <Box
              sx={{
                display: "grid",
                gridTemplateColumns: { md: "1.3fr 1fr", xs: "1fr" },
                gap: 6,
              }}
            >
              <Box
                sx={{
                  backgroundColor: "#FFFFFF",
                  borderRadius: "12px",
                  boxShadow: "0px 2px 10px rgba(0, 0, 0, 0.1)",
                  p: 3,
                }}
              >
                <Typography sx={{ mb: 2, fontWeight: 500 }}>
                  Frequency of Selected Options
                </Typography>
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart
                    data={chartData}
                    layout="vertical"
                    margin={{ left: 50 }}
                  >
                    <XAxis type="number" hide />
                    <YAxis dataKey="name" type="category" />
                    <Tooltip />
                    <Bar
                      dataKey="value"
                      radius={[8, 8, 8, 8]}
                      isAnimationActive={false}
                    >
                      {chartData.map((entry, index) => (
                        <Cell
                          key={`bar-${index}`}
                          fill={index === 3 ? "#1958F7" : "#CFCDFF"}
                          style={{ filter: "none" }}
                        />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </Box>

              <Box
                sx={{
                  backgroundColor: "#FFFFFF",
                  borderRadius: "12px",
                  boxShadow: "0px 2px 10px rgba(0, 0, 0, 0.1)",
                  p: 3,
                }}
              >
                <Typography sx={{ mb: 2, fontWeight: 500 }}>
                  Percentage of Selected Options
                </Typography>
                <ResponsiveContainer width="100%" height={200}>
                  <PieChart>
                    <Pie
                      data={chartData}
                      dataKey="value"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      outerRadius={70}
                    >
                      {chartData.map((entry, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={PIE_COLORS[index % PIE_COLORS.length]}
                        />
                      ))}
                    </Pie>
                  </PieChart>
                </ResponsiveContainer>

                <Box
                  sx={{ display: "flex", flexWrap: "wrap", gap: 1.5, mt: 2 }}
                >
                  {chartDataWithPercentages.map((entry, index) => {
                    const bgColor = PIE_COLORS[index % PIE_COLORS.length];
                    const textColor =
                      bgColor === "#FFF99E" ? "#374151" : "#FFFFFF";
                    return (
                      <Box
                        key={entry.name}
                        sx={{
                          display: "flex",
                          alignItems: "center",
                          gap: 1,
                          px: 1.5,
                          py: 0.5,
                          backgroundColor: bgColor,
                          color: textColor,
                          borderRadius: "4px",
                          fontSize: "12px",
                        }}
                      >
                        {entry.name}
                      </Box>
                    );
                  })}
                </Box>
              </Box>
            </Box>
          )}

          <Button
            variant="outlined"
            sx={{
              mt: 4,
              px: 4,
              borderRadius: "8px",
              textTransform: "none",
              borderColor: "#D1D5DB",
              color: "#374151",
              fontFamily: "Poppins, sans-serif",
              "&:hover": {
                borderColor: "#D1D5DB",
                backgroundColor: "#F9FAFB",
              },
            }}
            startIcon={<ChevronLeft />}
            onClick={() => navigate(-1)}
          >
            Back
          </Button>
        </Box>

      <Snackbar
        open={alert.open}
        autoHideDuration={4000}
        onClose={closeAlert}
        anchorOrigin={{ vertical: "top", horizontal: "center" }}
      >
        <Alert
          onClose={closeAlert}
          severity={alert.severity}
          sx={{ width: "100%" }}
        >
          {alert.message}
        </Alert>
      </Snackbar>
      </Box>
    </Box>
  );
}