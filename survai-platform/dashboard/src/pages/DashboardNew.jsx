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
  Alert
} from '@mui/material';
import {
  Plus,
  Search,
  Star,
  PhoneCall,
  Users,
  AlertCircle,
  BarChart3
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import StatCardNew from '../components/StatCardNew';
import SidebarNew from '../components/SidebarNew';
import TopNavNew from '../components/TopNavNew';
import { surveyAPI, analyticsAPI } from '../utils/surveyAPI';

const DashboardNew = () => {
  const navigate = useNavigate();
  const [surveys, setSurveys] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });

  // Fetch data from backend using the working API
  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Fetch surveys using the working API
      const surveysData = await surveyAPI.getSurveys();
      
      // Fetch templates using the working API
      const templatesData = await surveyAPI.getTemplates();
      
      // Fetch analytics data
      const analyticsData = await analyticsAPI.getSummary();
      
      setSurveys(surveysData || []);
      setTemplates(templatesData || []);
      
      console.log('Surveys loaded:', surveysData?.length || 0);
      console.log('Templates loaded:', templatesData?.length || 0);
      console.log('Analytics loaded:', analyticsData);
      
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError(err.message);
      // Set empty data as fallback
      setSurveys([]);
      setTemplates([]);
    } finally {
      setLoading(false);
    }
  };

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  // Create a new survey
  const handleCreateSurvey = async () => {
    try {
      const surveyData = {
        recipient: 'New User',
        riderName: 'New Rider',
        biodata: 'Survey created via dashboard',
        tenantId: 'itcurves',
        phone: '+15551234567',
        bilingual: true
      };
      
      const result = await surveyAPI.createSurvey(surveyData);
      
      setNotification({
        open: true,
        message: `Survey created successfully! ID: ${result.SurveyId}`,
        severity: 'success'
      });
      
      // Refresh data
      await fetchDashboardData();
      
      // Navigate to surveys page
      navigate('/surveys/manage');
      
    } catch (err) {
      console.error('Error creating survey:', err);
      setNotification({
        open: true,
        message: `Failed to create survey: ${err.message}`,
        severity: 'error'
      });
    }
  };

  // Create a new template
  const handleCreateTemplate = async () => {
    try {
      const templateData = {
        templateName: `Template_${Date.now()}`,
        status: 'Draft',
        description: 'Template created via dashboard',
        category: 'General',
        questions: [
          {
            text: 'How was your experience?',
            type: 'rating',
            required: true,
            ord: 1
          }
        ]
      };
      
      const result = await surveyAPI.createTemplate(templateData);
      
      setNotification({
        open: true,
        message: `Template created successfully!`,
        severity: 'success'
      });
      
      // Refresh data
      await fetchDashboardData();
      
      // Navigate to templates page
      navigate('/templates/manage');
      
    } catch (err) {
      console.error('Error creating template:', err);
      setNotification({
        open: true,
        message: `Failed to create template: ${err.message}`,
        severity: 'error'
      });
    }
  };

  // Filter surveys based on search and filter
  const filteredSurveys = surveys.filter(survey => {
    const matchesSearch = searchTerm === '' || 
      survey.Name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      survey.Recipient?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesFilter = statusFilter === 'all' || 
      (statusFilter === 'active' && survey.Status === 'Active') ||
      (statusFilter === 'completed' && survey.Status === 'Completed') ||
      (statusFilter === 'draft' && survey.Status === 'Draft');
    
    return matchesSearch && matchesFilter;
  });

  // Calculate stats from real data
  const stats = {
    totalSurveys: surveys.length,
    activeSurveys: surveys.filter(s => s.Status === 'Active').length,
    completedSurveys: surveys.filter(s => s.Status === 'Completed').length,
    totalTemplates: templates.length,
    publishedTemplates: templates.filter(t => t.Status === 'Published').length
  };

  return (
    <Box sx={{ display: 'flex', height: '100vh', bgcolor: '#f9fafb' }}>
      {/* Modern Sidebar */}
      <SidebarNew 
        isOpen={sidebarOpen} 
        onClose={() => setSidebarOpen(false)}
        isMobile={false}
      />
      
      {/* Main Content */}
      <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        {/* Top Navigation */}
        <TopNavNew onSidebarToggle={toggleSidebar} sidebarOpen={sidebarOpen} />
        
        {/* Dashboard Content */}
        <Box sx={{ 
          flex: 1, 
          overflowY: 'auto', 
          p: { xs: 3, md: 4 }, 
          maxWidth: 1400, 
          mx: 'auto',
          width: '100%'
        }}>
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
              Rider Voice
            </Typography>
            <Typography variant="h6" sx={{ color: '#6b7280', fontWeight: 400 }}>
              Transigo — Survey Management Dashboard
            </Typography>
          </Box>

          {/* Stats Grid with Real Data */}
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} sm={6} md={2.4}>
              <StatCardNew
                title="TOTAL SURVEYS"
                value={stats.totalSurveys}
                subValue={`${stats.activeSurveys} active`}
                icon={BarChart3}
                color="#6366f1"
                trend={stats.totalSurveys > 0 ? 12 : 0}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={2.4}>
              <StatCardNew
                title="ACTIVE SURVEYS"
                value={stats.activeSurveys}
                subValue={`${stats.completedSurveys} completed`}
                icon={Users}
                color="#10b981"
                trend={stats.activeSurveys > 0 ? 5 : 0}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={2.4}>
              <StatCardNew
                title="TEMPLATES"
                value={stats.totalTemplates}
                subValue={`${stats.publishedTemplates} published`}
                icon={Star}
                color="#f59e0b"
                trend={stats.totalTemplates > 0 ? 8 : 0}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={2.4}>
              <StatCardNew
                title="COMPLETION RATE"
                value={stats.totalSurveys > 0 ? Math.round((stats.completedSurveys / stats.totalSurveys) * 100) + '%' : '0%'}
                subValue={`${stats.completedSurveys} completed`}
                icon={PhoneCall}
                color="#8b5cf6"
                trend={stats.completedSurveys > 0 ? 15 : 0}
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
                        onClick={handleCreateSurvey}
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
                        Create Survey
                      </Button>
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                      <Button
                        variant="outlined"
                        startIcon={<Plus size={18} />}
                        onClick={handleCreateTemplate}
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
                      <Box sx={{ 
                        width: 8, 
                        height: 8, 
                        borderRadius: '50%', 
                        bgcolor: '#10b981' 
                      }} />
                      <Typography variant="body2" sx={{ color: '#6b7280' }}>
                        {stats.totalSurveys} surveys loaded
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Box sx={{ 
                        width: 8, 
                        height: 8, 
                        borderRadius: '50%', 
                        bgcolor: '#6366f1' 
                      }} />
                      <Typography variant="body2" sx={{ color: '#6b7280' }}>
                        {stats.totalTemplates} templates available
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Box sx={{ 
                        width: 8, 
                        height: 8, 
                        borderRadius: '50%', 
                        bgcolor: '#f59e0b' 
                      }} />
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
                  borderRadius: '8px',
                  '& fieldset': {
                    borderColor: '#e5e7eb'
                  }
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
            <FormControl sx={{ minWidth: 160, bgcolor: '#fff', borderRadius: '8px' }}>
              <Select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                displayEmpty
                sx={{
                  borderRadius: '8px',
                  '& .MuiOutlinedInput-notchedOutline': {
                    borderColor: '#e5e7eb'
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
              borderRadius: '12px',
              border: '1px solid #e5e7eb',
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
              <>
                <CircularProgress color="primary" sx={{ mb: 2 }} />
                <Typography variant="body1" sx={{ color: '#6b7280' }}>
                  Loading dashboard data...
                </Typography>
              </>
            ) : error ? (
              <>
                <Box sx={{
                  bgcolor: '#fef2f2',
                  p: 3,
                  borderRadius: '12px',
                  color: '#ef4444',
                  mb: 3
                }}>
                  <AlertCircle size={48} />
                </Box>
                <Typography variant="h5" sx={{ fontWeight: 700, mb: 2, color: '#1f2937' }}>
                  Error Loading Data
                </Typography>
                <Typography variant="body1" sx={{ color: '#6b7280', mb: 4 }}>
                  {error}
                </Typography>
                <Button
                  variant="contained"
                  onClick={fetchDashboardData}
                  sx={{
                    py: 2,
                    px: 4,
                    borderRadius: '8px',
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    textTransform: 'none',
                    fontWeight: 600,
                    boxShadow: '0 4px 14px 0 rgba(79, 70, 229, 0.39)',
                  }}
                >
                  Retry
                </Button>
              </>
            ) : filteredSurveys.length === 0 ? (
              <>
                <Box sx={{
                  bgcolor: '#eef2ff',
                  p: 3,
                  borderRadius: '12px',
                  color: '#6366f1',
                  mb: 3
                }}>
                  <BarChart3 size={48} />
                </Box>
                <Typography variant="h5" sx={{ fontWeight: 700, mb: 2, color: '#1f2937' }}>
                  {searchTerm || statusFilter !== 'all' ? 'No matching surveys found' : 'No surveys yet'}
                </Typography>
                <Typography variant="body1" sx={{ color: '#6b7280', mb: 4 }}>
                  {searchTerm || statusFilter !== 'all' 
                    ? 'Try adjusting your search or filters'
                    : 'Create your first survey to start collecting rider feedback.'
                  }
                </Typography>
                {!searchTerm && statusFilter === 'all' && (
                  <Button
                    variant="contained"
                    startIcon={<Plus size={20} />}
                    onClick={() => navigate('/surveys/launch')}
                    sx={{
                      py: 2,
                      px: 4,
                      borderRadius: '8px',
                      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                      textTransform: 'none',
                      fontWeight: 600,
                      boxShadow: '0 4px 14px 0 rgba(79, 70, 229, 0.39)',
                      '&:hover': {
                        transform: 'translateY(-2px)',
                        boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
                      }
                    }}
                  >
                    Create Your First Survey
                  </Button>
                )}
              </>
            ) : (
              <Box sx={{ width: '100%' }}>
                <Typography variant="h6" sx={{ mb: 2, color: '#1f2937' }}>
                  Found {filteredSurveys.length} surveys
                </Typography>
                <Typography variant="body2" sx={{ color: '#6b7280' }}>
                  Survey list implementation coming soon...
                </Typography>
                {/* Debug: Show first few surveys */}
                <Box sx={{ mt: 2, p: 2, bgcolor: '#f9fafb', borderRadius: '8px', textAlign: 'left' }}>
                  <Typography variant="subtitle2" sx={{ mb: 1 }}>Sample surveys:</Typography>
                  {filteredSurveys.slice(0, 3).map((survey, index) => (
                    <Typography key={index} variant="caption" sx={{ display: 'block', color: '#6b7280' }}>
                      • {survey.Name} ({survey.Status})
                    </Typography>
                  ))}
                </Box>
              </Box>
            )}
          </Card>
        </Box>
      </Box>

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
