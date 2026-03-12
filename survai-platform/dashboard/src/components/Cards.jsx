import React from "react";
import {
  Box,
  Typography,
  useMediaQuery,
  Button,
  CircularProgress,
  Alert,
} from "@mui/material";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";
import TrendingDownIcon from "@mui/icons-material/TrendingDown";
import StarBorderIcon from "@mui/icons-material/StarBorder";
import PhoneInTalkIcon from "@mui/icons-material/PhoneInTalk";
import FlagOutlinedIcon from "@mui/icons-material/FlagOutlined";
import BarChartOutlinedIcon from "@mui/icons-material/BarChartOutlined";
import Add from "@mui/icons-material/Add";
import User from "../assets/User.png";
import { useNavigate } from "react-router-dom";

const Cards = ({
  headerTitle = "Dashboard",
  variant = "default",
  statsData = {},
  loading = false,
  error = null,
}) => {
  const getCardsData = () => {
    if (variant === "riderVoice") {
      const avgCsat = statsData.AverageCSAT != null ? statsData.AverageCSAT.toFixed(1) : "N/A";
      const totalCalls = statsData.Total_Surveys ?? 0;
      const completed = statsData.Total_Completed_Surveys ?? 0;
      const completionPct = totalCalls > 0 ? ((completed / totalCalls) * 100).toFixed(0) : "N/A";
      const totalResponses = completed ?? 0;
      return [
        { title: "AVG. SATISFACTION", value: avgCsat, subtitle: null, icon: StarBorderIcon, iconColor: "#FFB74D" },
        { title: "CALL COMPLETION", value: totalCalls > 0 ? `${completionPct}%` : "N/A", subtitle: null, icon: PhoneInTalkIcon, iconColor: "#81C784" },
        { title: "CALLS THIS WEEK", value: (statsData.Total_Surveys ?? 0)?.toString() || "0", subtitle: `(${statsData.Total_Completed_Surveys_Today ?? 0} today)`, icon: PhoneInTalkIcon, iconColor: "#64B5F6" },
        { title: "FLAGGED RESPONSES", value: "0", subtitle: "None pending", icon: FlagOutlinedIcon, iconColor: "#81C784" },
        { title: "RESPONSE CHANNELS", value: totalResponses.toString(), subtitle: "total responses", subSubtitle: totalResponses === 0 ? "No responses yet" : null, icon: BarChartOutlinedIcon, iconColor: "#B39DDB" },
      ];
    }
    if (headerTitle === "Dashboard") {
      return [
        {
          title: "Created Templates",
          value: statsData.Total_Templates?.toString() || "0",
          change: `${statsData.Total_Templates_ThisMonth || 0} this month`,
          isPositive: (statsData.Total_Templates_ThisMonth || 0) > 0,
        },
        {
          title: "Published Templates",
          value: statsData.Total_Published_Templates?.toString() || "0",
          change: `${statsData.Total_Published_Templates_ThisMonth || 0} this month`,
          isPositive: (statsData.Total_Published_Templates_ThisMonth || 0) > 0,
        },
        {
          title: "Active Surveys",
          value: statsData.Total_Active_Surveys?.toString() || "0",
          change: `${statsData.Total_Surveys || 0} total surveys`,
          isPositive: (statsData.Total_Active_Surveys || 0) > 0,
        },
        {
          title: "Completed Surveys",
          value: statsData.Total_Completed_Surveys?.toString() || "0",
          change: `${statsData.Total_Completed_Surveys_Today || 0} completed today`,
          isPositive: (statsData.Total_Completed_Surveys_Today || 0) > 0,
        },
        {
          title: "Completed Today",
          value: statsData.Total_Completed_Surveys_Today?.toString() || "0",
          change: `out of ${statsData.Total_Active_Surveys || 0} active`,
          isPositive: (statsData.Total_Completed_Surveys_Today || 0) > 0,
        },
        {
          title: "Avg Completion Time",
          value: `${Math.floor((statsData.Median_Completion_Duration || 0) / 60)}m`,
          change: `${statsData.Median_Completion_Duration_Today ? Math.floor(statsData.Median_Completion_Duration_Today / 60) : 0}m today`,
          isPositive: (statsData.Median_Completion_Duration_Today || 0) > 0,
        },
      ];
    }
    if (headerTitle === "Manage Surveys") {
      return [
        {
          title: "Total Surveys",
          value: statsData.Total_Surveys?.toString() || "0",
          change: `${statsData.Total_Templates_ThisMonth || 0} this month`,
          isPositive: (statsData.Total_Templates_ThisMonth || 0) > 0,
        },
        {
          title: "Active Surveys",
          value: statsData.Total_Active_Surveys?.toString() || "0",
          change: `${statsData.Total_Surveys || 0} total surveys`,
          isPositive: (statsData.Total_Active_Surveys || 0) > 0,
        },
        {
          title: "Completed Surveys",
          value: statsData.Total_Completed_Surveys?.toString() || "0",
          change: `${
            statsData.Total_Completed_Surveys_Today || 0
          } completed today`,
          isPositive: (statsData.Total_Completed_Surveys_Today || 0) > 0,
        },
      ];
    }
    if (headerTitle === "Completed Surveys") {
      return [
        {
          title: "Total Surveys",
          value: statsData.Total_Surveys?.toString() || "0",
          change: `${statsData.Total_Templates_ThisMonth || 0} this month`,
          isPositive: (statsData.Total_Templates_ThisMonth || 0) > 0,
        },
        {
          title: "Active Surveys",
          value: statsData.Total_Active_Surveys?.toString() || "0",
          change: `${statsData.Total_Surveys || 0} total surveys`,
          isPositive: (statsData.Total_Active_Surveys || 0) > 0,
        },
        {
          title: "Completed Surveys",
          value: statsData.Total_Completed_Surveys?.toString() || "0",
          change: `${
            statsData.Total_Completed_Surveys_Today || 0
          } completed today`,
          isPositive: (statsData.Total_Completed_Surveys_Today || 0) > 0,
        },
      ];
    }
    return [
      {
        title: "Total Templates",
        value: statsData.Total_Templates?.toString() || "0",
        change: `${statsData.Total_Templates_ThisMonth || 0} this month`,
        isPositive: (statsData.Total_Templates_ThisMonth || 0) > 0,
      },
      {
        title: "Draft Templates", 
        value: statsData.Total_Draft_Templates?.toString() || "0",
        change: `${(statsData.Total_Templates_ThisMonth || 0) - (statsData.Total_Published_Templates_ThisMonth || 0)} this month`,
        isPositive: ((statsData.Total_Templates_ThisMonth || 0) - (statsData.Total_Published_Templates_ThisMonth || 0)) > 0,
      },
      {
        title: "Published Templates",
        value: statsData.Total_Published_Templates?.toString() || "0", 
        change: `${statsData.Total_Published_Templates_ThisMonth || 0} this month`,
        isPositive: (statsData.Total_Published_Templates_ThisMonth || 0) > 0,
      },
    ];
  };

  const navigate = useNavigate();

  const displayData = getCardsData();
  const isMobile = useMediaQuery("(max-width: 600px)");
  const isSmallMobile = useMediaQuery("(max-width: 400px)");

  const isRiderVoice = variant === "riderVoice";

  return (
    <Box
      sx={{
        py: isMobile ? 2 : 0,
        pb: isRiderVoice ? 3 : (isMobile ? 2 : 4),
      }}
    >
      {/* Header - hide for riderVoice (title is on page) */}
      {!isRiderVoice && (
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            mb: 4,
          }}
        >
          <Typography
            sx={{
              fontFamily: "Poppins, sans-serif",
              fontWeight: 500,
              fontSize: isMobile ? "20px" : "28px",
              lineHeight: "100%",
              mb: 1,
            }}
          >
            {headerTitle}
          </Typography>

          <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
            {headerTitle === "Manage Templates" && (
              <Button
                variant="contained"
                onClick={() => navigate('/templates/create')}
                startIcon={<Add />}
                sx={{
                  width: isMobile ? "170px" : "220px",
                  height: "48px",
                  background: "linear-gradient(180deg, #1958F7 0%, #3D69D9 100%)",
                  color: "white",
                  textTransform: "none",
                  borderRadius: "15px",
                  py: 1.5,
                  fontFamily: "Poppins, sans-serif",
                  fontSize: isMobile ? "12px" : "14px",
                  fontWeight: 400,
                  "&:hover": {
                    backgroundColor: "#1565c0",
                  },
                }}
              >
                Create Template
              </Button>
            )}
            {headerTitle === "Dashboard" && !isRiderVoice && <img src={User} alt="user" />}
          </Box>
        </Box>
      )}

      {/* Stats Cards */}
      <Box
        sx={{
          display: "flex",
          flexWrap: "wrap",
          justifyContent: isMobile ? "center" : "start",
          gap: isMobile ? 1.5 : 2,
          minHeight: isRiderVoice ? "100px" : "150px",
        }}
      >
        {/* Loading State */}
        {loading && (
          <Box
            sx={{
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              width: "100%",
              height: "150px",
            }}
          >
            <CircularProgress size={40} sx={{ color: "#1958F7" }} />
          </Box>
        )}

        {/* Error State */}
        {error && (
          <Box
            sx={{
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              width: "100%",
              height: "150px",
            }}
          >
            <Alert severity="error" sx={{ maxWidth: 400 }}>
              Error loading statistics: {error}
            </Alert>
          </Box>
        )}

        {/* Rider Voice style cards: white bg, subtle border, colored icons */}
        {!loading && !error && isRiderVoice && displayData.map((stat, index) => {
          const Icon = stat.icon;
          const iconColor = stat.iconColor || "#9E9E9E";
          return (
            <Box
              key={index}
              sx={{
                flex: isMobile ? "1 1 140px" : "1 1 180px",
                minWidth: isMobile ? 140 : 180,
                maxWidth: isMobile ? "none" : 240,
                minHeight: "100px",
                borderRadius: "12px",
                backgroundColor: "#fff",
                border: "1px solid #E8E8E8",
                boxShadow: "0 1px 3px rgba(0,0,0,0.06)",
                display: "flex",
                flexDirection: "column",
                justifyContent: "space-between",
                px: 2,
                py: 2,
                boxSizing: "border-box",
              }}
            >
              <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                <Typography
                  sx={{
                    fontFamily: "Poppins, sans-serif",
                    fontWeight: 500,
                    fontSize: "11px",
                    lineHeight: "14px",
                    color: "#7D7D7D",
                    letterSpacing: "0.02em",
                  }}
                >
                  {stat.title}
                </Typography>
                {Icon && <Icon sx={{ fontSize: 22, color: iconColor }} />}
              </Box>
              <Typography
                sx={{
                  fontFamily: "Poppins, sans-serif",
                  fontWeight: 600,
                  fontSize: "22px",
                  lineHeight: "28px",
                  color: "#1E1E1E",
                }}
              >
                {stat.value}
              </Typography>
              {(stat.subtitle || stat.subSubtitle) && (
                <Typography
                  sx={{
                    fontFamily: "Poppins, sans-serif",
                    fontWeight: 400,
                    fontSize: "12px",
                    color: "#7D7D7D",
                  }}
                >
                  {stat.subtitle}
                  {stat.subSubtitle && (
                    <>
                      <br />
                      {stat.subSubtitle}
                    </>
                  )}
                </Typography>
              )}
            </Box>
          );
        })}

        {/* Default style cards */}
        {!loading &&
          !error &&
          !isRiderVoice &&
          displayData.map((stat, index) => (
            <Box
              key={index}
              sx={{
                width: isSmallMobile ? "135px" : isMobile ? "155px" : "300px",
                minHeight: "115px",
                borderRadius: "20px",
                border: "1px solid #F0F0F0",
                display: "flex",
                flexDirection: "column",
                justifyContent: "center",
                px: 2,
                py: 3,
                boxSizing: "border-box",
              }}
            >
              <Typography
                sx={{
                  fontFamily: "Poppins, sans-serif",
                  fontWeight: 400,
                  fontSize: "16px",
                  lineHeight: "28px",
                  color: "#929292",
                  mb: 1,
                }}
              >
                {stat.title}
              </Typography>

              <Typography
                sx={{
                  fontFamily: "Poppins, sans-serif",
                  fontWeight: 500,
                  fontSize: "24px",
                  lineHeight: "100%",
                  color: "#1E1E1E",
                  mb: 1,
                }}
              >
                {stat.value}
              </Typography>

              <Box
                sx={{
                  display: "flex",
                  alignItems: "center",
                  gap: 0.5,
                }}
              >
                {stat.isPositive ? (
                  <TrendingUpIcon sx={{ fontSize: 16, color: "#00A857" }} />
                ) : (
                  <TrendingDownIcon sx={{ fontSize: 16, color: "#FF3535" }} />
                )}
                <Typography
                  sx={{
                    fontFamily: "Poppins, sans-serif",
                    fontWeight: 400,
                    fontSize: "12px",
                    lineHeight: "100%",
                  }}
                >
                  <Box
                    component="span"
                    sx={{ color: stat.isPositive ? "#00A857" : "#FF3535" }}
                  >
                    {stat.change.split(" ")[0]}
                  </Box>{" "}
                  <Box component="span" sx={{ color: "#929292" }}>
                    {stat.change.split(" ").slice(1).join(" ")}
                  </Box>
                </Typography>
              </Box>
            </Box>
          ))}
      </Box>
    </Box>
  );
};

export default Cards;
