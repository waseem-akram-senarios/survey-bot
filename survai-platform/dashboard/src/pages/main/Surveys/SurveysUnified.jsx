import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Box, Tabs, Tab, Typography } from '@mui/material';
import { ClipboardList, Library } from 'lucide-react';
import ManageSurveys from './ManageSurveys';
import Templates from '../Templates/Templates';

const TAB_LAUNCHED = 'launched';
const TAB_LIBRARY = 'library';

export default function SurveysUnified() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const tabFromUrl = searchParams.get('tab') || TAB_LAUNCHED;
  const [tab, setTab] = useState(tabFromUrl === TAB_LIBRARY ? TAB_LIBRARY : TAB_LAUNCHED);

  useEffect(() => {
    const t = searchParams.get('tab') || TAB_LAUNCHED;
    setTab(t === TAB_LIBRARY ? TAB_LIBRARY : TAB_LAUNCHED);
  }, [searchParams]);

  const handleTabChange = (_, value) => {
    setTab(value);
    setSearchParams({ tab: value });
  };

  return (
    <Box sx={{ width: '100%', minHeight: '100%', pb: 4 }}>
      <Box sx={{ borderBottom: 1, borderColor: 'divider', px: { xs: 2, md: 3 }, pt: 2 }}>
        <Typography variant="h5" sx={{ fontWeight: 700, mb: 2 }}>
          Surveys
        </Typography>
        <Tabs value={tab} onChange={handleTabChange} sx={{ minHeight: 48 }}>
          <Tab
            value={TAB_LAUNCHED}
            label="Launched"
            icon={<ClipboardList size={18} />}
            iconPosition="start"
            sx={{ textTransform: 'none', fontWeight: 600 }}
          />
          <Tab
            value={TAB_LIBRARY}
            label="Survey library"
            icon={<Library size={18} />}
            iconPosition="start"
            sx={{ textTransform: 'none', fontWeight: 600 }}
          />
        </Tabs>
      </Box>
      <Box sx={{ px: { xs: 2, md: 3 }, pt: 2 }}>
        {tab === TAB_LAUNCHED && <ManageSurveys />}
        {tab === TAB_LIBRARY && <Templates />}
      </Box>
    </Box>
  );
}
