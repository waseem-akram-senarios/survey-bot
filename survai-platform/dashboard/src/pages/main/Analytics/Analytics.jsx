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
  Divider,
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
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  AreaChart,
  Area
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

  // Mock data for the chart since real data might not be formatted for the new chart type yet
  const chartData = [
    { name: 'Feb 11', value: 0 },
    { name: 'Feb 15', value: 0.2 },
    { name: 'Feb 21', value: 0.1 },
    { name: 'Feb 27', value: 0.3 },
    { name: 'Mar 1', value: 0.1 },
    { name: 'Mar 5', value: 0.2 },
    { name: 'Mar 9', value: 0.1 },
    { name: 'Mar 12', value: 0 },
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

  const totalResponses = stats?.Total_Completed_Surveys ?? summary?.completed ?? 0;
  const completionRate = summary?.completion_rate != null ? `${Number(summary.completion_rate).toFixed(1)}%` : '0%';
  const avgDurationMin = summary?.avg_duration_seconds != null
    ? `${Math.round(Number(summary.avg_duration_seconds) / 60)} min`
    : '0 min';
  const channelCounts = summary?.channel_counts || {};

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
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 6 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
           <Button sx={{ minWidth: 0, p: 1, color: '#6b7280' }}>
              <ChevronLeft size={24} />
           </Button>
           <Box>
            <Typography variant="h3" sx={{ fontWeight: 800, color: 'var(--color-gray-900)', mb: 1, fontSize: { xs: '2rem', md: '2.5rem' } }}>
              Analytics
            </Typography>
            <Typography variant="h6" sx={{ color: 'var(--color-gray-600)', fontWeight: 400 }}>
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

      {/* Stats Cards */}
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
        {['Overview', 'Question Analysis', 'Flagged', 'AI Insights'].map((tab, i) => (
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
          <Paper sx={{ p: 4, borderRadius: 4, height: 450, display: 'flex', flexDirection: 'column' }}>
            <Typography variant="h6" sx={{ fontWeight: 700, mb: 4 }}>
              Responses Over Time
            </Typography>
            <Box sx={{ flexGrow: 1 }}>
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#6366f1" stopOpacity={0.1}/>
                      <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f3f4f6" />
                  <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: '#9ca3af', fontSize: 12}} dy={10} />
                  <YAxis axisLine={false} tickLine={false} tick={{fill: '#9ca3af', fontSize: 12}} dx={-10} />
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
          <Paper sx={{ p: 4, borderRadius: 4, height: '100%' }}>
            <Typography variant="h6" sx={{ fontWeight: 700, mb: 4 }}>
              Response Channels
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
              {[
                { key: 'phone', label: 'Phone Calls', icon: Phone, color: '#10b981' },
                { key: 'web', label: 'Web Survey', icon: Globe, color: '#6366f1' },
                { key: 'qr', label: 'QR Code', icon: QrCode, color: '#8b5cf6' }
              ].map((channel) => {
                const count = channelCounts[channel.key] ?? channelCounts.phone ?? 0;
                const totalC = totalResponses || 1;
                const pct = totalResponses > 0 ? ((count / totalResponses) * 100).toFixed(1) : '0.0';
                return (
                  <Box key={channel.label} sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', p: 2, borderRadius: 3, bgcolor: '#f9fafb' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Box sx={{ p: 1, borderRadius: 2, bgcolor: `${channel.color}15`, color: channel.color }}>
                        <channel.icon size={20} />
                      </Box>
                      <Box>
                        <Typography variant="body1" sx={{ fontWeight: 600 }}>{channel.label}</Typography>
                        <Typography variant="caption" sx={{ color: '#6b7280' }}>{count} responses</Typography>
                      </Box>
                    </Box>
                    <Typography variant="body1" sx={{ fontWeight: 700 }}>{pct}%</Typography>
                  </Box>
                );
              })}
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Analytics;
