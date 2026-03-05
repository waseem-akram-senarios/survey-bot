import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  CircularProgress,
  Alert,
  useMediaQuery,
  Paper,
  Chip,
  LinearProgress,
  Divider,
  Button,
} from '@mui/material';
import {
  TrendingUp,
  AccessTime,
  CheckCircleOutline,
  PeopleOutline,
  AssessmentOutlined,
  PhoneOutlined,
  TextFieldsOutlined,
  EmailOutlined,
  DownloadOutlined,
} from '@mui/icons-material';
import AnalyticsService from '../../../services/Analytics/analyticsService';
import { useAuth } from '../../../context/AuthContext';

const StatCard = ({ title, value, subtitle, icon, color = '#1958F7', trend }) => (
  <Paper
    elevation={0}
    sx={{
      p: 3,
      borderRadius: '16px',
      border: '1px solid #F0F0F0',
      display: 'flex',
      flexDirection: 'column',
      gap: 1,
      minWidth: 0,
      flex: 1,
    }}
  >
    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
      <Box
        sx={{
          width: 44,
          height: 44,
          borderRadius: '12px',
          backgroundColor: `${color}14`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        {React.cloneElement(icon, { sx: { color, fontSize: 22 } })}
      </Box>
      {trend && (
        <Chip
          label={trend}
          size="small"
          icon={<TrendingUp sx={{ fontSize: 14 }} />}
          sx={{
            backgroundColor: '#E8F5E9',
            color: '#2E7D32',
            fontFamily: 'Poppins, sans-serif',
            fontSize: '11px',
            fontWeight: 500,
            height: 24,
          }}
        />
      )}
    </Box>
    <Typography
      sx={{
        fontFamily: 'Poppins, sans-serif',
        fontSize: '28px',
        fontWeight: 600,
        color: '#1A1A1A',
        lineHeight: 1.2,
      }}
    >
      {value}
    </Typography>
    <Typography
      sx={{
        fontFamily: 'Poppins, sans-serif',
        fontSize: '13px',
        fontWeight: 500,
        color: '#7D7D7D',
      }}
    >
      {title}
    </Typography>
    {subtitle && (
      <Typography
        sx={{
          fontFamily: 'Poppins, sans-serif',
          fontSize: '11px',
          color: '#ABABAB',
        }}
      >
        {subtitle}
      </Typography>
    )}
  </Paper>
);

const ChannelBar = ({ label, count, total, color, icon }) => {
  const pct = total > 0 ? (count / total) * 100 : 0;
  return (
    <Box sx={{ mb: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {icon}
          <Typography sx={{ fontFamily: 'Poppins, sans-serif', fontSize: '13px', fontWeight: 500, color: '#4B4B4B' }}>
            {label}
          </Typography>
        </Box>
        <Typography sx={{ fontFamily: 'Poppins, sans-serif', fontSize: '13px', fontWeight: 600, color: '#1A1A1A' }}>
          {count} <span style={{ color: '#ABABAB', fontWeight: 400 }}>({pct.toFixed(1)}%)</span>
        </Typography>
      </Box>
      <LinearProgress
        variant="determinate"
        value={pct}
        sx={{
          height: 8,
          borderRadius: 4,
          backgroundColor: '#F0F0F0',
          '& .MuiLinearProgress-bar': { backgroundColor: color, borderRadius: 4 },
        }}
      />
    </Box>
  );
};

const ResponseTypeBar = ({ label, count, total, color }) => {
  const pct = total > 0 ? (count / total) * 100 : 0;
  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1.5 }}>
      <Box sx={{ width: 90 }}>
        <Typography sx={{ fontFamily: 'Poppins, sans-serif', fontSize: '12px', fontWeight: 500, color: '#4B4B4B', textTransform: 'capitalize' }}>
          {label}
        </Typography>
      </Box>
      <Box sx={{ flex: 1 }}>
        <LinearProgress
          variant="determinate"
          value={pct}
          sx={{
            height: 6,
            borderRadius: 3,
            backgroundColor: '#F0F0F0',
            '& .MuiLinearProgress-bar': { backgroundColor: color, borderRadius: 3 },
          }}
        />
      </Box>
      <Typography sx={{ fontFamily: 'Poppins, sans-serif', fontSize: '12px', fontWeight: 500, color: '#7D7D7D', minWidth: 30, textAlign: 'right' }}>
        {count}
      </Typography>
    </Box>
  );
};

const SectionTitle = ({ children }) => (
  <Typography
    sx={{
      fontFamily: 'Poppins, sans-serif',
      fontSize: '16px',
      fontWeight: 600,
      color: '#1A1A1A',
      mb: 2,
    }}
  >
    {children}
  </Typography>
);

const formatDuration = (seconds) => {
  if (!seconds || seconds === 0) return '0m 0s';
  const m = Math.floor(seconds / 60);
  const s = Math.round(seconds % 60);
  return m > 0 ? `${m}m ${s}s` : `${s}s`;
};

const Analytics = () => {
  const isMobile = useMediaQuery('(max-width: 600px)');
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [summary, setSummary] = useState(null);
  const [stats, setStats] = useState(null);
  const [completedSurveys, setCompletedSurveys] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const tenantId = user?.tenantId || '';
        const [summaryData, statsData, completed] = await Promise.all([
          AnalyticsService.getSummary(),
          AnalyticsService.getSurveyStats(tenantId),
          AnalyticsService.getCompletedSurveys(tenantId),
        ]);
        setSummary(summaryData);
        setStats(statsData);
        setCompletedSurveys(completed || []);
      } catch (err) {
        console.error('Error loading analytics:', err);
        setError('Failed to load analytics data.');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [user]);

  const handleExport = (type) => {
    const baseUrl = import.meta.env.VITE_SERVER_URL || '';
    window.open(`${baseUrl}/api/export/${type}`, '_blank');
  };

  if (loading) {
    return (
      <Box sx={{ backgroundColor: '#F9FBFC', flexGrow: 1, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
        <CircularProgress size={60} sx={{ color: '#1958F7' }} />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ backgroundColor: '#F9FBFC', flexGrow: 1, p: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  const totalSurveys = stats?.Total_Surveys || summary?.total_surveys || 0;
  const completed = stats?.Total_Completed_Surveys || summary?.completed || 0;
  const active = stats?.Total_Active_Surveys || 0;
  const completionRate = totalSurveys > 0 ? ((completed / totalSurveys) * 100).toFixed(1) : '0';
  const avgDuration = summary?.avg_duration_seconds || 0;
  const avgCSAT = stats?.AverageCSAT || 0;
  const completedToday = stats?.Total_Completed_Surveys_Today || 0;
  const medianDuration = stats?.Median_Completion_Duration || 0;
  const channelCounts = summary?.channel_counts || {};
  const totalChannels = Object.values(channelCounts).reduce((a, b) => a + b, 0);
  const dropoutPoints = summary?.dropout_points || [];
  const responseTypes = summary?.response_types || {};
  const totalResponses = Object.values(responseTypes).reduce((a, b) => a + b, 0);

  const responseColors = { open: '#1958F7', scale: '#FF9800', categorical: '#4CAF50', text: '#9C27B0', unknown: '#999' };
  const responseLabels = { open: 'Open', scale: 'Scale', categorical: 'Multiple Choice', text: 'Text', unknown: 'Unknown' };

  return (
    <Box
      sx={{
        backgroundColor: '#F9FBFC',
        flexGrow: 1,
        display: 'flex',
        flexDirection: 'column',
        p: isMobile ? 2 : 4,
        overflow: 'auto',
        width: '100%',
      }}
    >
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography sx={{ fontFamily: 'Poppins, sans-serif', fontSize: '24px', fontWeight: 600, color: '#1A1A1A' }}>
            Analytics
          </Typography>
          <Typography sx={{ fontFamily: 'Poppins, sans-serif', fontSize: '13px', color: '#7D7D7D' }}>
            Survey performance and insights
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            size="small"
            startIcon={<DownloadOutlined />}
            onClick={() => handleExport('surveys')}
            sx={{
              fontFamily: 'Poppins, sans-serif',
              textTransform: 'none',
              borderRadius: '10px',
              borderColor: '#E0E0E0',
              color: '#4B4B4B',
              fontSize: '12px',
              '&:hover': { borderColor: '#1958F7', color: '#1958F7' },
            }}
          >
            Export Surveys
          </Button>
          <Button
            variant="outlined"
            size="small"
            startIcon={<DownloadOutlined />}
            onClick={() => handleExport('transcripts')}
            sx={{
              fontFamily: 'Poppins, sans-serif',
              textTransform: 'none',
              borderRadius: '10px',
              borderColor: '#E0E0E0',
              color: '#4B4B4B',
              fontSize: '12px',
              '&:hover': { borderColor: '#1958F7', color: '#1958F7' },
            }}
          >
            Export Transcripts
          </Button>
        </Box>
      </Box>

      {/* Stat Cards */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: isMobile ? '1fr 1fr' : 'repeat(4, 1fr)',
          gap: 2,
          mb: 3,
        }}
      >
        <StatCard
          title="Total Surveys"
          value={totalSurveys}
          subtitle={`${completedToday} completed today`}
          icon={<AssessmentOutlined />}
          color="#1958F7"
        />
        <StatCard
          title="Completed"
          value={completed}
          subtitle={`${completionRate}% completion rate`}
          icon={<CheckCircleOutline />}
          color="#4CAF50"
          trend={completedToday > 0 ? `+${completedToday} today` : undefined}
        />
        <StatCard
          title="In Progress"
          value={active}
          subtitle="Active surveys"
          icon={<PeopleOutline />}
          color="#FF9800"
        />
        <StatCard
          title="Avg Duration"
          value={formatDuration(medianDuration || avgDuration)}
          subtitle={avgCSAT > 0 ? `Avg CSAT: ${avgCSAT.toFixed(1)}/5` : 'Median completion time'}
          icon={<AccessTime />}
          color="#9C27B0"
        />
      </Box>

      {/* Two Column Layout */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: isMobile ? '1fr' : '1fr 1fr',
          gap: 3,
          mb: 3,
        }}
      >
        {/* Channel Distribution */}
        <Paper elevation={0} sx={{ p: 3, borderRadius: '16px', border: '1px solid #F0F0F0' }}>
          <SectionTitle>Channel Distribution</SectionTitle>
          {totalChannels > 0 ? (
            <>
              <ChannelBar
                label="Phone"
                count={channelCounts.phone || 0}
                total={totalChannels}
                color="#1958F7"
                icon={<PhoneOutlined sx={{ fontSize: 16, color: '#1958F7' }} />}
              />
              <ChannelBar
                label="Text / Web"
                count={(channelCounts.text || 0) + (channelCounts.web || 0)}
                total={totalChannels}
                color="#4CAF50"
                icon={<TextFieldsOutlined sx={{ fontSize: 16, color: '#4CAF50' }} />}
              />
              <ChannelBar
                label="Email"
                count={channelCounts.email || 0}
                total={totalChannels}
                color="#FF9800"
                icon={<EmailOutlined sx={{ fontSize: 16, color: '#FF9800' }} />}
              />
              {Object.entries(channelCounts)
                .filter(([k]) => !['phone', 'text', 'web', 'email'].includes(k))
                .map(([k, v]) => (
                  <ChannelBar key={k} label={k} count={v} total={totalChannels} color="#999" icon={<AssessmentOutlined sx={{ fontSize: 16, color: '#999' }} />} />
                ))}
            </>
          ) : (
            <Typography sx={{ fontFamily: 'Poppins, sans-serif', fontSize: '13px', color: '#ABABAB' }}>
              No channel data yet
            </Typography>
          )}
        </Paper>

        {/* Response Types */}
        <Paper elevation={0} sx={{ p: 3, borderRadius: '16px', border: '1px solid #F0F0F0' }}>
          <SectionTitle>Response Types</SectionTitle>
          {totalResponses > 0 ? (
            <>
              {Object.entries(responseTypes)
                .sort(([, a], [, b]) => b - a)
                .map(([type, count]) => (
                  <ResponseTypeBar
                    key={type}
                    label={responseLabels[type] || type}
                    count={count}
                    total={totalResponses}
                    color={responseColors[type] || '#999'}
                  />
                ))}
              <Divider sx={{ my: 1.5 }} />
              <Typography sx={{ fontFamily: 'Poppins, sans-serif', fontSize: '12px', color: '#ABABAB' }}>
                Total responses: {totalResponses}
              </Typography>
            </>
          ) : (
            <Typography sx={{ fontFamily: 'Poppins, sans-serif', fontSize: '13px', color: '#ABABAB' }}>
              No response data yet
            </Typography>
          )}
        </Paper>
      </Box>

      {/* Dropout Points */}
      {dropoutPoints.length > 0 && (
        <Paper elevation={0} sx={{ p: 3, borderRadius: '16px', border: '1px solid #F0F0F0', mb: 3 }}>
          <SectionTitle>Top Dropout Points</SectionTitle>
          <Typography sx={{ fontFamily: 'Poppins, sans-serif', fontSize: '12px', color: '#ABABAB', mb: 2 }}>
            Where in-progress surveys stopped responding
          </Typography>
          {dropoutPoints.map((dp, i) => (
            <Box key={i} sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1.5, p: 1.5, borderRadius: '10px', backgroundColor: '#FAFAFA' }}>
              <Chip
                label={`Q${dp.question_order}`}
                size="small"
                sx={{
                  fontFamily: 'Poppins, sans-serif',
                  fontWeight: 600,
                  fontSize: '11px',
                  backgroundColor: '#1958F714',
                  color: '#1958F7',
                }}
              />
              <Typography sx={{ fontFamily: 'Poppins, sans-serif', fontSize: '13px', color: '#4B4B4B', flex: 1 }} noWrap>
                {dp.question}
              </Typography>
              <Chip
                label={`${dp.count} dropoffs`}
                size="small"
                sx={{
                  fontFamily: 'Poppins, sans-serif',
                  fontSize: '11px',
                  fontWeight: 500,
                  backgroundColor: '#FFF3E0',
                  color: '#E65100',
                }}
              />
            </Box>
          ))}
        </Paper>
      )}

      {/* Recently Completed */}
      {completedSurveys.length > 0 && (
        <Paper elevation={0} sx={{ p: 3, borderRadius: '16px', border: '1px solid #F0F0F0' }}>
          <SectionTitle>Recently Completed Surveys</SectionTitle>
          <Box sx={{ overflowX: 'auto' }}>
            <Box component="table" sx={{ width: '100%', borderCollapse: 'collapse' }}>
              <Box component="thead">
                <Box component="tr" sx={{ borderBottom: '1px solid #F0F0F0' }}>
                  {['Survey', 'Recipient', 'Status', 'Completed', 'CSAT'].map((h) => (
                    <Box
                      component="th"
                      key={h}
                      sx={{
                        fontFamily: 'Poppins, sans-serif',
                        fontSize: '12px',
                        fontWeight: 600,
                        color: '#7D7D7D',
                        textAlign: 'left',
                        p: 1.5,
                        whiteSpace: 'nowrap',
                      }}
                    >
                      {h}
                    </Box>
                  ))}
                </Box>
              </Box>
              <Box component="tbody">
                {completedSurveys.slice(0, 10).map((s) => (
                  <Box component="tr" key={s.SurveyId} sx={{ borderBottom: '1px solid #FAFAFA', '&:hover': { backgroundColor: '#FAFAFA' } }}>
                    <Box component="td" sx={{ p: 1.5, fontFamily: 'Poppins, sans-serif', fontSize: '13px', color: '#1A1A1A', fontWeight: 500 }}>
                      {s.Name || s.SurveyId}
                    </Box>
                    <Box component="td" sx={{ p: 1.5, fontFamily: 'Poppins, sans-serif', fontSize: '13px', color: '#4B4B4B' }}>
                      {s.RiderName || s.Recipient || '-'}
                    </Box>
                    <Box component="td" sx={{ p: 1.5 }}>
                      <Chip
                        label={s.Status}
                        size="small"
                        sx={{
                          fontFamily: 'Poppins, sans-serif',
                          fontSize: '11px',
                          fontWeight: 500,
                          backgroundColor: s.Status === 'Completed' ? '#E8F5E9' : '#FFF3E0',
                          color: s.Status === 'Completed' ? '#2E7D32' : '#E65100',
                        }}
                      />
                    </Box>
                    <Box component="td" sx={{ p: 1.5, fontFamily: 'Poppins, sans-serif', fontSize: '12px', color: '#7D7D7D' }}>
                      {s.CompletionDate || '-'}
                    </Box>
                    <Box component="td" sx={{ p: 1.5, fontFamily: 'Poppins, sans-serif', fontSize: '13px', fontWeight: 500, color: '#1958F7' }}>
                      {s.CSAT ? `${s.CSAT}/5` : '-'}
                    </Box>
                  </Box>
                ))}
              </Box>
            </Box>
          </Box>
        </Paper>
      )}
    </Box>
  );
};

export default Analytics;
