import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  Avatar,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Paper,
  LinearProgress,
  IconButton,
  Menu,
  MenuItem,
} from '@mui/material';
import {
  User,
  Phone,
  Star,
  TrendingUp,
  Users,
  Calendar,
  MoreVertical,
  Plus,
  BarChart3,
  MessageSquare,
  CheckCircle,
  Clock,
  AlertCircle,
  PhoneCall,
  Globe,
  QrCode,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { useDashboard } from '../hooks/Surveys/useSurveyTable';

const FirstTimeLanding = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const { surveys, loading } = useDashboard();
  const [anchorEl, setAnchorEl] = useState(null);

  // Mock data for demonstration
  const stats = {
    totalSurveys: surveys?.length || 156,
    completedSurveys: 89,
    activeUsers: 1240,
    responseRate: 73.5,
    avgRating: 4.2,
    recentGrowth: 12.3,
  };

  const recentActivity = [
    { id: 1, type: 'survey', title: 'Customer Satisfaction Survey', time: '2 hours ago', status: 'completed', responses: 45 },
    { id: 2, type: 'call', title: 'Phone call with John Doe', time: '3 hours ago', status: 'completed', duration: '5:23' },
    { id: 3, type: 'survey', title: 'Product Feedback Survey', time: '5 hours ago', status: 'active', responses: 12 },
    { id: 4, type: 'message', title: 'New message from support', time: '6 hours ago', status: 'unread' },
    { id: 5, type: 'survey', title: 'Employee Engagement Survey', time: '1 day ago', status: 'completed', responses: 78 },
  ];

  const quickActions = [
    { icon: Plus, label: 'Create Survey', color: '#1958F7', route: '/surveys/builder' },
    { icon: PhoneCall, label: 'Make Call', color: '#10B981', route: '/surveys/call' },
    { icon: BarChart3, label: 'View Analytics', color: '#F59E0B', route: '/analytics' },
    { icon: Users, label: 'Manage Users', color: '#8B5CF6', route: '/users' },
  ];

  const getActivityIcon = (type) => {
    switch (type) {
      case 'survey': return <MessageSquare size={20} color="#1958F7" />;
      case 'call': return <Phone size={20} color="#10B981" />;
      case 'message': return <MessageSquare size={20} color="#F59E0B" />;
      default: return <Clock size={20} color="#6B7280" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'success';
      case 'active': return 'primary';
      case 'unread': return 'warning';
      default: return 'default';
    }
  };

  const handleMenuClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  return (
    <Box sx={{ 
      p: 3, 
      maxWidth: '1400px', 
      mx: 'auto',
      backgroundColor: '#F8FAFC',
      minHeight: '100vh'
    }}>
      {/* Header Section */}
      <Box sx={{ mb: 4 }}>
        <Grid container spacing={3} alignItems="center">
          <Grid item xs={12} md={8}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 3 }}>
              <Avatar sx={{ width: 64, height: 64, bgcolor: '#1958F7' }}>
                <User size={32} />
              </Avatar>
              <Box>
                <Typography variant="h4" sx={{ fontWeight: 600, color: '#1F2937', mb: 0.5 }}>
                  Welcome back, {user?.name || 'User'}!
                </Typography>
                <Typography variant="body1" sx={{ color: '#6B7280' }}>
                  Here's what's happening with your surveys today.
                </Typography>
              </Box>
            </Box>
          </Grid>
          <Grid item xs={12} md={4} sx={{ textAlign: 'right' }}>
            <IconButton onClick={handleMenuClick}>
              <MoreVertical size={24} />
            </IconButton>
            <Menu
              anchorEl={anchorEl}
              open={Boolean(anchorEl)}
              onClose={handleMenuClose}
            >
              <MenuItem onClick={handleMenuClose}>Profile Settings</MenuItem>
              <MenuItem onClick={handleMenuClose}>Preferences</MenuItem>
              <MenuItem onClick={handleMenuClose}>Help</MenuItem>
            </Menu>
          </Grid>
        </Grid>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ 
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            borderRadius: '16px',
            boxShadow: '0 4px 20px rgba(102, 126, 234, 0.3)'
          }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                <MessageSquare size={24} />
                <TrendingUp size={20} />
              </Box>
              <Typography variant="h4" sx={{ fontWeight: 600, mb: 0.5 }}>
                {stats.totalSurveys}
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>
                Total Surveys
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ 
            background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
            color: 'white',
            borderRadius: '16px',
            boxShadow: '0 4px 20px rgba(240, 147, 251, 0.3)'
          }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                <CheckCircle size={24} />
                <TrendingUp size={20} />
              </Box>
              <Typography variant="h4" sx={{ fontWeight: 600, mb: 0.5 }}>
                {stats.completedSurveys}
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>
                Completed
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ 
            background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
            color: 'white',
            borderRadius: '16px',
            boxShadow: '0 4px 20px rgba(79, 172, 254, 0.3)'
          }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                <Users size={24} />
                <TrendingUp size={20} />
              </Box>
              <Typography variant="h4" sx={{ fontWeight: 600, mb: 0.5 }}>
                {stats.activeUsers}
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>
                Active Users
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ 
            background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
            color: 'white',
            borderRadius: '16px',
            boxShadow: '0 4px 20px rgba(250, 112, 154, 0.3)'
          }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                <Star size={24} />
                <Typography variant="caption" sx={{ opacity: 0.9 }}>
                  +{stats.recentGrowth}%
                </Typography>
              </Box>
              <Typography variant="h4" sx={{ fontWeight: 600, mb: 0.5 }}>
                {stats.responseRate}%
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>
                Response Rate
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Main Content */}
      <Grid container spacing={3}>
        {/* Quick Actions */}
        <Grid item xs={12} md={4}>
          <Card sx={{ borderRadius: '16px', height: '100%' }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 3, color: '#1F2937' }}>
                Quick Actions
              </Typography>
              <Grid container spacing={2}>
                {quickActions.map((action, index) => (
                  <Grid item xs={6} key={index}>
                    <Paper
                      sx={{
                        p: 2,
                        textAlign: 'center',
                        cursor: 'pointer',
                        transition: 'all 0.3s ease',
                        '&:hover': {
                          transform: 'translateY(-2px)',
                          boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
                        },
                        border: `2px solid ${action.color}20`,
                      }}
                      onClick={() => navigate(action.route)}
                    >
                      <action.icon size={24} style={{ color: action.color, marginBottom: '8px' }} />
                      <Typography variant="body2" sx={{ fontWeight: 500, color: '#374151' }}>
                        {action.label}
                      </Typography>
                    </Paper>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12} md={8}>
          <Card sx={{ borderRadius: '16px', height: '100%' }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6" sx={{ fontWeight: 600, color: '#1F2937' }}>
                  Recent Activity
                </Typography>
                <Button variant="text" size="small" sx={{ color: '#1958F7' }}>
                  View All
                </Button>
              </Box>
              
              <List sx={{ p: 0 }}>
                {recentActivity.map((activity) => (
                  <ListItem key={activity.id} sx={{ px: 0, py: 2 }}>
                    <ListItemIcon sx={{ minWidth: 40 }}>
                      {getActivityIcon(activity.type)}
                    </ListItemIcon>
                    <ListItemText
                      primary={activity.title}
                      secondary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                          <Typography variant="caption" color="#6B7280">
                            {activity.time}
                          </Typography>
                          <Chip
                            label={activity.status}
                            size="small"
                            color={getStatusColor(activity.status)}
                            variant="outlined"
                          />
                          {activity.responses && (
                            <Typography variant="caption" color="#6B7280">
                              {activity.responses} responses
                            </Typography>
                          )}
                        </Box>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Progress Overview */}
        <Grid item xs={12} md={6}>
          <Card sx={{ borderRadius: '16px' }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 3, color: '#1F2937' }}>
                Survey Progress
              </Typography>
              
              <Box sx={{ mb: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2" color="#374151">Customer Satisfaction</Typography>
                  <Typography variant="body2" color="#374151">78%</Typography>
                </Box>
                <LinearProgress variant="determinate" value={78} sx={{ height: 8, borderRadius: 4 }} />
              </Box>
              
              <Box sx={{ mb: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2" color="#374151">Product Feedback</Typography>
                  <Typography variant="body2" color="#374151">45%</Typography>
                </Box>
                <LinearProgress variant="determinate" value={45} sx={{ height: 8, borderRadius: 4 }} />
              </Box>
              
              <Box sx={{ mb: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2" color="#374151">Employee Engagement</Typography>
                  <Typography variant="body2" color="#374151">92%</Typography>
                </Box>
                <LinearProgress variant="determinate" value={92} sx={{ height: 8, borderRadius: 4 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Performance Metrics */}
        <Grid item xs={12} md={6}>
          <Card sx={{ borderRadius: '16px' }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 3, color: '#1F2937' }}>
                Performance Metrics
              </Typography>
              
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Box sx={{ textAlign: 'center', p: 2, bgcolor: '#F3F4F6', borderRadius: '12px' }}>
                    <Typography variant="h5" sx={{ fontWeight: 600, color: '#1958F7', mb: 0.5 }}>
                      4.2
                    </Typography>
                    <Typography variant="caption" color="#6B7280">
                      Average Rating
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box sx={{ textAlign: 'center', p: 2, bgcolor: '#F3F4F6', borderRadius: '12px' }}>
                    <Typography variant="h5" sx={{ fontWeight: 600, color: '#10B981', mb: 0.5 }}>
                      2.3s
                    </Typography>
                    <Typography variant="caption" color="#6B7280">
                      Avg Response Time
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box sx={{ textAlign: 'center', p: 2, bgcolor: '#F3F4F6', borderRadius: '12px' }}>
                    <Typography variant="h5" sx={{ fontWeight: 600, color: '#F59E0B', mb: 0.5 }}>
                      98%
                    </Typography>
                    <Typography variant="caption" color="#6B7280">
                      Uptime
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box sx={{ textAlign: 'center', p: 2, bgcolor: '#F3F4F6', borderRadius: '12px' }}>
                    <Typography variant="h5" sx={{ fontWeight: 600, color: '#8B5CF6', mb: 0.5 }}>
                      24/7
                    </Typography>
                    <Typography variant="caption" color="#6B7280">
                      Support
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default FirstTimeLanding;
