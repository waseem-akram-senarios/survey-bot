import React, { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  Collapse,
  IconButton,
  Avatar,
  Divider,
  Tooltip
} from '@mui/material';
import {
  Dashboard,
  FileText,
  Users,
  Settings,
  HelpCircle,
  LogOut,
  ChevronDown,
  ChevronRight,
  Plus,
  Menu,
  X
} from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';
import logo from '../assets/logo.png';

const ModernSidebar = ({ isOpen, onClose, isMobile = false }) => {
  const navigate = useNavigate();
  const location = useLocation();
  
  const [expandedSections, setExpandedSections] = useState({
    templates: true,
    surveys: true
  });

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const isActive = (path) => location.pathname.startsWith(path);

  const menuItems = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      icon: Dashboard,
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
        { label: 'Manage Templates', path: '/templates/manage' },
        { label: 'Saved Drafts', path: '/templates/drafts' }
      ]
    },
    {
      id: 'surveys',
      label: 'Surveys',
      icon: Users,
      path: '/surveys',
      color: '#10b981',
      children: [
        { label: 'Launch New Survey', path: '/surveys/launch' },
        { label: 'Manage Surveys', path: '/surveys/manage' },
        { label: 'Completed Surveys', path: '/surveys/completed' }
      ]
    }
  ];

  const bottomMenuItems = [
    {
      id: 'settings',
      label: 'Settings',
      icon: Settings,
      path: '/settings',
      color: '#6b7280'
    },
    {
      id: 'help',
      label: 'Help & Support',
      icon: HelpCircle,
      path: '/help',
      color: '#6b7280'
    }
  ];

  const handleNavigation = (path) => {
    navigate(path);
    if (isMobile) {
      onClose();
    }
  };

  return (
    <Box
      sx={{
        width: isMobile ? '100vw' : 280,
        height: '100vh',
        bgcolor: '#fff',
        borderRight: '1px solid var(--color-gray-200)',
        display: 'flex',
        flexDirection: 'column',
        position: isMobile ? 'fixed' : 'relative',
        left: 0,
        top: 0,
        zIndex: isMobile ? 1400 : 1,
        transform: isMobile && !isOpen ? 'translateX(-100%)' : 'translateX(0)',
        transition: 'transform 0.3s ease',
        boxShadow: isMobile ? 'var(--shadow-lg)' : 'none'
      }}
    >
      {/* Header */}
      <Box sx={{ p: 3, borderBottom: '1px solid var(--color-gray-200)' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <img src={logo} alt="SurvAI" style={{ width: 32, height: 32 }} />
            <Typography variant="h6" sx={{ fontWeight: 700, color: 'var(--color-gray-900)' }}>
              SurvAI
            </Typography>
          </Box>
          {isMobile && (
            <IconButton onClick={onClose} size="small">
              <X size={20} />
            </IconButton>
          )}
        </Box>
      </Box>

      {/* User Profile */}
      <Box sx={{ p: 3, borderBottom: '1px solid var(--color-gray-200)' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 3 }}>
          <Avatar
            sx={{
              width: 48,
              height: 48,
              bgcolor: 'var(--gradient-primary)',
              color: '#fff',
              fontWeight: 600,
              fontSize: '18px'
            }}
          >
            AD
          </Avatar>
          <Box sx={{ flex: 1 }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 600, color: 'var(--color-gray-900)' }}>
              Admin User
            </Typography>
            <Typography variant="caption" sx={{ color: 'var(--color-gray-500)' }}>
              admin@survai.com
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
                color: isActive(item.path) ? item.color : 'var(--color-gray-700)',
                '&:hover': {
                  bgcolor: isActive(item.path) ? `${item.color}25` : 'var(--color-gray-50)'
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
                        color: isActive(child.path) ? item.color : 'var(--color-gray-600)',
                        fontSize: '13px',
                        '&:hover': {
                          bgcolor: 'var(--color-gray-50)'
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

        {/* Create Template Button */}
        <Box sx={{ px: 3, py: 2 }}>
          <Button
            variant="contained"
            startIcon={<Plus size={16} />}
            onClick={() => handleNavigation('/templates/create')}
            sx={{
              width: '100%',
              py: 2,
              background: 'var(--gradient-primary)',
              color: '#fff',
              textTransform: 'none',
              fontWeight: 600,
              fontSize: '14px',
              borderRadius: 'var(--radius-lg)',
              boxShadow: 'var(--shadow-button)',
              '&:hover': {
                background: 'var(--gradient-primary)',
                transform: 'translateY(-1px)',
                boxShadow: 'var(--shadow-lg)'
              }
            }}
          >
            Create Template
          </Button>
        </Box>
      </Box>

      {/* Bottom Navigation */}
      <Box sx={{ borderTop: '1px solid var(--color-gray-200)', py: 2 }}>
        {bottomMenuItems.map((item) => (
          <Button
            key={item.id}
            onClick={() => handleNavigation(item.path)}
            sx={{
              width: '100%',
              justifyContent: 'flex-start',
              px: 3,
              py: 2,
              borderRadius: 0,
              textTransform: 'none',
              color: isActive(item.path) ? item.color : 'var(--color-gray-600)',
              '&:hover': {
                bgcolor: 'var(--color-gray-50)'
              }
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <item.icon size={18} />
              <Typography sx={{ fontWeight: 500, fontSize: '14px' }}>
                {item.label}
              </Typography>
            </Box>
          </Button>
        ))}
        
        <Divider sx={{ mx: 3, my: 2 }} />
        
        <Button
          onClick={() => {
            // Handle logout
            console.log('Logout clicked');
          }}
          sx={{
            width: '100%',
            justifyContent: 'flex-start',
            px: 3,
            py: 2,
            borderRadius: 0,
            textTransform: 'none',
            color: 'var(--color-error-500)',
            '&:hover': {
              bgcolor: 'var(--color-error-50)'
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

export default ModernSidebar;
