import React, { useState } from 'react';
import {
  Box,
  useMediaQuery,
  CircularProgress,
  Alert,
  AlertTitle,
} from '@mui/material';
import Cards from '../../../components/Cards';
import TemplateTable from '../../../components/TemplateTables/TemplateDashboard';
import useTemplateTable from '../../../hooks/Templates/useTemplateTable';

const Templates = () => {
  const {
    statsData,
    tableData,
    loading,
    error,
    fetchData
  } = useTemplateTable();

  const [navigationLoading, setNavigationLoading] = useState(false);
  const isMobile = useMediaQuery("(max-width: 600px)");

  if (loading || navigationLoading) {
    return (
      <Box sx={{
        backgroundColor: '#F9FBFC',
        flexGrow: 1,
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        zIndex: 9999,
        ...(isMobile && {
          minHeight: 'calc(100vh - 64px)',
        })
      }}>
        <CircularProgress size={60} sx={{ color: '#1958F7' }} />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{
        backgroundColor: '#F9FBFC',
        flexGrow: 1,
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        p: isMobile ? 2 : 4,
        ...(isMobile && {
          minHeight: 'calc(100vh - 64px)',
        })
      }}>
        <Alert severity="error" sx={{ maxWidth: 500 }}>
          <AlertTitle>Error Loading Data</AlertTitle>
          {error}
        </Alert>
      </Box>
    );
  }

  return (
    <Box sx={{
      backgroundColor: '#F9FBFC',
      flexGrow: 1,
      display: 'flex',
      flexDirection: 'column',
      p: isMobile ? 2 : 4,
      ...(isMobile && {
        minHeight: 'calc(100vh - 64px)',
        overflow: 'auto'
      })
    }}>
      <Cards headerTitle="Manage Templates" statsData={statsData} loading={loading} error={error} />
      <TemplateTable 
        tableData={tableData} 
        refreshTable={fetchData} 
        setNavigationLoading={setNavigationLoading}
      />
    </Box>
  );
};

export default Templates;