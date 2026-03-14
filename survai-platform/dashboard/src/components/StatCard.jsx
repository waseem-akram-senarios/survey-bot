import React from 'react';
import { Card, CardContent, Typography, Box, Avatar } from '@mui/material';

const StatCard = ({ title, value, subValue, icon: _Icon, color, trend, gradient }) => {
  // Default gradient based on color if not provided
  const defaultGradients = {
    '#f59e0b': 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
    '#10b981': 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
    '#6366f1': 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)',
    '#8b5cf6': 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
    '#ef4444': 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
  };

  const cardGradient = gradient || defaultGradients[color] || defaultGradients['#6366f1'];

  return (
    <Card 
      className="fade-in hover-lift"
      sx={{ 
        minWidth: 200, 
        flex: 1, 
        background: '#fff', 
        border: '1px solid var(--color-gray-200)',
        borderRadius: 'var(--radius-xl)',
        boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.06), 0 1px 2px -1px rgb(0 0 0 / 0.06)',
        transition: 'all 0.3s ease',
        position: 'relative',
        overflow: 'hidden',
        '&:hover': { 
          transform: 'translateY(-4px)',
          boxShadow: '0 20px 25px -5px rgb(0 0 0 / 0.08), 0 8px 10px -6px rgb(0 0 0 / 0.06)',
          borderColor: color
        },
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '4px',
          background: cardGradient,
        }
      }}
    >
      <CardContent sx={{ 
        display: 'flex', 
        alignItems: 'flex-start', 
        justifyContent: 'space-between', 
        pb: '24px !important',
        pt: '20px !important',
        px: '24px !important'
      }}>
        <Box sx={{ flex: 1 }}>
          <Typography 
            variant="overline" 
            sx={{ 
              color: 'var(--color-gray-500)', 
              fontWeight: 600, 
              letterSpacing: '0.5px',
              fontSize: 'var(--text-xs)',
              textTransform: 'uppercase',
              mb: 1
            }}
          >
            {title}
          </Typography>
          <Typography 
            variant="h4" 
            sx={{ 
              fontWeight: 800, 
              fontSize: 'var(--text-3xl)',
              color: 'var(--color-gray-900)',
              lineHeight: 1.2,
              mb: 0.5
            }}
          >
            {value}
          </Typography>
          {subValue && (
            <Typography 
              variant="caption" 
              sx={{ 
                color: 'var(--color-gray-500)', 
                display: 'block', 
                fontSize: 'var(--text-sm)',
                fontWeight: 500
              }}
            >
              {subValue}
            </Typography>
          )}
          {trend && (
            <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
              <Typography 
                variant="caption" 
                sx={{ 
                  color: trend > 0 ? 'var(--color-success-500)' : 'var(--color-error-500)',
                  fontWeight: 600,
                  fontSize: 'var(--text-xs)',
                  mr: 0.5
                }}
              >
                {trend > 0 ? '+' : ''}{trend}%
              </Typography>
            </Box>
          )}
        </Box>
        <Avatar sx={{ 
          background: cardGradient,
          color: '#fff',
          width: 56,
          height: 56,
          borderRadius: 'var(--radius-xl)',
          boxShadow: 'var(--shadow-md)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <Icon size={28} />
        </Avatar>
      </CardContent>
    </Card>
  );
};

export default StatCard;
