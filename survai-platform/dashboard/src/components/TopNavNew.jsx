import React, { useState } from 'react';
import {
  Box,
  Typography,
  IconButton,
  Avatar,
  Menu,
  MenuItem,
  Badge,
  TextField,
  InputAdornment,
  Button
} from '@mui/material';
import {
  Search,
  Bell,
  Settings,
  User,
  LogOut,
  HelpCircle,
  Menu as MenuIcon
} from 'lucide-react';

const TopNavNew = ({ onSidebarToggle, sidebarOpen }) => {
  const [anchorEl, setAnchorEl] = useState(null);
  const [notificationAnchor, setNotificationAnchor] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');

  const handleUserMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleUserMenuClose = () => {
    setAnchorEl(null);
  };

  const handleNotificationMenuOpen = (event) => {
    setNotificationAnchor(event.currentTarget);
  };

  const handleNotificationMenuClose = () => {
    setNotificationAnchor(null);
  };

  return (
    <Box
      sx={{
        height: 72,
        bgcolor: '#fff',
        borderBottom: '1px solid #e5e7eb',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        px: 4,
        position: 'sticky',
        top: 0,
        zIndex: 100
      }}
    >
      {/* Left Section */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 3 }}>
        {/* Menu Toggle */}
        <IconButton
          onClick={onSidebarToggle}
          sx={{
            color: '#6b7280',
            '&:hover': {
              bgcolor: '#f9fafb'
            }
          }}
        >
          <MenuIcon size={24} />
        </IconButton>

        {/* Search Bar */}
        <TextField
          placeholder="Search surveys, templates..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          size="small"
          sx={{
            width: 320,
            '& .MuiOutlinedInput-root': {
              bgcolor: '#f9fafb',
              borderRadius: '8px',
              '& fieldset': {
                border: '1px solid #e5e7eb',
                '&:hover': {
                  borderColor: '#d1d5db'
                }
              },
              '&.Mui-focused fieldset': {
                borderColor: '#6366f1',
                boxShadow: '0 0 0 3px rgba(99, 102, 241, 0.1)'
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
      </Box>

      {/* Right Section */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        {/* Notifications */}
        <IconButton
          onClick={handleNotificationMenuOpen}
          sx={{
            color: '#6b7280',
            '&:hover': {
              bgcolor: '#f9fafb'
            }
          }}
        >
          <Badge badgeContent={3} color="error">
            <Bell size={20} />
          </Badge>
        </IconButton>

        {/* User Menu */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, cursor: 'pointer' }} onClick={handleUserMenuOpen}>
          <Box sx={{ textAlign: 'right', display: { xs: 'none', md: 'block' } }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#1f2937', fontSize: '14px' }}>
              Admin User
            </Typography>
            <Typography variant="caption" sx={{ color: '#6b7280', fontSize: '12px' }}>
              Administrator
            </Typography>
          </Box>
          <Avatar
            sx={{
              width: 40,
              height: 40,
              bgcolor: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: '#fff',
              fontWeight: 600,
              fontSize: '14px'
            }}
          >
            AD
          </Avatar>
        </Box>
      </Box>

      {/* User Menu Dropdown */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleUserMenuClose}
        PaperProps={{
          sx: {
            mt: 1,
            minWidth: 200,
            borderRadius: '8px',
            boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
            border: '1px solid #e5e7eb'
          }
        }}
      >
        <MenuItem onClick={handleUserMenuClose}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <User size={18} />
            <Typography>Profile</Typography>
          </Box>
        </MenuItem>
        <MenuItem onClick={handleUserMenuClose}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Settings size={18} />
            <Typography>Settings</Typography>
          </Box>
        </MenuItem>
        <MenuItem onClick={handleUserMenuClose}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <HelpCircle size={18} />
            <Typography>Help & Support</Typography>
          </Box>
        </MenuItem>
        <MenuItem onClick={handleUserMenuClose} sx={{ color: '#ef4444' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <LogOut size={18} />
            <Typography>Logout</Typography>
          </Box>
        </MenuItem>
      </Menu>

      {/* Notification Menu Dropdown */}
      <Menu
        anchorEl={notificationAnchor}
        open={Boolean(notificationAnchor)}
        onClose={handleNotificationMenuClose}
        PaperProps={{
          sx: {
            mt: 1,
            minWidth: 320,
            maxWidth: 400,
            borderRadius: '8px',
            boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
            border: '1px solid #e5e7eb'
          }
        }}
      >
        <Box sx={{ p: 2, borderBottom: '1px solid #e5e7eb' }}>
          <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
            Notifications
          </Typography>
        </Box>
        
        <MenuItem sx={{ py: 2, flexDirection: 'column', alignItems: 'flex-start' }}>
          <Typography variant="body2" sx={{ fontWeight: 500, mb: 0.5 }}>
            New survey completed
          </Typography>
          <Typography variant="caption" sx={{ color: '#6b7280' }}>
            Customer satisfaction survey completed 2 hours ago
          </Typography>
        </MenuItem>
        
        <MenuItem sx={{ py: 2, flexDirection: 'column', alignItems: 'flex-start' }}>
          <Typography variant="body2" sx={{ fontWeight: 500, mb: 0.5 }}>
            Template published
          </Typography>
          <Typography variant="caption" sx={{ color: '#6b7280' }}>
            Your template was successfully published
          </Typography>
        </MenuItem>
      </Menu>
    </Box>
  );
};

export default TopNavNew;
