import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  CircularProgress,
  Alert,
  Grid,
  Button,
  FormControl,
  Select,
  MenuItem,
  Paper,
} from '@mui/material';
import {
  Users,
  CheckCircle,
  Clock,
  TrendingUp,
  Download,
  ChevronLeft,
  Phone,
  Globe,
  QrCode
} from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';
import AnalyticsService from '../../../services/Analytics/analyticsService';
import { useAuth } from '../../../context/AuthContext';
import StatCard from '../../../components/StatCard';

const Analytics = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [summary, setSummary] = useState(null);
  const [stats, setStats] = useState(null);

  // Use real data from API
  const totalResponses = summary?.total_surveys || 0;
  const completedSurveys = summary?.completed || 0;
  const avgDurationMin = summary?.avg_duration_seconds ? Math.round(summary.avg_duration_seconds / 60) + " min" : "0 min";
  const completionRate = summary?.completion_rate ? summary.completion_rate.toFixed(1) + "%" : "0%";

  // Channel data from API
  const channelData = {
    phone: { count: summary?.channel_counts?.phone || 0, percentage: summary?.channel_counts?.phone ? ((summary.channel_counts.phone / (summary.total_surveys || 1)) * 100).toFixed(1) : 0 },
    web: { count: summary?.channel_counts?.web || 0, percentage: summary?.channel_counts?.web ? ((summary.channel_counts.web / (summary.total_surveys || 1)) * 100).toFixed(1) : 0 },
    qr: { count: summary?.channel_counts?.qr || 0, percentage: summary?.channel_counts?.qr ? ((summary.channel_counts.qr / (summary.total_surveys || 1)) * 100).toFixed(1) : 0 }
  };

  // Real dropout points from API
  const dropoutPoints = summary?.dropout_points?.map((point, index) => ({
    q: `Q${index + 1}`,
    question: point.question || 'Unknown question',
    dropoffs: point.count || 0
  })) || [];

  // Real recent surveys from API
  const recentSurveys = stats?.recent_surveys?.slice(0, 5).map(survey => ({
    name: survey.name || survey.survey_id || 'Unknown',
    recipient: survey.recipient || 'Unknown',
    status: survey.status || 'Unknown',
    completed: survey.completion_date || '—',
    csat: survey.csat || '—'
  })) || [];

  // Real chart data from API (if available, otherwise use completion trend)
  const chartData = stats?.completion_trend?.map(item => ({
    name: item.date || 'Unknown',
    value: item.completion_rate || 0
  })) || [
    { name: 'Today', value: (summary?.completion_rate || 0) / 100 },
  ];

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const tenantId = user?.tenantId || '';
        const [summaryData, statsData] = await Promise.all([
          AnalyticsService.getSummary(),
          AnalyticsService.getSurveyStats(tenantId),
        ]);
        setSummary(summaryData);
        setStats(statsData);
      } catch (err) {
        console.error('Error loading analytics:', err);
        setError('Failed to load analytics data.');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [user]);

  if (loading) {
    return (
      <Box sx={{ flexGrow: 1, display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '80vh' }}>
        <CircularProgress size={60} sx={{ color: '#6366f1' }} />
      </Box>
    );
  }

  return (
    <Box sx={{
      p: { xs: 3, md: 4 },
      maxWidth: 1400,
      mx: 'auto',
      width: '100%',
      minHeight: '100%',
      background: 'linear-gradient(180deg, rgba(249, 250, 251, 0.98) 0%, rgba(243, 244, 246, 0.95) 100%)',
    }}>
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Header with ITCURVES logo style */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h6" sx={{ color: '#6366f1', fontWeight: 700, letterSpacing: '0.5px' }}>
          ITCURVES
        </Typography>
        <Typography variant="body2" sx={{ color: '#6b7280', mb: 2 }}>
          INTELLIGENT TRANSPORTATION SOFTWARE
        </Typography>
      </Box>

      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 6 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Button sx={{ minWidth: 0, p: 1, color: '#6b7280' }}>
            <ChevronLeft size={24} />
          </Button>
          <Box>
            <Typography variant="h3" sx={{ fontWeight: 800, color: '#111827', mb: 1, fontSize: { xs: '2rem', md: '2.5rem' } }}>
              Analytics
            </Typography>
            <Typography variant="h6" sx={{ color: '#6b7280', fontWeight: 400 }}>
              View response data and insights
            </Typography>
          </Box>
        </Box>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <FormControl size="small" sx={{ minWidth: 200, bgcolor: '#fff' }}>
            <Select value="all" displayEmpty>
              <MenuItem value="all">All Surveys</MenuItem>
            </Select>
          </FormControl>
          <Button variant="outlined" startIcon={<Download size={18} />} sx={{ color: '#4b5563', borderColor: '#e5e7eb', bgcolor: '#fff' }}>
            Export CSV
          </Button>
          <Button variant="outlined" startIcon={<Download size={18} />} sx={{ color: '#4b5563', borderColor: '#e5e7eb', bgcolor: '#fff' }}>
            Export PDF
          </Button>
        </Box>
      </Box>

      {/* Stats Cards - Updated with values from image */}
      <Grid container spacing={3} sx={{ mb: 6 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="TOTAL RESPONSES" value={totalResponses} icon={Users} color="#6366f1" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="COMPLETED" value={totalResponses} icon={CheckCircle} color="#10b981" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="AVG. DURATION" value={avgDurationMin} icon={Clock} color="#8b5cf6" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="COMPLETION RATE" value={completionRate} icon={TrendingUp} color="#f59e0b" />
        </Grid>
      </Grid>

      {/* Tabs */}
      <Box sx={{ display: 'flex', gap: 4, borderBottom: '1px solid #e5e7eb', mb: 4 }}>
        {['Overview'].map((tab, i) => (
          <Typography
            key={tab}
            sx={{
              pb: 2,
              color: i === 0 ? '#111827' : '#6b7280',
              fontWeight: 600,
              cursor: 'pointer',
              borderBottom: i === 0 ? '2px solid #6366f1' : 'none',
              fontSize: '15px'
            }}
          >
            {tab}
          </Typography>
        ))}
      </Box>

      {/* Main Content Grid */}
      <Grid container spacing={4}>
        {/* Chart Column */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 4, borderRadius: 4, height: 450, width: '100%' }}>
            <Typography variant="h6" sx={{ fontWeight: 700, mb: 4 }}>
              Responses Over Time
            </Typography>
            <Box sx={{ width: '100%', height: 'calc(100% - 60px)' }}>
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#6366f1" stopOpacity={0.1} />
                      <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f3f4f6" />
                  <XAxis
                    dataKey="name"
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: '#9ca3af', fontSize: 12 }}
                    dy={10}
                  />
                  <YAxis
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: '#9ca3af', fontSize: 12 }}
                    dx={-10}
                    domain={[0, 0.35]}
                    ticks={[0, 0.075, 0.15, 0.225, 0.3]}
                    width={60}
                  />
                  <Tooltip
                    contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                  />
                  <Area
                    type="monotone"
                    dataKey="value"
                    stroke="#6366f1"
                    strokeWidth={3}
                    fillOpacity={1}
                    fill="url(#colorValue)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </Box>
          </Paper>
        </Grid>

        {/* Channels Column */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 4, borderRadius: 4, height: 450, width: '100%' }}>
            <Typography variant="h6" sx={{ fontWeight: 700, mb: 4 }}>
              Response Channels
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, height: 'calc(100% - 60px)' }}>
              {[
                { key: 'phone', label: 'Phone Calls', icon: Phone, color: '#10b981' },
                { key: 'web', label: 'Web Survey', icon: Globe, color: '#6366f1' },
                { key: 'qr', label: 'QR Code', icon: QrCode, color: '#8b5cf6' }
              ].map((channel) => {
                const data = channelData[channel.key];
                return (
                  <Box
                    key={channel.label}
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      p: 2,
                      borderRadius: 3,
                      bgcolor: '#f9fafb',
                      width: '100%'
                    }}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flex: 1 }}>
                      <Box sx={{ p: 1, borderRadius: 2, bgcolor: `${channel.color}15`, color: channel.color }}>
                        <channel.icon size={20} />
                      </Box>
                      <Box>
                        <Typography variant="body1" sx={{ fontWeight: 600 }}>
                          {channel.label}
                        </Typography>
                        <Typography variant="caption" sx={{ color: '#6b7280' }}>
                          {data.count} responses
                        </Typography>
                      </Box>
                    </Box>
                    <Typography variant="body1" sx={{ fontWeight: 700, ml: 2 }}>
                      {data.percentage}%
                    </Typography>
                  </Box>
                );
              })}
            </Box>
          </Paper>
        </Grid>
      </Grid>
      {/* Top Dropout Points */}
      <Paper sx={{ p: 4, borderRadius: 4, mt: 4 }}>
        <Typography variant="h6" sx={{ fontWeight: 700, mb: 0.5 }}>
          Top Dropout Points
        </Typography>
        <Typography variant="body2" sx={{ color: '#9ca3af', mb: 3 }}>
          Where in-progress surveys stopped responding
        </Typography>
        <Box sx={{ display: 'flex', flexDirection: 'column' }}>
          {dropoutPoints.map((item, i) => (
            <Box
              key={i}
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                py: 2,
                borderBottom: i < dropoutPoints.length - 1 ? '1px solid #f3f4f6' : 'none',
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box sx={{
                  px: 1.5, py: 0.5, borderRadius: 1.5,
                  bgcolor: '#ede9fe', color: '#6366f1',
                  fontSize: '12px', fontWeight: 700, minWidth: 36, textAlign: 'center'
                }}>
                  {item.q}
                </Box>
                <Typography variant="body2" sx={{ color: '#374151' }}>
                  {item.question}
                </Typography>
              </Box>
              <Typography variant="body2" sx={{
                color: '#f59e0b', fontWeight: 600, whiteSpace: 'nowrap', ml: 2
              }}>
                {item.dropoffs} dropoffs
              </Typography>
            </Box>
          ))}
        </Box>
      </Paper>

      {/* Recently Completed Surveys */}
      <Paper sx={{ p: 4, borderRadius: 4, mt: 4 }}>
        <Typography variant="h6" sx={{ fontWeight: 700, mb: 3 }}>
          Recently Completed Surveys
        </Typography>
        <Box sx={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                {['Survey', 'Recipient', 'Status', 'Completed', 'CSAT'].map((col) => (
                  <th key={col} style={{
                    textAlign: 'left', padding: '8px 12px',
                    color: '#6b7280', fontWeight: 600, fontSize: '13px',
                    borderBottom: '1px solid #f3f4f6'
                  }}>
                    {col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {recentSurveys.map((row, i) => (
                <tr key={i} style={{ borderBottom: '1px solid #f9fafb' }}>
                  <td style={{ padding: '14px 12px', fontWeight: 600, fontSize: '14px', color: '#111827' }}>
                    {row.name}
                  </td>
                  <td style={{ padding: '14px 12px', fontSize: '14px', color: '#374151' }}>
                    {row.recipient}
                  </td>
                  <td style={{ padding: '14px 12px' }}>
                    <Box component="span" sx={{
                      px: 2, py: 0.5, borderRadius: 5,
                      bgcolor: '#d1fae5', color: '#065f46',
                      fontSize: '13px', fontWeight: 600
                    }}>
                      {row.status}
                    </Box>
                  </td>
                  <td style={{ padding: '14px 12px', fontSize: '14px', color: '#6b7280' }}>
                    {row.completed}
                  </td>
                  <td style={{ padding: '14px 12px', fontSize: '14px', color: '#6b7280' }}>
                    {row.csat}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Box>
      </Paper>
    </Box>
  );
};

export default Analytics;