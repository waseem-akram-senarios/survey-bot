import React, { useState } from 'react';
import {
  Box,
  Typography,
  IconButton,
  Avatar,
  Menu,
  MenuItem,
  Badge,
  Tooltip,
  TextField,
  InputAdornment
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

const TopNavigation = ({ onSidebarToggle, sidebarOpen }) => {
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
        borderBottom: '1px solid var(--color-gray-200)',
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
            color: 'var(--color-gray-600)',
            '&:hover': {
              bgcolor: 'var(--color-gray-50)'
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
              bgcolor: 'var(--color-gray-50)',
              borderRadius: 'var(--radius-lg)',
              '& fieldset': {
                border: '1px solid var(--color-gray-200)',
                '&:hover': {
                  borderColor: 'var(--color-gray-300)'
                }
              },
              '&.Mui-focused fieldset': {
                borderColor: 'var(--color-primary-500)',
                boxShadow: '0 0 0 3px rgba(99, 102, 241, 0.1)'
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
      </Box>

      {/* Right Section */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        {/* Notifications */}
        <Tooltip title="Notifications">
          <IconButton
            onClick={handleNotificationMenuOpen}
            sx={{
              color: 'var(--color-gray-600)',
              '&:hover': {
                bgcolor: 'var(--color-gray-50)'
              }
            }}
          >
            <Badge badgeContent={3} color="error">
              <Bell size={20} />
            </Badge>
          </IconButton>
        </Tooltip>

        {/* User Menu */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, cursor: 'pointer' }} onClick={handleUserMenuOpen}>
          <Box sx={{ textAlign: 'right', display: { xs: 'none', md: 'block' } }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 600, color: 'var(--color-gray-900)', fontSize: '14px' }}>
              Admin User
            </Typography>
            <Typography variant="caption" sx={{ color: 'var(--color-gray-500)', fontSize: '12px' }}>
              Administrator
            </Typography>
          </Box>
          <Avatar
            sx={{
              width: 40,
              height: 40,
              bgcolor: 'var(--gradient-primary)',
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
            borderRadius: 'var(--radius-lg)',
            boxShadow: 'var(--shadow-lg)',
            border: '1px solid var(--color-gray-200)'
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
        <MenuItem onClick={handleUserMenuClose} sx={{ color: 'var(--color-error-500)' }}>
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
            borderRadius: 'var(--radius-lg)',
            boxShadow: 'var(--shadow-lg)',
            border: '1px solid var(--color-gray-200)'
          }
        }}
      >
        <Box sx={{ p: 2, borderBottom: '1px solid var(--color-gray-200)' }}>
          <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
            Notifications
          </Typography>
        </Box>
        
        <MenuItem sx={{ py: 2, flexDirection: 'column', alignItems: 'flex-start' }}>
          <Typography variant="body2" sx={{ fontWeight: 500, mb: 0.5 }}>
            New survey completed
          </Typography>
          <Typography variant="caption" sx={{ color: 'var(--color-gray-500)' }}>
            Customer satisfaction survey for John Doe was completed 2 hours ago
          </Typography>
        </MenuItem>
        
        <MenuItem sx={{ py: 2, flexDirection: 'column', alignItems: 'flex-start' }}>
          <Typography variant="body2" sx={{ fontWeight: 500, mb: 0.5 }}>
            Template published
          </Typography>
          <Typography variant="caption" sx={{ color: 'var(--color-gray-500)' }}>
            Your "Customer Feedback" template was successfully published
          </Typography>
        </MenuItem>
        
        <MenuItem sx={{ py: 2, flexDirection: 'column', alignItems: 'flex-start' }}>
          <Typography variant="body2" sx={{ fontWeight: 500, mb: 0.5 }}>
            System update
          </Typography>
          <Typography variant="caption" sx={{ color: 'var(--color-gray-500)' }}>
            New features have been added to the survey platform
          </Typography>
        </MenuItem>
      </Menu>
    </Box>
  );
};

export default TopNavigation;
