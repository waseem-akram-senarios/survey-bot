import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  IconButton,
  Tab,
  Tabs,
  TextField,
  Typography,
  Stack,
  Paper,
  Snackbar,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  Add as AddIcon,
  ArrowBack as ArrowBackIcon,
  Visibility as PreviewIcon,
  Save as SaveIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import { useAuth } from '../../../context/AuthContext';
import { useTemplateAPI } from '../../../hooks/Templates/useTemplates';
import {
  createCategoryQuestion,
  createRatingQuestion,
  createOpenQuestion,
  createFlowQuestion,
  generateUUID,
} from '../../../utils/Templates/templateHelpers';

const QUESTION_TYPE_BUTTONS = [
  { label: 'Multiple Choice', color: '#7B61FF', uiType: 'multiple_choice' },
  { label: 'Open Ended', color: '#FF7AB2', uiType: 'open_ended' },
  { label: 'Yes / No', color: '#00C4B8', uiType: 'yes_no' },
  { label: 'Rating Scale', color: '#FFCF4A', uiType: 'rating_scale' },
  { label: 'NPS Score', color: '#F97316', uiType: 'nps_score' },
  { label: 'Route / Stop', color: '#38BDF8', uiType: 'route_stop' },
  { label: 'Date / Time', color: '#6366F1', uiType: 'date_time' },
];

function buildQuestionFromUiType(uiType) {
  switch (uiType) {
    case 'multiple_choice':
      return createCategoryQuestion(
        { question: 'New multiple choice question', options: ['Option 1', 'Option 2'] },
        false
      );
    case 'open_ended':
      return createOpenQuestion({ question: 'New open-ended question' }, false);
    case 'yes_no':
      return createCategoryQuestion(
        { question: 'New yes/no question', options: ['Yes', 'No'] },
        false
      );
    case 'rating_scale':
      return createRatingQuestion({ question: 'New rating question', maxRange: 5 }, false);
    case 'nps_score':
      return createRatingQuestion({ question: 'How likely are you to recommend us? (0–10)', maxRange: 10 }, false);
    case 'route_stop': {
      return createFlowQuestion({
        parentQuestion: 'Which route or stop?',
        parentOptions: ['Route A', 'Route B'],
        childQuestions: {
          'Route A': [{ question: 'Feedback for Route A', type: 'open' }],
          'Route B': [{ question: 'Feedback for Route B', type: 'open' }],
        },
      });
    }
    case 'date_time':
      return createOpenQuestion({ question: 'Date and time preference?' }, false);
    default:
      return createOpenQuestion({ question: 'New question' }, false);
  }
}

export default function CreateSurveyBuilder() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { createTemplate, saveMultipleQuestions } = useTemplateAPI();

  const [activeTab, setActiveTab] = useState('questions');
  const [surveyTitle, setSurveyTitle] = useState('');
  const [clientName, setClientName] = useState('');
  const [description, setDescription] = useState('');
  const [questions, setQuestions] = useState([]);
  const [saving, setSaving] = useState(false);
  const [snack, setSnack] = useState({ open: false, message: '', severity: 'success' });

  const handleAddQuestion = (uiType) => {
    const q = buildQuestionFromUiType(uiType);
    setQuestions((prev) => [...prev, q]);
  };

  const handleSaveSurvey = async () => {
    const name = surveyTitle?.trim() || `Survey ${new Date().toISOString().slice(0, 10)}`;
    setSaving(true);
    try {
      await createTemplate(name);
      if (questions.length > 0) {
        await saveMultipleQuestions(name, questions);
      }
      setSnack({ open: true, message: 'Survey saved successfully.', severity: 'success' });
      setTimeout(() => navigate('/templates/manage'), 1500);
    } catch (err) {
      setSnack({
        open: true,
        message: err?.message || 'Failed to save survey.',
        severity: 'error',
      });
    } finally {
      setSaving(false);
    }
  };

  const handlePreview = () => {
    setSnack({ open: true, message: 'Preview not implemented for this builder yet.', severity: 'info' });
  };

  return (
    <Box sx={{ minHeight: '100%', bgcolor: 'background.default', pb: 4 }}>
      {/* Page header: Back, Title, Subtitle, Preview, Save */}
      <Box
        sx={{
          bgcolor: 'background.paper',
          borderBottom: '1px solid',
          borderColor: 'divider',
          px: { xs: 2, md: 3 },
          py: 2,
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <IconButton onClick={() => navigate(-1)} size="small" aria-label="Back">
              <ArrowBackIcon />
            </IconButton>
            <Box>
              <Typography variant="h6" sx={{ fontWeight: 700 }}>
                Create Survey
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Rider Voice — {user?.username || 'User'}
              </Typography>
            </Box>
          </Box>
          <Stack direction="row" spacing={1.5}>
            <Button
              variant="outlined"
              size="small"
              startIcon={<PreviewIcon fontSize="small" />}
              onClick={handlePreview}
              sx={{ textTransform: 'none', borderRadius: 999 }}
            >
              Preview
            </Button>
            <Button
              variant="contained"
              size="small"
              startIcon={saving ? <CircularProgress size={16} color="inherit" /> : <SaveIcon fontSize="small" />}
              onClick={handleSaveSurvey}
              disabled={saving}
              sx={{
                textTransform: 'none',
                borderRadius: 999,
                px: 3,
                bgcolor: '#1958F7',
                '&:hover': { bgcolor: '#1346d4' },
              }}
            >
              {saving ? 'Saving…' : 'Save Survey'}
            </Button>
          </Stack>
        </Box>
      </Box>

      {/* Tabs */}
      <Box sx={{ bgcolor: 'background.paper', borderBottom: '1px solid', borderColor: 'divider' }}>
        <Tabs
          value={activeTab}
          onChange={(_, value) => setActiveTab(value)}
          sx={{
            '& .MuiTab-root': { textTransform: 'none', fontWeight: 600, minHeight: 48 },
            '& .Mui-selected': { color: 'primary.main' },
          }}
        >
          <Tab value="questions" label="Questions" />
          <Tab value="settings" label="Settings" icon={<SettingsIcon fontSize="small" />} iconPosition="start" />
          <Tab value="distribution" label="Distribution" />
        </Tabs>
      </Box>

      {/* Content */}
      <Box sx={{ maxWidth: 900, mx: 'auto', px: { xs: 2, md: 3 }, pt: 3 }}>
        {activeTab === 'questions' && (
          <Stack spacing={3}>
            <Paper elevation={0} sx={{ p: 3, borderRadius: 2, border: '1px solid', borderColor: 'divider' }}>
              <Typography variant="overline" sx={{ fontWeight: 600, color: 'text.secondary', display: 'block', mb: 1 }}>
                Survey details
              </Typography>
              <Stack spacing={2}>
                <TextField
                  fullWidth
                  label="Survey title"
                  placeholder="e.g., Rider Satisfaction Survey"
                  value={surveyTitle}
                  onChange={(e) => setSurveyTitle(e.target.value)}
                  size="small"
                />
                <TextField
                  fullWidth
                  label="Client / Agency name"
                  placeholder="e.g., Metro Transit"
                  value={clientName}
                  onChange={(e) => setClientName(e.target.value)}
                  size="small"
                />
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  label="Description"
                  placeholder="Brief description…"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  size="small"
                />
              </Stack>
            </Paper>

            <Typography variant="body2" color="text.secondary">
              {questions.length === 0
                ? 'No questions yet. Add your first question below.'
                : `${questions.length} question(s) added.`}
            </Typography>

            <Paper
              elevation={0}
              sx={{
                p: 3,
                borderRadius: 2,
                border: '2px dashed',
                borderColor: 'primary.light',
                bgcolor: 'background.default',
              }}
            >
              <Typography variant="subtitle1" sx={{ fontWeight: 700, mb: 2 }}>
                Add a question
              </Typography>
              <Stack direction="row" flexWrap="wrap" gap={1.5} useFlexGap>
                {QUESTION_TYPE_BUTTONS.map((btn) => (
                  <Button
                    key={btn.label}
                    variant="contained"
                    size="small"
                    startIcon={<AddIcon fontSize="small" />}
                    onClick={() => handleAddQuestion(btn.uiType)}
                    sx={{
                      textTransform: 'none',
                      borderRadius: 999,
                      bgcolor: `${btn.color}20`,
                      color: btn.color,
                      fontWeight: 600,
                      '&:hover': { bgcolor: `${btn.color}30` },
                    }}
                  >
                    {btn.label}
                  </Button>
                ))}
              </Stack>
            </Paper>

            {questions.length > 0 && (
              <Paper elevation={0} sx={{ p: 2, borderRadius: 2, border: '1px solid', borderColor: 'divider' }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1 }}>
                  Questions in this survey
                </Typography>
                <Stack spacing={0.5}>
                  {questions.map((q, idx) => (
                    <Typography key={q.queId || q.id} variant="body2" color="text.secondary">
                      {idx + 1}. {q.question || (q.type && `Question (${q.type})`)}
                    </Typography>
                  ))}
                </Stack>
              </Paper>
            )}
          </Stack>
        )}

        {activeTab === 'settings' && (
          <Paper elevation={0} sx={{ p: 3, borderRadius: 2, border: '1px solid', borderColor: 'divider' }}>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
              Survey settings
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Branding, language, and survey experience. Configure after saving from the template.
            </Typography>
          </Paper>
        )}

        {activeTab === 'distribution' && (
          <Paper elevation={0} sx={{ p: 3, borderRadius: 2, border: '1px solid', borderColor: 'divider' }}>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
              Distribution
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Share this survey via SMS, email, or web link after creating it from Templates or Surveys.
            </Typography>
          </Paper>
        )}
      </Box>

      <Snackbar
        open={snack.open}
        autoHideDuration={6000}
        onClose={() => setSnack((s) => ({ ...s, open: false }))}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert severity={snack.severity} onClose={() => setSnack((s) => ({ ...s, open: false }))}>
          {snack.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}
