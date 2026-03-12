import React, { useState, useEffect } from 'react';
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
  Snackbar,
  Alert,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Plus,
  Search,
  Star,
  PhoneCall,
  Users,
  AlertCircle,
  BarChart3,
  Eye,
  Edit,
  Copy,
  Trash2,
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import StatCardNew from '../components/StatCardNew';
import { useDashboard } from '../hooks/Surveys/useSurveyTable';
import { useAuth } from '../context/AuthContext';

const statusColors = {
  Active: { bg: '#ecfdf5', color: '#059669', label: 'Active' },
  Completed: { bg: '#ecfdf5', color: '#059669', label: 'Completed' },
  'In-Progress': { bg: '#eef2ff', color: '#4f46e5', label: 'In-Progress' },
  Draft: { bg: '#fff7ed', color: '#d97706', label: 'Draft' },
  Pending: { bg: '#fefce8', color: '#ca8a04', label: 'Pending' },
};

const DashboardNew = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const {
    statsData,
    tableData,
    statsLoading,
    tableLoading,
    statsError,
    tableError,
    globalLoading,
  } = useDashboard();

  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });

  // Filter surveys based on search and filter
  const filteredSurveys = (tableData || []).filter(survey => {
    const matchesSearch = searchTerm === '' ||
      (survey.name || survey.Name || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (survey.recipient || survey.Recipient || '').toLowerCase().includes(searchTerm.toLowerCase());

    const status = survey.status || survey.Status || '';
    const matchesFilter = statusFilter === 'all' || status.toLowerCase() === statusFilter.toLowerCase();

    return matchesSearch && matchesFilter;
  });

  // Calculate stats from the statsData returned by useDashboard hook
  const totalSurveys = statsData?.Total_Surveys ?? statsData?.totalSurveys ?? tableData?.length ?? 0;
  const activeSurveys = statsData?.Active_Surveys ?? statsData?.activeSurveys ?? 0;
  const completedSurveys = statsData?.Total_Completed_Surveys ?? statsData?.completedSurveys ?? 0;
  const totalTemplates = statsData?.Total_Templates ?? statsData?.totalTemplates ?? 0;
  const publishedTemplates = statsData?.Published_Templates ?? statsData?.publishedTemplates ?? 0;

  if (globalLoading) {
    return (
      <Box sx={{ flexGrow: 1, display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '70vh' }}>
        <CircularProgress size={60} sx={{ color: '#6366f1' }} />
      </Box>
    );
  }

  return (
    <Box sx={{ p: { xs: 2, md: 4 }, maxWidth: 1400, mx: 'auto', width: '100%' }}>
      {/* Header Section */}
      <Box sx={{ mb: 4 }}>
        <Typography
          variant="h3"
          sx={{
            fontWeight: 800,
            color: '#1f2937',
            mb: 1,
            fontSize: { xs: '2rem', md: '2.5rem' }
          }}
        >
          Dashboard
        </Typography>
        <Typography variant="h6" sx={{ color: '#6b7280', fontWeight: 400 }}>
          Welcome back{user?.username ? `, ${user.username}` : ''} — Survey Management Overview
        </Typography>
      </Box>

      {/* Stats Grid */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={2.4}>
          <StatCardNew
            title="TOTAL SURVEYS"
            value={totalSurveys}
            subValue={`${activeSurveys} active`}
            icon={BarChart3}
            color="#6366f1"
            trend={totalSurveys > 0 ? 12 : 0}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <StatCardNew
            title="ACTIVE SURVEYS"
            value={activeSurveys}
            subValue={`${completedSurveys} completed`}
            icon={Users}
            color="#10b981"
            trend={activeSurveys > 0 ? 5 : 0}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <StatCardNew
            title="TEMPLATES"
            value={totalTemplates}
            subValue={`${publishedTemplates} published`}
            icon={Star}
            color="#f59e0b"
            trend={totalTemplates > 0 ? 8 : 0}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <StatCardNew
            title="COMPLETION RATE"
            value={totalSurveys > 0 ? Math.round((completedSurveys / totalSurveys) * 100) + '%' : '0%'}
            subValue={`${completedSurveys} completed`}
            icon={PhoneCall}
            color="#8b5cf6"
            trend={completedSurveys > 0 ? 15 : 0}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <StatCardNew
            title="FLAGGED"
            value="0"
            subValue="No issues"
            icon={AlertCircle}
            color="#ef4444"
            trend={0}
          />
        </Grid>
      </Grid>

      {/* Quick Actions */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={8}>
          <Card sx={{ borderRadius: '12px', border: '1px solid #e5e7eb' }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ fontWeight: 700, mb: 3, color: '#1f2937' }}>
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
                      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                      textTransform: 'none',
                      fontWeight: 600,
                      borderRadius: '8px',
                      boxShadow: '0 4px 14px 0 rgba(79, 70, 229, 0.39)',
                      '&:hover': {
                        transform: 'translateY(-2px)',
                        boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
                      }
                    }}
                  >
                    Launch Survey
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
                      borderColor: '#6366f1',
                      color: '#6366f1',
                      textTransform: 'none',
                      fontWeight: 600,
                      borderRadius: '8px',
                      '&:hover': {
                        borderColor: '#4f46e5',
                        bgcolor: '#f3f4f6'
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
                      color: '#374151',
                      textTransform: 'none',
                      fontWeight: 600,
                      borderRadius: '8px',
                      '&:hover': {
                        bgcolor: '#f9fafb'
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
          <Card sx={{ borderRadius: '12px', border: '1px solid #e5e7eb' }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ fontWeight: 700, mb: 2, color: '#1f2937' }}>
                Recent Activity
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: '#10b981' }} />
                  <Typography variant="body2" sx={{ color: '#6b7280' }}>
                    {totalSurveys} surveys loaded
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: '#6366f1' }} />
                  <Typography variant="body2" sx={{ color: '#6b7280' }}>
                    {totalTemplates} templates available
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: '#f59e0b' }} />
                  <Typography variant="body2" sx={{ color: '#6b7280' }}>
                    Backend connected
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Search and Filters */}
      <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap', alignItems: 'center' }}>
        <Typography variant="h6" sx={{ fontWeight: 700, color: '#1f2937', mr: 'auto' }}>
          Recent Surveys
        </Typography>
        <TextField
          placeholder="Search surveys..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          size="small"
          sx={{
            minWidth: 240,
            '& .MuiOutlinedInput-root': {
              bgcolor: '#fff',
              borderRadius: '8px',
              '& fieldset': { borderColor: '#e5e7eb' }
            }
          }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <Search size={18} color="#9ca3af" />
              </InputAdornment>
            ),
          }}
        />
        <FormControl size="small" sx={{ minWidth: 140, bgcolor: '#fff', borderRadius: '8px' }}>
          <Select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            sx={{
              borderRadius: '8px',
              '& .MuiOutlinedInput-notchedOutline': { borderColor: '#e5e7eb' }
            }}
          >
            <MenuItem value="all">All Statuses</MenuItem>
            <MenuItem value="active">Active</MenuItem>
            <MenuItem value="draft">Draft</MenuItem>
            <MenuItem value="completed">Completed</MenuItem>
          </Select>
        </FormControl>
      </Box>

      {/* Survey Table */}
      <Card sx={{ borderRadius: '12px', border: '1px solid #e5e7eb', overflow: 'hidden' }}>
        {tableLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
            <CircularProgress size={48} sx={{ color: '#6366f1' }} />
          </Box>
        ) : tableError ? (
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <AlertCircle size={48} color="#ef4444" style={{ marginBottom: 16 }} />
            <Typography variant="h6" sx={{ mb: 1, color: '#1f2937' }}>Error Loading Surveys</Typography>
            <Typography variant="body2" sx={{ color: '#6b7280' }}>{tableError}</Typography>
          </Box>
        ) : filteredSurveys.length === 0 ? (
          <Box sx={{ p: 6, textAlign: 'center' }}>
            <Box sx={{ bgcolor: '#eef2ff', p: 3, borderRadius: '50%', color: '#6366f1', mb: 3, display: 'inline-flex' }}>
              <BarChart3 size={48} />
            </Box>
            <Typography variant="h5" sx={{ fontWeight: 700, mb: 2, color: '#1f2937' }}>
              {searchTerm || statusFilter !== 'all' ? 'No matching surveys found' : 'No surveys yet'}
            </Typography>
            <Typography variant="body1" sx={{ color: '#6b7280', mb: 4 }}>
              {searchTerm || statusFilter !== 'all'
                ? 'Try adjusting your search or filters'
                : 'Create your first survey to start collecting feedback.'}
            </Typography>
            {!searchTerm && statusFilter === 'all' && (
              <Button
                variant="contained"
                startIcon={<Plus size={20} />}
                onClick={() => navigate('/surveys/launch')}
                sx={{
                  py: 2, px: 4, borderRadius: '8px',
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  textTransform: 'none', fontWeight: 600,
                  boxShadow: '0 4px 14px 0 rgba(79, 70, 229, 0.39)',
                }}
              >
                Create Your First Survey
              </Button>
            )}
          </Box>
        ) : (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow sx={{ bgcolor: '#f9fafb' }}>
                  <TableCell sx={{ fontWeight: 600, color: '#374151', fontSize: '13px' }}>SURVEY NAME</TableCell>
                  <TableCell sx={{ fontWeight: 600, color: '#374151', fontSize: '13px' }}>RECIPIENT</TableCell>
                  <TableCell sx={{ fontWeight: 600, color: '#374151', fontSize: '13px' }}>STATUS</TableCell>
                  <TableCell sx={{ fontWeight: 600, color: '#374151', fontSize: '13px' }}>DATE</TableCell>
                  <TableCell sx={{ fontWeight: 600, color: '#374151', fontSize: '13px' }} align="right">ACTIONS</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredSurveys.slice(0, 15).map((survey, idx) => {
                  const name = survey.name || survey.Name || 'Untitled';
                  const recipient = survey.recipient || survey.Recipient || '—';
                  const status = survey.status || survey.Status || 'Draft';
                  const date = survey.formattedLaunchDate || survey.LaunchDate || survey.date || survey.CreatedAt || survey.created_at || '';
                  const surveyId = survey.surveyId || survey.SurveyId || survey.id || '';
                  const statusStyle = statusColors[status] || statusColors.Draft;

                  return (
                    <TableRow
                      key={surveyId || idx}
                      hover
                      sx={{
                        cursor: 'pointer',
                        '&:hover': { bgcolor: '#f9fafb' },
                        '&:last-child td': { borderBottom: 0 }
                      }}
                      onClick={() => {
                        if (surveyId) navigate(`/surveys/status/${surveyId}`, { state: { surveyData: survey } });
                      }}
                    >
                      <TableCell>
                        <Typography variant="body2" sx={{ fontWeight: 600, color: '#1f2937' }}>
                          {name}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" sx={{ color: '#6b7280' }}>
                          {recipient}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={statusStyle.label}
                          size="small"
                          sx={{
                            bgcolor: statusStyle.bg,
                            color: statusStyle.color,
                            fontWeight: 600,
                            fontSize: '12px',
                            borderRadius: '6px',
                            height: 24,
                          }}
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="caption" sx={{ color: '#9ca3af' }}>
                          {date ? (typeof date === 'string' && date.includes(',') ? date : new Date(date).toLocaleDateString()) : '—'}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Box sx={{ display: 'flex', gap: 0.5, justifyContent: 'flex-end' }}>
                          <Tooltip title="View">
                            <IconButton
                              size="small"
                              onClick={(e) => { e.stopPropagation(); if (surveyId) navigate(`/surveys/status/${surveyId}`, { state: { surveyData: survey } }); }}
                              sx={{ color: '#6b7280', '&:hover': { color: '#6366f1', bgcolor: '#eef2ff' } }}
                            >
                              <Eye size={16} />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Edit">
                            <IconButton
                              size="small"
                              onClick={(e) => { e.stopPropagation(); if (surveyId) navigate(`/surveys/edit/${surveyId}`, { state: { surveyData: survey } }); }}
                              sx={{ color: '#6b7280', '&:hover': { color: '#f59e0b', bgcolor: '#fff7ed' } }}
                            >
                              <Edit size={16} />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
            {filteredSurveys.length > 15 && (
              <Box sx={{ p: 2, textAlign: 'center', borderTop: '1px solid #e5e7eb' }}>
                <Button
                  onClick={() => navigate('/surveys/manage')}
                  sx={{ textTransform: 'none', color: '#6366f1', fontWeight: 600 }}
                >
                  View All {filteredSurveys.length} Surveys →
                </Button>
              </Box>
            )}
          </TableContainer>
        )}
      </Card>

      {/* Notification Snackbar */}
      <Snackbar
        open={notification.open}
        autoHideDuration={6000}
        onClose={() => setNotification({ ...notification, open: false })}
        anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
      >
        <Alert
          onClose={() => setNotification({ ...notification, open: false })}
          severity={notification.severity}
          sx={{ width: '100%' }}
        >
          {notification.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default DashboardNew;
