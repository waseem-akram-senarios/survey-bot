import React from 'react';
import { Box } from '@mui/material';
import { Outlet } from 'react-router-dom';
import TopBar from '../components/TopBar';

const TOP_BAR_HEIGHT = 72;

const MainLayout = () => {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', bgcolor: 'background.default' }}>
      <TopBar />
      <Box
        component="main"
        sx={{
          flex: 1,
          overflowY: 'auto',
          pt: `${TOP_BAR_HEIGHT}px`,
          bgcolor: 'background.default',
          width: '100%',
        }}
      >
        <Outlet />
      </Box>
    </Box>
  );
};

export default MainLayout;
