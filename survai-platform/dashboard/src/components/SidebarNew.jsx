import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  Box,
  Typography,
  Button,
  Collapse,
  IconButton,
  Avatar,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText
} from '@mui/material';
import {
  LayoutDashboard,
  FileText,
  Users,
  Settings,
  HelpCircle,
  LogOut,
  Menu,
  X,
  ChevronDown,
  ChevronRight,
  Home,
  BarChart3,
  Phone,
  MessageSquare,
  Calendar,
  TrendingUp,
  Plus
} from 'lucide-react';

const SidebarNew = ({ isOpen, onClose, isMobile = false }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();
  
  const [expandedSections, setExpandedSections] = useState({
    templates: false,
    surveys: false
  });

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const isActive = (path) => location.pathname.startsWith(path);

  const handleNavigation = (path) => {
    navigate(path);
    if (isMobile) {
      onClose();
    }
  };

  const menuItems = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      icon: LayoutDashboard,
      path: '/dashboard',
      color: '#6366f1'
    },
    {
      id: 'templates',
      label: 'Templates',
      icon: FileText,
      path: '/templates',
      color: '#8b5cf6',
      children: [
        { label: 'Create Template', path: '/templates/create' },
        { label: 'Manage Templates', path: '/templates/manage' }
      ]
    },
    {
      id: 'surveys',
      label: 'Surveys',
      icon: Users,
      path: '/surveys',
      color: '#10b981',
      children: [
        { label: 'Launch Survey', path: '/surveys/launch' },
        { label: 'Manage Surveys', path: '/surveys/manage' }
      ]
    }
  ];

  return (
    <Box
      sx={{
        width: isMobile ? '100vw' : 280,
        height: '100vh',
        bgcolor: '#fff',
        borderRight: '1px solid #e5e7eb',
        display: 'flex',
        flexDirection: 'column',
        position: isMobile ? 'fixed' : 'relative',
        left: 0,
        top: 0,
        zIndex: isMobile ? 1400 : 1,
        transform: isMobile && !isOpen ? 'translateX(-100%)' : 'translateX(0)',
        transition: 'transform 0.3s ease',
        boxShadow: isMobile ? '0 10px 15px -3px rgba(0, 0, 0, 0.1)' : 'none'
      }}
    >
      {/* Header */}
      <Box sx={{ p: 3, borderBottom: '1px solid #e5e7eb' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography variant="h6" sx={{ fontWeight: 700, color: '#1f2937' }}>
            SurvAI
          </Typography>
          {isMobile && (
            <IconButton onClick={onClose} size="small">
              <X size={20} />
            </IconButton>
          )}
        </Box>
      </Box>

      {/* User Profile */}
      <Box sx={{ p: 3, borderBottom: '1px solid #e5e7eb' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Avatar
            sx={{
              width: 40,
              height: 40,
              bgcolor: '#6366f1',
              color: '#fff',
              fontWeight: 600
            }}
          >
            {user?.username ? user.username.charAt(0).toUpperCase() : 'U'}
          </Avatar>
          <Box>
            <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#1f2937' }}>
              {user?.username || 'User'}
            </Typography>
            <Typography variant="caption" sx={{ color: '#6b7280' }}>
              {user?.orgName || 'Organization'}
            </Typography>
          </Box>
        </Box>
      </Box>

      {/* Navigation */}
      <Box sx={{ flex: 1, overflowY: 'auto', py: 2 }}>
        {menuItems.map((item) => (
          <Box key={item.id}>
            <Button
              onClick={() => item.children ? toggleSection(item.id) : handleNavigation(item.path)}
              sx={{
                width: '100%',
                justifyContent: 'space-between',
                px: 3,
                py: 2,
                borderRadius: 0,
                textTransform: 'none',
                bgcolor: isActive(item.path) ? `${item.color}15` : 'transparent',
                color: isActive(item.path) ? item.color : '#374151',
                '&:hover': {
                  bgcolor: isActive(item.path) ? `${item.color}25` : '#f9fafb'
                }
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <item.icon size={20} />
                <Typography sx={{ fontWeight: 500, fontSize: '14px' }}>
                  {item.label}
                </Typography>
              </Box>
              {item.children && (
                expandedSections[item.id] ? <ChevronDown size={16} /> : <ChevronRight size={16} />
              )}
            </Button>

            {/* Submenu */}
            {item.children && (
              <Collapse in={expandedSections[item.id]} timeout="auto" unmountOnExit>
                <Box sx={{ pl: 7, pr: 3, py: 1 }}>
                  {item.children.map((child) => (
                    <Button
                      key={child.path}
                      onClick={() => handleNavigation(child.path)}
                      sx={{
                        width: '100%',
                        justifyContent: 'flex-start',
                        py: 1.5,
                        borderRadius: 0,
                        textTransform: 'none',
                        color: isActive(child.path) ? item.color : '#6b7280',
                        fontSize: '13px',
                        '&:hover': {
                          bgcolor: '#f9fafb'
                        }
                      }}
                    >
                      <Typography sx={{ fontWeight: isActive(child.path) ? 600 : 400 }}>
                        {child.label}
                      </Typography>
                    </Button>
                  ))}
                </Box>
              </Collapse>
            )}
          </Box>
        ))}

        {/* Create Button */}
        <Box sx={{ px: 3, py: 2 }}>
          <Button
            variant="contained"
            startIcon={<Plus size={16} />}
            onClick={() => handleNavigation('/templates/create')}
            sx={{
              width: '100%',
              py: 2,
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: '#fff',
              textTransform: 'none',
              fontWeight: 600,
              fontSize: '14px',
              borderRadius: '8px',
              boxShadow: '0 4px 14px 0 rgba(79, 70, 229, 0.39)',
              '&:hover': {
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                transform: 'translateY(-1px)',
                boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
              }
            }}
          >
            Create Template
          </Button>
        </Box>
      </Box>

      {/* Bottom Navigation */}
      <Box sx={{ borderTop: '1px solid #e5e7eb', py: 2 }}>
        <Button
          onClick={() => handleNavigation('/settings')}
          sx={{
            width: '100%',
            justifyContent: 'flex-start',
            px: 3,
            py: 2,
            borderRadius: 0,
            textTransform: 'none',
            color: '#6b7280',
            '&:hover': {
              bgcolor: '#f9fafb'
            }
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Settings size={18} />
            <Typography sx={{ fontWeight: 500, fontSize: '14px' }}>
              Settings
            </Typography>
          </Box>
        </Button>
        
        <Divider sx={{ mx: 3, my: 2 }} />
        
        <Button
          onClick={() => { logout(); navigate('/login'); if (isMobile) onClose(); }}
          sx={{
            width: '100%',
            justifyContent: 'flex-start',
            px: 3,
            py: 2,
            borderRadius: 0,
            textTransform: 'none',
            color: '#ef4444',
            '&:hover': {
              bgcolor: '#fef2f2'
            }
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <LogOut size={18} />
            <Typography sx={{ fontWeight: 500, fontSize: '14px' }}>
              Logout
            </Typography>
          </Box>
        </Button>
      </Box>
    </Box>
  );
};

export default SidebarNew;
