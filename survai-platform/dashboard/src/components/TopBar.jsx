import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Button,
  Box,
  IconButton,
  useMediaQuery,
  Drawer,
  List,
  ListItemButton,
  ListItemText,
  Avatar,
  Menu,
  MenuItem,
  Typography,
  Divider,
} from '@mui/material';
import { Menu as MenuIcon, User, LayoutDashboard, BarChart3, Users, ClipboardList, LogOut, Settings } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import logo from '../assets/logo.png';

const navItems = [
  { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/surveys', label: 'Surveys', icon: ClipboardList },
  { path: '/analytics', label: 'Analytics', icon: BarChart3 },
  { path: '/contacts', label: 'Contacts', icon: Users },
];

const TopBar = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const isMobile = useMediaQuery('(max-width: 900px)');
  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);

  const isActive = (path) => {
    if (path === '/dashboard') return location.pathname === '/dashboard';
    // Match any sub-path for sections
    const base = path.split('/').slice(0, 2).join('/');
    return location.pathname.startsWith(base);
  };

  const handleLogout = () => {
    setAnchorEl(null);
    logout();
    navigate('/login');
  };

  const drawer = (
    <Box sx={{ pt: 2, px: 2 }}>
      <List>
        {navItems.map(({ path, label, icon: Icon }) => (
          <ListItemButton
            key={path}
            data-testid={`nav-${label.toLowerCase()}`}
            onClick={() => {
              navigate(path);
              setMobileOpen(false);
            }}
            sx={{
              borderRadius: '12px',
              mb: 0.5,
              backgroundColor: isActive(path) ? '#E8E0F5' : 'transparent',
            }}
          >
            <Box sx={{ mr: 1.5, display: 'flex', color: isActive(path) ? '#4f46e5' : '#6b7280' }}>
              <Icon size={20} />
            </Box>
            <ListItemText primary={label} primaryTypographyProps={{ fontSize: 15, color: isActive(path) ? '#4f46e5' : '#333', fontWeight: isActive(path) ? 600 : 400 }} />
          </ListItemButton>
        ))}
      </List>
      <Divider sx={{ my: 2 }} />
      <ListItemButton
        onClick={handleLogout}
        sx={{ borderRadius: '12px', color: '#ef4444' }}
      >
        <Box sx={{ mr: 1.5, display: 'flex' }}>
          <LogOut size={20} />
        </Box>
        <ListItemText primary="Logout" primaryTypographyProps={{ fontSize: 15, fontWeight: 500 }} />
      </ListItemButton>
    </Box>
  );

  return (
    <AppBar
      position="fixed"
      elevation={0}
      sx={{
        backgroundColor: 'rgba(255, 255, 255, 0.8)',
        backdropFilter: 'blur(8px)',
        borderBottom: '1px solid #f0f0f0',
        zIndex: 1300,
        px: { xs: 1, md: 4 }
      }}
    >
      <Toolbar sx={{ justifyContent: 'space-between', height: 72 }}>
        {/* Left: logo + tagline + user pill */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          {isMobile ? (
            <IconButton onClick={() => setMobileOpen(true)} edge="start" sx={{ color: '#333' }}>
              <MenuIcon size={24} />
            </IconButton>
          ) : null}
          <Box
            component="img"
            src={logo}
            alt="SurvAI"
            sx={{ height: 32, width: 'auto', cursor: 'pointer' }}
            onClick={() => navigate('/dashboard')}
          />
          {user && (
            <Box sx={{ 
              backgroundColor: '#eef2ff', 
              color: '#4f46e5', 
              px: 2, 
              py: 0.5, 
              borderRadius: '99px',
              fontWeight: 500,
              fontSize: '13px'
            }}>
              {user.orgName || user.username}
            </Box>
          )}
        </Box>

        {/* Center: nav links */}
        {!isMobile && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            {navItems.map(({ path, label, icon: Icon }) => (
              <Button
                key={path}
                data-testid={`nav-${label.toLowerCase()}`}
                onClick={() => navigate(path)}
                startIcon={<Icon size={18} />}
                sx={{
                  color: isActive(path) ? '#4f46e5' : '#6b7280',
                  backgroundColor: isActive(path) ? '#eef2ff' : 'transparent',
                  fontWeight: 600,
                  fontSize: '13px',
                  px: 1.5,
                  py: 1,
                  borderRadius: '10px',
                  '&:hover': {
                    backgroundColor: isActive(path) ? '#eef2ff' : '#f3f4f6',
                  },
                }}
              >
                {label}
              </Button>
            ))}
          </Box>
        )}

        {/* Right: profile icon with dropdown */}
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Avatar
            onClick={(e) => setAnchorEl(e.currentTarget)}
            sx={{
              bgcolor: '#eef2ff',
              color: '#4f46e5',
              width: 36,
              height: 36,
              cursor: 'pointer',
              fontWeight: 600,
              fontSize: '14px',
            }}
          >
            {user?.username ? user.username.charAt(0).toUpperCase() : <User size={18} />}
          </Avatar>
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={() => setAnchorEl(null)}
            PaperProps={{
              sx: {
                mt: 1,
                minWidth: 200,
                borderRadius: '12px',
                boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
                border: '1px solid #e5e7eb',
              }
            }}
          >
            <Box sx={{ px: 2, pt: 1.5, pb: 1 }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#1f2937' }}>
                {user?.username || 'User'}
              </Typography>
              <Typography variant="caption" sx={{ color: '#6b7280' }}>
                {user?.orgName || 'Organization'}
              </Typography>
            </Box>
            <Divider sx={{ my: 0.5 }} />
            <MenuItem onClick={() => { setAnchorEl(null); navigate('/dashboard'); }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                <Settings size={16} />
                <Typography variant="body2">Settings</Typography>
              </Box>
            </MenuItem>
            <MenuItem onClick={handleLogout} sx={{ color: '#ef4444' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                <LogOut size={16} />
                <Typography variant="body2">Logout</Typography>
              </Box>
            </MenuItem>
          </Menu>
        </Box>
      </Toolbar>

      <Drawer
        anchor="left"
        open={mobileOpen}
        onClose={() => setMobileOpen(false)}
        PaperProps={{
          sx: { width: 280, p: 2 },
        }}
      >
        <Box sx={{ mb: 4, px: 2, pt: 2 }}>
           <img src={logo} alt="Logo" style={{ height: 28 }} />
        </Box>
        {drawer}
      </Drawer>
    </AppBar>
  );
};

export default TopBar;
