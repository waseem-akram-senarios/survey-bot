import React, { useMemo, useState } from 'react';
import {
  Avatar,
  Box,
  Button,
  Chip,
  Divider,
  IconButton,
  LinearProgress,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Paper,
  Stack,
  Tab,
  Tabs,
  Tooltip,
  Typography,
} from '@mui/material';
import {
  Add,
  Assessment,
  CalendarMonth,
  ChatBubbleOutline,
  CheckCircle,
  ContentCopy,
  Dashboard,
  Description,
  Drafts,
  HelpOutline,
  InsertChartOutlined,
  Menu,
  PeopleAlt,
  RadioButtonChecked,
  Settings,
  Share,
  Star,
  TextFields,
  Visibility,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const NAV_LINKS = [
  { label: 'Dashboard', icon: <Dashboard fontSize="small" />, path: '/dashboard' },
  { label: 'Analytics', icon: <Assessment fontSize="small" />, path: '/analytics' },
  { label: 'Contacts', icon: <PeopleAlt fontSize="small" />, path: '/contacts' },
];

const QUESTION_TYPES = [
  {
    label: 'Multiple Choice',
    description: 'Respondents select one option',
    icon: RadioButtonChecked,
    color: '#7B61FF',
  },
  {
    label: 'Open Ended',
    description: 'Short or long text responses',
    icon: TextFields,
    color: '#FF7AB2',
  },
  {
    label: 'Yes / No',
    description: 'Binary decision question',
    icon: CheckCircle,
    color: '#00C4B8',
  },
  {
    label: 'Rating Scale',
    description: 'Measure satisfaction on a scale',
    icon: Star,
    color: '#FFCF4A',
  },
  {
    label: 'NPS Score',
    description: 'Net promoter score question',
    icon: InsertChartOutlined,
    color: '#F97316',
  },
  {
    label: 'Route / Stop',
    description: 'Transit or route based question',
    icon: Share,
    color: '#38BDF8',
  },
  {
    label: 'Date / Time',
    description: 'Collect scheduling preferences',
    icon: CalendarMonth,
    color: '#6366F1',
  },
];

const QUICK_ADD_BUTTONS = [
  { label: 'Multiple Choice', color: '#7B61FF' },
  { label: 'Open Ended', color: '#FF7AB2' },
  { label: 'Yes / No', color: '#00C4B8' },
  { label: 'Rating Scale', color: '#FFCF4A' },
  { label: 'NPS Score', color: '#F97316' },
  { label: 'Route / Stop', color: '#38BDF8' },
  { label: 'Date / Time', color: '#6366F1' },
];

const RIGHT_PANEL_CONTENT = {
  questions: {
    title: 'Question Properties',
    description: 'Select a question to configure visibility, logic, and validation.',
    sections: [
      { heading: 'Visibility', items: ['Always show', 'Show based on logic', 'Hide in preview'] },
      { heading: 'Response options', items: ['Required response', 'Limit to one per rider'] },
    ],
  },
  settings: {
    title: 'Survey Settings',
    description: 'Branding, language, and survey experience controls.',
    sections: [
      { heading: 'Branding', items: ['ITCurves Primary Theme', 'Logo placement: Top'] },
      { heading: 'Language', items: ['English (default)', 'Spanish (secondary)'] },
    ],
  },
  distribution: {
    title: 'Distribution Channels',
    description: 'Decide how you want to share this survey.',
    sections: [
      { heading: 'Channels', items: ['SMS Blast (Scheduled)', 'Email Campaign draft', 'Web Link active'] },
      { heading: 'Follow ups', items: ['Reminder 24h after no response'] },
    ],
  },
};

const SurveyBuilderSimple = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('questions');

  const rightPanel = useMemo(() => RIGHT_PANEL_CONTENT[activeTab], [activeTab]);

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#F5F6FA', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box
        sx={{
          bgcolor: 'white',
          borderBottom: '1px solid #E5E7EB',
          boxShadow: '0 2px 12px rgba(15, 23, 42, 0.08)',
          px: 3,
          py: 1.5,
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <IconButton onClick={() => navigate('/surveys')}>
            <Menu />
          </IconButton>

          <Stack spacing={0}>
            <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
              ITCurves
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Rider Voice — waseem
            </Typography>
          </Stack>

          <Divider orientation="vertical" flexItem sx={{ mx: 2 }} />

          <Stack direction="row" spacing={1} alignItems="center" sx={{ flex: 1 }}>
            {NAV_LINKS.map((link) => (
              <Button
                key={link.label}
                startIcon={link.icon}
                variant="text"
                sx={{
                  textTransform: 'none',
                  color: 'text.secondary',
                  fontWeight: 500,
                }}
                onClick={() => navigate(link.path)}
              >
                {link.label}
              </Button>
            ))}
          </Stack>

          <Stack direction="row" spacing={1.5} alignItems="center">
            <Button
              variant="outlined"
              size="small"
              sx={{ textTransform: 'none', borderRadius: 999, borderColor: '#E5E7EB' }}
            >
              Preview
            </Button>
            <Button
              variant="contained"
              size="small"
              sx={{
                textTransform: 'none',
                borderRadius: 999,
                px: 3,
                bgcolor: '#7B61FF',
                '&:hover': { bgcolor: '#6B4FE0' },
              }}
            >
              Save Survey
            </Button>
            <Avatar sx={{ width: 36, height: 36, bgcolor: '#7B61FF' }}>W</Avatar>
          </Stack>
        </Box>
      </Box>

      {/* Tabs */}
      <Box sx={{ bgcolor: 'white', borderBottom: '1px solid #E5E7EB' }}>
        <Tabs
          value={activeTab}
          onChange={(_, value) => setActiveTab(value)}
          textColor="secondary"
          TabIndicatorProps={{ style: { display: 'none' } }}
          sx={{
            '& .MuiTab-root': {
              textTransform: 'none',
              fontWeight: 600,
              color: '#6B7280',
              minHeight: 48,
            },
            '& .Mui-selected': {
              color: '#7B61FF',
              bgcolor: '#F2ECFF',
              borderRadius: 999,
              mx: 1,
            },
          }}
        >
          <Tab value="questions" label="Questions" />
          <Tab value="settings" label="Settings" />
          <Tab value="distribution" label="Distribution" />
        </Tabs>
      </Box>

      {/* Workspace */}
      <Box sx={{ flex: 1, display: 'flex', gap: 3, p: 3 }}>
        {/* Left Sidebar */}
        <Box
          sx={{
            width: 300,
            bgcolor: 'white',
            borderRadius: 3,
            p: 3,
            boxShadow: '0 8px 20px rgba(15, 23, 42, 0.07)',
            border: '1px solid #F1F5F9',
          }}
        >
          <Typography variant="subtitle1" sx={{ fontWeight: 700, mb: 0.5 }}>
            Question Types
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Drag or click to add questions to your survey
          </Typography>

          <Stack spacing={2}>
            {QUESTION_TYPES.map((type) => {
              const Icon = type.icon;
              return (
                <Paper
                  key={type.label}
                  elevation={0}
                  sx={{
                    border: '1px solid #EEF2FF',
                    borderRadius: 3,
                    p: 2,
                    display: 'flex',
                    alignItems: 'center',
                    gap: 2,
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    '&:hover': {
                      boxShadow: '0 8px 16px rgba(124, 58, 237, 0.15)',
                      transform: 'translateY(-2px)',
                    },
                  }}
                >
                  <Box
                    sx={{
                      width: 44,
                      height: 44,
                      borderRadius: 2,
                      bgcolor: `${type.color}10`,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: type.color,
                    }}
                  >
                    <Icon />
                  </Box>
                  <Box sx={{ flex: 1 }}>
                    <Typography sx={{ fontWeight: 600 }}>{type.label}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      {type.description}
                    </Typography>
                  </Box>
                  <Button size="small" variant="outlined" sx={{ borderRadius: 999, textTransform: 'none' }}>
                    + Add
                  </Button>
                </Paper>
              );
            })}
          </Stack>
        </Box>

        {/* Center Canvas */}
        <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 2 }}>
          <Paper
            elevation={0}
            sx={{
              borderRadius: 3,
              p: 3,
              border: '1px solid #E2E8F0',
              background: 'linear-gradient(135deg, #FFFFFF 0%, #F8FAFF 100%)',
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
              <Box>
                <Typography variant="h6" sx={{ fontWeight: 700 }}>
                  Create Survey
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Rider Voice — waseem
                </Typography>
              </Box>
              <Chip
                label="Draft"
                color="warning"
                variant="outlined"
                sx={{ borderRadius: 999, fontWeight: 600 }}
              />
            </Box>

            <Stack spacing={2}>
              <Paper elevation={0} sx={{ p: 2.5, borderRadius: 2, border: '1px solid #E2E8F0' }}>
                <Typography variant="caption" sx={{ fontWeight: 600, color: '#94A3B8' }}>
                  SURVEY TITLE
                </Typography>
                <Typography sx={{ fontSize: 18, fontWeight: 600, mt: 0.5 }}>
                  e.g., Rider Satisfaction Survey
                </Typography>
              </Paper>
              <Paper elevation={0} sx={{ p: 2.5, borderRadius: 2, border: '1px solid #E2E8F0' }}>
                <Typography variant="caption" sx={{ fontWeight: 600, color: '#94A3B8' }}>
                  CLIENT / AGENCY NAME
                </Typography>
                <Typography sx={{ fontWeight: 500, mt: 0.5 }}>e.g., Metro Transit</Typography>
              </Paper>
              <Paper elevation={0} sx={{ p: 2.5, borderRadius: 2, border: '1px solid #E2E8F0' }}>
                <Typography variant="caption" sx={{ fontWeight: 600, color: '#94A3B8' }}>
                  DESCRIPTION
                </Typography>
                <Typography sx={{ mt: 0.5 }}>
                  Brief description of the survey goals and target riders…
                </Typography>
              </Paper>
            </Stack>
          </Paper>

          <Paper
            elevation={0}
            sx={{
              flex: 1,
              borderRadius: 3,
              border: '2px dashed #CBD5F5',
              bgcolor: '#FFFFFF',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              textAlign: 'center',
              gap: 2,
              p: 4,
            }}
          >
            <Box>
              <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>
                No questions yet. Add your first question.
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Drag from the left panel or use quick add buttons below.
              </Typography>
            </Box>

            <Stack direction="row" spacing={1.5} flexWrap="wrap" justifyContent="center">
              {QUICK_ADD_BUTTONS.map((btn) => (
                <Button
                  key={btn.label}
                  variant="contained"
                  size="small"
                  startIcon={<Add fontSize="small" />}
                  sx={{
                    textTransform: 'none',
                    borderRadius: 999,
                    bgcolor: `${btn.color}15`,
                    color: btn.color,
                    fontWeight: 600,
                    '&:hover': {
                      bgcolor: `${btn.color}25`,
                    },
                  }}
                >
                  {btn.label}
                </Button>
              ))}
            </Stack>
          </Paper>

          <Paper elevation={0} sx={{ borderRadius: 3, p: 2.5, border: '1px solid #E2E8F0' }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1 }}>
              Recent drafts
            </Typography>
            <List dense>
              {['Onboard Experience', 'Metro Night Routes', 'Spanish Rider Feedback'].map((item, idx) => (
                <ListItem key={item} sx={{ px: 0 }}>
                  <ListItemIcon>
                    {idx === 0 ? <Description color="primary" /> : <Drafts color="disabled" />}
                  </ListItemIcon>
                  <ListItemText primary={item} secondary="Updated 2h ago" />
                  <IconButton size="small">
                    <ContentCopy fontSize="small" />
                  </IconButton>
                </ListItem>
              ))}
            </List>
          </Paper>
        </Box>

        {/* Right Panel */}
        <Box
          sx={{
            width: 340,
            bgcolor: 'white',
            borderRadius: 3,
            p: 3,
            border: '1px solid #E2E8F0',
            boxShadow: '0 10px 24px rgba(15, 23, 42, 0.08)',
            display: 'flex',
            flexDirection: 'column',
            gap: 3,
          }}
        >
          <Stack spacing={1.5}>
            <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>
              {rightPanel.title}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {rightPanel.description}
            </Typography>
            <Button
              variant="contained"
              startIcon={<Visibility />}
              sx={{
                textTransform: 'none',
                borderRadius: 2,
                bgcolor: '#0EA5E9',
                '&:hover': { bgcolor: '#0284C7' },
              }}
            >
              Preview Survey
            </Button>
          </Stack>

          <Divider />

          <Stack spacing={2}>
            {rightPanel.sections.map((section) => (
              <Box key={section.heading}>
                <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1 }}>
                  {section.heading}
                </Typography>
                <Stack spacing={1}>
                  {section.items.map((item) => (
                    <Stack
                      key={item}
                      direction="row"
                      spacing={1.5}
                      alignItems="center"
                      sx={{
                        border: '1px solid #EEF2FF',
                        borderRadius: 2,
                        p: 1.5,
                      }}
                    >
                      <CheckCircle fontSize="small" sx={{ color: '#7B61FF' }} />
                      <Typography variant="body2">{item}</Typography>
                    </Stack>
                  ))}
                </Stack>
              </Box>
            ))}
          </Stack>

          <Box>
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
              SURVEY HEALTH
            </Typography>
            <LinearProgress variant="determinate" value={62} sx={{ height: 8, borderRadius: 999 }} />
            <Stack direction="row" justifyContent="space-between" sx={{ mt: 0.5 }}>
              <Typography variant="caption" color="text.secondary">
                62% ready
              </Typography>
              <Tooltip title="Complete mandatory settings to publish">
                <HelpOutline fontSize="small" sx={{ color: '#94A3B8' }} />
              </Tooltip>
            </Stack>
          </Box>
        </Box>
      </Box>
    </Box>
  );
};

export default SurveyBuilderSimple;
