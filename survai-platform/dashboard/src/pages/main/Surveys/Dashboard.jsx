import React, { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  TextField,
  MenuItem,
  Select,
  FormControl,
  InputAdornment,
  Grid,
  CircularProgress,
  Card,
  CardContent,
  Alert
} from '@mui/material';
import {
  Plus,
  Search,
  Star,
  PhoneCall,
  Users,
  AlertCircle,
  BarChart3,
  TrendingUp,
  TrendingDown,
  Calendar,
  Clock
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import StatCard from '../../../components/StatCard';
import { useDashboard } from '../../../hooks/Surveys/useSurveyTable';
import { filterData } from '../../../utils/Surveys/surveyTableHelpers';

const Dashboard = () => {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const {
    statsData,
    tableData,
    statsLoading,
    tableLoading,
    statsError,
    tableError,
    refetchStats,
    refetchTable,
  } = useDashboard();

  const loading = statsLoading || tableLoading;
  const surveys = filterData(
    statusFilter === 'all'
      ? tableData
      : tableData.filter((s) => (s.Status || '').toLowerCase() === statusFilter.toLowerCase()),
    searchTerm
  );

  const total = statsData?.Total_Surveys ?? 0;
  const completed = statsData?.Total_Completed_Surveys ?? 0;
  const today = statsData?.Total_Completed_Surveys_Today ?? 0;
  const avgCsat = statsData?.AverageCSAT;
  const completionPct = total > 0 ? Math.round((completed / total) * 100) : null;

  return (
    <Box sx={{
      p: { xs: 3, md: 4 },
      maxWidth: 1400,
      mx: 'auto',
      width: '100%',
      minHeight: '100%',
      background: 'linear-gradient(180deg, rgba(249, 250, 251, 0.98) 0%, rgba(243, 244, 246, 0.95) 100%)',
    }}>
      {/* Header Section: Rider Voice + Create Survey */}
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 2 }}>
        <Box>
          <Typography
            variant="h3"
            sx={{
              fontWeight: 800,
              color: 'var(--color-gray-900)',
              mb: 1,
              fontSize: { xs: '2rem', md: '2.5rem' }
            }}
          >
            Rider Voice
          </Typography>
          <Typography variant="h6" sx={{ color: 'var(--color-gray-600)', fontWeight: 400 }}>
            Transigo — Survey Management Dashboard
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<Plus size={18} />}
          onClick={() => navigate('/surveys/launch')}
          sx={{
            py: 1.5,
            px: 3,
            borderRadius: 'var(--radius-lg)',
            background: 'var(--gradient-primary, linear-gradient(135deg, #7B61FF 0%, #5b21b6 100%))',
            textTransform: 'none',
            fontWeight: 600,
            boxShadow: 'var(--shadow-button, 0 4px 14px rgba(123, 97, 255, 0.4))',
            '&:hover': { transform: 'translateY(-2px)', boxShadow: 'var(--shadow-lg)' }
          }}
        >
          + Create Survey
        </Button>
      </Box>

      {/* Stats Grid - wired to API */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={2.4}>
          <StatCard
            title="AVG. SATISFACTION"
            value={avgCsat != null && avgCsat > 0 ? String(Number(avgCsat).toFixed(1)) : 'N/A'}
            subValue={avgCsat > 0 ? `Based on ${completed} responses` : ''}
            icon={Star}
            color="#f59e0b"
            gradient="linear-gradient(135deg, #f59e0b 0%, #d97706 100%)"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <StatCard
            title="CALL COMPLETION"
            value={completionPct != null ? `${completionPct}%` : 'N/A'}
            subValue={completionPct != null ? `${completed} of ${total} completed` : ''}
            icon={PhoneCall}
            color="#10b981"
            gradient="linear-gradient(135deg, #10b981 0%, #059669 100%)"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <StatCard
            title="CALLS THIS WEEK"
            value={String(total)}
            subValue={`(${today} today)`}
            icon={Users}
            color="#6366f1"
            gradient="linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <StatCard
            title="FLAGGED RESPONSES"
            value="0"
            subValue="None pending"
            icon={AlertCircle}
            color="#ef4444"
            gradient="linear-gradient(135deg, #ef4444 0%, #dc2626 100%)"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <StatCard
            title="RESPONSE CHANNELS"
            value={String(completed)}
            subValue={completed === 0 ? 'No responses yet' : 'total responses'}
            icon={BarChart3}
            color="#8b5cf6"
            gradient="linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)"
          />
        </Grid>
      </Grid>

      {(statsError || tableError) && (
        <Alert severity="warning" sx={{ mb: 2 }} onClose={() => {}}>
          {statsError || tableError} You can still create surveys.
        </Alert>
      )}

      {/* Quick Actions */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={8}>
          <Card sx={{ borderRadius: 'var(--radius-xl)', border: '1px solid var(--color-gray-200)', boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.06), 0 1px 2px -1px rgb(0 0 0 / 0.06)' }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ fontWeight: 700, mb: 3, color: 'var(--color-gray-900)' }}>
                Quick Actions
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6} md={4}>
                  <Button
                    variant="contained"
                    startIcon={<Plus size={18} />}
                    onClick={() => navigate('/surveys/launch')}
                    sx={{
                      width: '100%',
                      py: 2,
                      background: 'var(--gradient-primary)',
                      textTransform: 'none',
                      fontWeight: 600,
                      borderRadius: 'var(--radius-lg)',
                      boxShadow: 'var(--shadow-button)',
                      '&:hover': {
                        transform: 'translateY(-2px)',
                        boxShadow: 'var(--shadow-lg)'
                      }
                    }}
                  >
                    Create Survey
                  </Button>
                </Grid>
                <Grid item xs={12} sm={6} md={4}>
                  <Button
                    variant="outlined"
                    startIcon={<Plus size={18} />}
                    onClick={() => navigate('/templates/create')}
                    sx={{
                      width: '100%',
                      py: 2,
                      borderColor: 'var(--color-primary-500)',
                      color: 'var(--color-primary-600)',
                      textTransform: 'none',
                      fontWeight: 600,
                      borderRadius: 'var(--radius-lg)',
                      '&:hover': {
                        borderColor: 'var(--color-primary-600)',
                        bgcolor: 'var(--color-primary-50)'
                      }
                    }}
                  >
                    Create Template
                  </Button>
                </Grid>
                <Grid item xs={12} sm={6} md={4}>
                  <Button
                    variant="text"
                    startIcon={<BarChart3 size={18} />}
                    onClick={() => navigate('/analytics')}
                    sx={{
                      width: '100%',
                      py: 2,
                      color: 'var(--color-gray-700)',
                      textTransform: 'none',
                      fontWeight: 600,
                      borderRadius: 'var(--radius-lg)',
                      '&:hover': {
                        bgcolor: 'var(--color-gray-50)'
                      }
                    }}
                  >
                    View Analytics
                  </Button>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card sx={{ borderRadius: 'var(--radius-xl)', border: '1px solid var(--color-gray-200)', boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.06), 0 1px 2px -1px rgb(0 0 0 / 0.06)' }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ fontWeight: 700, mb: 2, color: 'var(--color-gray-900)' }}>
                Recent Activity
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Box sx={{ 
                    width: 8, 
                    height: 8, 
                    borderRadius: '50%', 
                    bgcolor: 'var(--color-success-500)' 
                  }} />
                  <Typography variant="body2" sx={{ color: 'var(--color-gray-600)' }}>
                    New survey completed
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Box sx={{ 
                    width: 8, 
                    height: 8, 
                    borderRadius: '50%', 
                    bgcolor: 'var(--color-primary-500)' 
                  }} />
                  <Typography variant="body2" sx={{ color: 'var(--color-gray-600)' }}>
                    Template published
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Box sx={{ 
                    width: 8, 
                    height: 8, 
                    borderRadius: '50%', 
                    bgcolor: 'var(--color-warning-500)' 
                  }} />
                  <Typography variant="body2" sx={{ color: 'var(--color-gray-600)' }}>
                    3 responses flagged
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Search and Filters */}
      <Box sx={{ display: 'flex', gap: 2, mb: 4, flexWrap: 'wrap' }}>
        <TextField
          placeholder="Search surveys..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          sx={{ 
            flexGrow: 1, 
            maxWidth: 400,
            '& .MuiOutlinedInput-root': {
              bgcolor: '#fff',
              borderRadius: 'var(--radius-lg)',
              '& fieldset': {
                borderColor: 'var(--color-gray-200)'
              }
            }
          }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <Search size={18} color="var(--color-gray-400)" />
              </InputAdornment>
            ),
          }}
        />
        <FormControl sx={{ minWidth: 160, bgcolor: '#fff', borderRadius: 'var(--radius-lg)' }}>
          <Select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            displayEmpty
            sx={{
              borderRadius: 'var(--radius-lg)',
              '& .MuiOutlinedInput-notchedOutline': {
                borderColor: 'var(--color-gray-200)'
              }
            }}
          >
            <MenuItem value="all">All Statuses</MenuItem>
            <MenuItem value="active">Active</MenuItem>
            <MenuItem value="draft">Draft</MenuItem>
            <MenuItem value="completed">Completed</MenuItem>
          </Select>
        </FormControl>
      </Box>

      {/* Content Area */}
      <Card
        sx={{
          borderRadius: 'var(--radius-xl)',
          border: '1px solid var(--color-gray-200)',
          boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.06), 0 1px 2px -1px rgb(0 0 0 / 0.06)',
          p: 8,
          textAlign: 'center',
          minHeight: 400,
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          bgcolor: '#fff'
        }}
      >
        {loading ? (
          <CircularProgress color="primary" />
        ) : surveys.length === 0 ? (
          <>
            <Box sx={{
              bgcolor: 'var(--color-primary-50)',
              p: 3,
              borderRadius: 'var(--radius-xl)',
              color: 'var(--color-primary-600)',
              mb: 3
            }}>
              <BarChart3 size={48} />
            </Box>
            <Typography variant="h5" sx={{ fontWeight: 700, mb: 2, color: 'var(--color-gray-900)' }}>
              No surveys yet
            </Typography>
            <Typography variant="body1" sx={{ color: 'var(--color-gray-600)', mb: 4 }}>
              Create your first survey to start collecting rider feedback.
            </Typography>
            <Button
              variant="contained"
              startIcon={<Plus size={20} />}
              onClick={() => navigate('/surveys/launch')}
              sx={{
                py: 2,
                px: 4,
                borderRadius: 'var(--radius-lg)',
                background: 'var(--gradient-primary)',
                textTransform: 'none',
                fontWeight: 600,
                boxShadow: 'var(--shadow-button)',
                '&:hover': {
                  transform: 'translateY(-2px)',
                  boxShadow: 'var(--shadow-lg)'
                }
              }}
            >
              Create Your First Survey
            </Button>
          </>
        ) : (
          <Box sx={{ textAlign: 'center' }}>
            <Typography variant="h6" sx={{ mb: 2, color: 'var(--color-gray-900)' }}>
              Found {surveys.length} survey{surveys.length !== 1 ? 's' : ''}
            </Typography>
            <Typography variant="body2" sx={{ color: 'var(--color-gray-600)', mb: 3 }}>
              View and manage all surveys, send links, or clone.
            </Typography>
            <Button
              variant="contained"
              onClick={() => navigate('/surveys/manage')}
              sx={{
                py: 1.5,
                px: 3,
                borderRadius: 'var(--radius-lg)',
                background: 'var(--gradient-primary, linear-gradient(135deg, #7B61FF 0%, #5b21b6 100%))',
                textTransform: 'none',
                fontWeight: 600
              }}
            >
              Manage Surveys
            </Button>
          </Box>
        )}
      </Card>
    </Box>
  );
};

export default Dashboard;