import React from 'react';
import { Card, CardContent, Typography, Box, Avatar } from '@mui/material';

const StatCardNew = ({ title, value, subValue, icon: _Icon, color, trend, gradient }) => {
  // Default gradients for each color
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
      sx={{ 
        minWidth: 200, 
        flex: 1, 
        background: '#fff', 
        border: '1px solid #e5e7eb',
        borderRadius: '12px',
        transition: 'all 0.3s ease',
        position: 'relative',
        overflow: 'hidden',
        '&:hover': { 
          transform: 'translateY(-4px)',
          boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
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
              color: '#6b7280', 
              fontWeight: 600, 
              letterSpacing: '0.5px',
              fontSize: '12px',
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
              fontSize: '30px',
              color: '#1f2937',
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
                color: '#6b7280', 
                display: 'block', 
                fontSize: '14px',
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
                  color: trend > 0 ? '#10b981' : '#ef4444',
                  fontWeight: 600,
                  fontSize: '12px',
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
          borderRadius: '12px',
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
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

export default StatCardNew;
