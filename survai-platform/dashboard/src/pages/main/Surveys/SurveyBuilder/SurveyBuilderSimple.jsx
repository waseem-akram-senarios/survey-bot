import React, { useMemo, useState } from 'react';
import {
  Avatar,
  Box,
  Button,
  Chip,
  Divider,
  IconButton,
  Paper,
  Snackbar,
  Alert as MuiAlert,
  Stack,
  Tab,
  Tabs,
  TextField,
  MenuItem,
  Select,
  FormControl,
  Typography,
  InputLabel,
} from '@mui/material';
import {
  Add,
  ArrowBack,
  CalendarMonth,
  CheckCircle,
  ContentCopy,
  Description,
  Drafts,
  HelpOutline,
  InsertChartOutlined,
  Phone as PhoneIcon,
  Public,
  QrCode2,
  RadioButtonChecked,
  Save,
  Star,
  TextFields,
  Visibility,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../../../context/AuthContext';
import ApiBaseHelper from '../../../../network/apiBaseHelper';
import ApiLinks, { RECIPIENT_BASE } from '../../../../network/apiLinks';
import { useTemplateAPI } from '../../../../hooks/Templates/useTemplates';
import { useSurvey } from '../../../../hooks/Surveys/useSurvey';

const QUESTION_TYPES = [
  { label: 'Multiple Choice', description: 'Respondents select one option', icon: RadioButtonChecked, color: '#7B61FF', type: 'multiple_choice' },
  { label: 'Open Ended', description: 'Short or long text responses', icon: TextFields, color: '#FF7AB2', type: 'open_ended' },
  { label: 'Yes / No', description: 'Binary decision question', icon: CheckCircle, color: '#00C4B8', type: 'yes_no' },
  { label: 'Rating Scale', description: 'Measure satisfaction on a scale', icon: Star, color: '#FFCF4A', type: 'rating_scale' },
  { label: 'NPS Score', description: 'Net promoter score question', icon: InsertChartOutlined, color: '#F97316', type: 'nps' },
  { label: 'Route / Stop', description: 'Transit or route based question', icon: ContentCopy, color: '#38BDF8', type: 'route_stop' },
  { label: 'Date / Time', description: 'Collect scheduling preferences', icon: CalendarMonth, color: '#6366F1', type: 'date_time' },
];

const SurveyBuilderSimple = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { createTemplate, saveMultipleQuestions, updateTemplateStatus } = useTemplateAPI();
  const { generateSurvey, launchSurvey } = useSurvey();
  const [activeTab, setActiveTab] = useState('questions');
  const [saving, setSaving] = useState(false);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });

  // Survey form state
  const [surveyTitle, setSurveyTitle] = useState('');
  const [clientName, setClientName] = useState('');
  const [description, setDescription] = useState('');
  const [questions, setQuestions] = useState([]);

  // Settings state
  const [status, setStatus] = useState('Draft');
  const [phoneNumber, setPhoneNumber] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  const showNotification = (message, severity = 'success') =>
    setNotification({ open: true, message, severity });

  const addQuestion = (type) => {
    const qt = QUESTION_TYPES.find(q => q.type === type);
    setQuestions(prev => [...prev, {
      id: Date.now(),
      type: type,
      label: qt?.label || type,
      text: '',
      options: type === 'multiple_choice' ? ['Option 1', 'Option 2'] : [],
    }]);
    showNotification(`${qt?.label || type} question added`);
  };

  const removeQuestion = (id) => {
    setQuestions(prev => prev.filter(q => q.id !== id));
  };

  const updateQuestionText = (id, text) => {
    setQuestions(prev => prev.map(q => q.id === id ? { ...q, text } : q));
  };

  const handleSaveSurvey = async () => {
    if (!surveyTitle.trim()) {
      showNotification('Please enter a survey title', 'warning');
      return;
    }
    setSaving(true);
    try {
      // 1. Create Template
      const templateRes = await createTemplate(surveyTitle);
      
      // 2. Save Questions to Template
      if (questions.length > 0) {
        const formattedQuestions = questions.map((q, i) => {
          let type = 'category';
          if (q.type === 'open_ended' || q.type === 'date_time' || q.type === 'route_stop') type = 'open';
          if (q.type === 'rating_scale' || q.type === 'nps') type = 'rating';
          
          let options = q.options || [];
          if (q.type === 'yes_no') options = ['Yes', 'No'];
          
          let maxRange = null;
          if (q.type === 'rating_scale') maxRange = 5;
          if (q.type === 'nps') maxRange = 10;
          
          return {
            id: q.id,
            queId: null,
            isSaved: false,
            question: q.text || `Question ${i + 1}`,
            type: type,
            options: options,
            maxRange: maxRange,
            autofill: 'No'
          };
        });
        
        await saveMultipleQuestions(surveyTitle, formattedQuestions);
      }

      // 3. Generate Survey from Template
      const surveyId = crypto.randomUUID();
      const surveyData = {
        surveyId: surveyId,
        template: surveyTitle,
        recipient: clientName || 'General',
        biodata: description,
        tenantId: user?.tenantId || '',
        phone: phoneNumber,
        riderName: '',
        rideId: '',
      };
      
      const generatedSurvey = await generateSurvey(surveyData);

      // 4. Update Status & Launch if not Draft
      if (status !== 'Draft') {
        await launchSurvey(generatedSurvey, generatedSurvey.questions || [], true);
      } else {
        await updateTemplateStatus(surveyTitle, 'Draft');
      }

      showNotification('Survey saved successfully!');
      setTimeout(() => navigate('/dashboard'), 1500);
    } catch (err) {
      console.error('Error saving survey:', err);
      showNotification(err.message || 'Failed to save survey. Please try again.', 'error');
    } finally {
      setSaving(false);
    }
  };

  // ─── Questions Tab Content ─────────────────────────────────────────────
  const QuestionsContent = () => (
    <>
      {/* Survey info form */}
      <Paper elevation={0} sx={{ borderRadius: 3, p: 3, border: '1px solid #E2E8F0', mb: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 700 }}>Create Survey</Typography>
            <Typography variant="body2" color="text.secondary">Rider Voice — {user?.username || 'waseem'}</Typography>
          </Box>
        </Box>
        <Stack spacing={2}>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Box sx={{ flex: 1 }}>
              <Typography variant="caption" sx={{ fontWeight: 600, color: '#94A3B8', textTransform: 'uppercase', mb: 0.5, display: 'block' }}>Survey Title</Typography>
              <TextField fullWidth size="small" placeholder="e.g., Rider Satisfaction Survey" value={surveyTitle} onChange={(e) => setSurveyTitle(e.target.value)}
                sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2, bgcolor: '#fff' } }} />
            </Box>
            <Box sx={{ flex: 1 }}>
              <Typography variant="caption" sx={{ fontWeight: 600, color: '#94A3B8', textTransform: 'uppercase', mb: 0.5, display: 'block' }}>Client/Agency Name</Typography>
              <TextField fullWidth size="small" placeholder="e.g., Metro Transit" value={clientName} onChange={(e) => setClientName(e.target.value)}
                sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2, bgcolor: '#fff' } }} />
            </Box>
          </Box>
          <Box>
            <Typography variant="caption" sx={{ fontWeight: 600, color: '#94A3B8', textTransform: 'uppercase', mb: 0.5, display: 'block' }}>Description</Typography>
            <TextField fullWidth multiline rows={3} size="small" placeholder="Brief description..." value={description} onChange={(e) => setDescription(e.target.value)}
              sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2, bgcolor: '#fff' } }} />
          </Box>
        </Stack>
      </Paper>

      {/* Added Questions */}
      {questions.length > 0 && (
        <Paper elevation={0} sx={{ borderRadius: 3, p: 3, border: '1px solid #E2E8F0', mb: 2 }}>
          <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 2 }}>Questions ({questions.length})</Typography>
          <Stack spacing={2}>
            {questions.map((q, idx) => {
              const qt = QUESTION_TYPES.find(t => t.type === q.type);
              const QIcon = qt?.icon || Description;
              return (
                <Paper key={q.id} elevation={0} sx={{ border: '1px solid #EEF2FF', borderRadius: 2, p: 2, display: 'flex', alignItems: 'flex-start', gap: 2 }}>
                  <Box sx={{ width: 36, height: 36, borderRadius: 1.5, bgcolor: `${qt?.color || '#6366f1'}15`, display: 'flex', alignItems: 'center', justifyContent: 'center', color: qt?.color || '#6366f1', flexShrink: 0, mt: 0.5 }}>
                    <QIcon fontSize="small" />
                  </Box>
                  <Box sx={{ flex: 1 }}>
                    <Chip label={q.label} size="small" sx={{ mb: 1, bgcolor: `${qt?.color || '#6366f1'}15`, color: qt?.color || '#6366f1', fontWeight: 600, fontSize: '11px' }} />
                    <TextField fullWidth size="small" placeholder={`Enter your ${q.label.toLowerCase()} question...`} value={q.text} onChange={(e) => updateQuestionText(q.id, e.target.value)}
                      sx={{ '& .MuiOutlinedInput-root': { borderRadius: 1.5 } }} />
                  </Box>
                  <IconButton size="small" onClick={() => removeQuestion(q.id)} sx={{ color: '#ef4444', mt: 0.5 }}>✕</IconButton>
                </Paper>
              );
            })}
          </Stack>
        </Paper>
      )}

      {/* Empty state / Quick add */}
      <Paper elevation={0} sx={{ borderRadius: 3, border: '2px dashed #CBD5F5', bgcolor: '#FFFFFF', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center', gap: 2, p: 4, minHeight: 200 }}>
        <Typography color="text.secondary" sx={{ fontWeight: 500 }}>
          {questions.length === 0 ? 'No questions yet. Add your first question below.' : 'Add a question'}
        </Typography>
        <Stack direction="row" spacing={1.5} flexWrap="wrap" justifyContent="center" useFlexGap>
          {QUESTION_TYPES.map((btn) => (
            <Button key={btn.label} variant="contained" size="small" startIcon={<Add fontSize="small" />}
              onClick={() => addQuestion(btn.type)}
              sx={{ textTransform: 'none', borderRadius: 999, bgcolor: `${btn.color}15`, color: btn.color, fontWeight: 600, boxShadow: 'none', '&:hover': { bgcolor: `${btn.color}25`, boxShadow: 'none' } }}>
              {btn.label}
            </Button>
          ))}
        </Stack>
      </Paper>
    </>
  );

  // ─── Settings Tab Content ──────────────────────────────────────────────
  const SettingsContent = () => (
    <Paper elevation={0} sx={{ borderRadius: 3, p: 4, border: '1px solid #E2E8F0' }}>
      <Typography variant="h6" sx={{ fontWeight: 700, mb: 3 }}>Survey Settings</Typography>
      <Box sx={{ display: 'flex', gap: 3, mb: 3 }}>
        <Box sx={{ flex: 1 }}>
          <Typography variant="caption" sx={{ fontWeight: 600, color: '#94A3B8', textTransform: 'uppercase', mb: 0.5, display: 'block' }}>Status</Typography>
          <FormControl fullWidth size="small">
            <Select value={status} onChange={(e) => setStatus(e.target.value)}
              sx={{ borderRadius: 2, bgcolor: '#fff' }}>
              <MenuItem value="Draft">Draft</MenuItem>
              <MenuItem value="Active">Active</MenuItem>
              <MenuItem value="Completed">Completed</MenuItem>
              <MenuItem value="Pending">Pending</MenuItem>
            </Select>
          </FormControl>
        </Box>
        <Box sx={{ flex: 1 }}>
          <Typography variant="caption" sx={{ fontWeight: 600, color: '#94A3B8', textTransform: 'uppercase', mb: 0.5, display: 'block' }}>Phone Number (for voice surveys)</Typography>
          <TextField fullWidth size="small" placeholder="+1 (555) 123-4567" value={phoneNumber} onChange={(e) => setPhoneNumber(e.target.value)}
            sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2, bgcolor: '#fff' } }} />
        </Box>
      </Box>
      <Box sx={{ display: 'flex', gap: 3 }}>
        <Box sx={{ flex: 1 }}>
          <Typography variant="caption" sx={{ fontWeight: 600, color: '#6366f1', textTransform: 'uppercase', mb: 0.5, display: 'block' }}>Start Date</Typography>
          <TextField fullWidth size="small" type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)}
            InputLabelProps={{ shrink: true }}
            sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2, bgcolor: '#fff' } }} />
        </Box>
        <Box sx={{ flex: 1 }}>
          <Typography variant="caption" sx={{ fontWeight: 600, color: '#6366f1', textTransform: 'uppercase', mb: 0.5, display: 'block' }}>End Date</Typography>
          <TextField fullWidth size="small" type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)}
            InputLabelProps={{ shrink: true }}
            sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2, bgcolor: '#fff' } }} />
        </Box>
      </Box>
    </Paper>
  );

  // ─── Distribution Tab Content ──────────────────────────────────────────
  const DistributionContent = () => {
    const channels = [
      {
        title: 'Phone Survey',
        description: 'Respondents call or receive calls from the AI survey agent',
        subtext: phoneNumber ? `Phone: ${phoneNumber}` : 'Set phone number in settings',
        icon: <PhoneIcon sx={{ fontSize: 40 }} />,
        bgColor: '#e0f7f5',
        iconColor: '#00C4B8',
      },
      {
        title: 'Web Survey',
        description: 'Share a link for respondents to complete online',
        subtext: surveyTitle ? 'Ready to generate link' : 'Save the survey first',
        icon: <Public sx={{ fontSize: 40 }} />,
        bgColor: '#eef2ff',
        iconColor: '#6366f1',
      },
      {
        title: 'QR Code',
        description: 'Print on buses — riders scan to take the survey',
        subtext: surveyTitle ? 'Ready to generate QR' : 'Save the survey first to generate a QR code',
        icon: <QrCode2 sx={{ fontSize: 40 }} />,
        bgColor: '#f5f3ff',
        iconColor: '#8b5cf6',
      },
    ];

    return (
      <Box sx={{ display: 'flex', gap: 3 }}>
        {channels.map((ch) => (
          <Paper key={ch.title} elevation={0} sx={{
            flex: 1, borderRadius: 3, border: '1px solid #E2E8F0', p: 4,
            display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', gap: 2,
            transition: 'all 0.2s', '&:hover': { boxShadow: '0 8px 20px rgba(0,0,0,0.08)', transform: 'translateY(-2px)' },
          }}>
            <Box sx={{ width: 80, height: 80, borderRadius: '50%', bgcolor: ch.bgColor, display: 'flex', alignItems: 'center', justifyContent: 'center', color: ch.iconColor }}>
              {ch.icon}
            </Box>
            <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>{ch.title}</Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>{ch.description}</Typography>
            <Typography variant="caption" color="text.secondary">{ch.subtext}</Typography>
          </Paper>
        ))}
      </Box>
    );
  };

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#F5F6FA', display: 'flex', flexDirection: 'column' }}>
      {/* Sub-Header for Builder */}
      <Paper elevation={0} sx={{ borderBottom: '1px solid #E5E7EB', px: 3, py: 1.5, borderRadius: 0 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <IconButton onClick={() => navigate('/dashboard')} size="small">
              <ArrowBack />
            </IconButton>
            <Box>
              <Typography variant="h6" sx={{ fontWeight: 700, lineHeight: 1.2 }}>Create Survey</Typography>
              <Typography variant="caption" color="text.secondary">Rider Voice — {user?.username || 'waseem'}</Typography>
            </Box>
          </Box>
          <Stack direction="row" spacing={1.5} alignItems="center">
            <Button variant="outlined" size="small" startIcon={<Visibility />}
              sx={{ textTransform: 'none', borderRadius: 999, borderColor: '#E5E7EB', color: '#374151' }}>
              Preview
            </Button>
            <Button variant="contained" size="small" startIcon={<Save />}
              onClick={handleSaveSurvey} disabled={saving}
              sx={{ textTransform: 'none', borderRadius: 999, px: 3, bgcolor: '#7B61FF', '&:hover': { bgcolor: '#6B4FE0' } }}>
              {saving ? 'Saving...' : 'Save Survey'}
            </Button>
          </Stack>
        </Box>
      </Paper>

      {/* Tabs */}
      <Box sx={{ bgcolor: 'white', borderBottom: '1px solid #E5E7EB' }}>
        <Tabs value={activeTab} onChange={(_, value) => setActiveTab(value)} textColor="secondary"
          TabIndicatorProps={{ style: { display: 'none' } }}
          sx={{
            px: 2,
            '& .MuiTab-root': { textTransform: 'none', fontWeight: 600, color: '#6B7280', minHeight: 48 },
            '& .Mui-selected': { color: '#7B61FF', bgcolor: '#F2ECFF', borderRadius: 999, mx: 0.5 },
          }}>
          <Tab value="questions" label="Questions" />
          <Tab value="settings" icon={null} label="Settings" iconPosition="start" />
          <Tab value="distribution" label="Distribution" />
        </Tabs>
      </Box>

      {/* Workspace */}
      <Box sx={{ flex: 1, p: 3, maxWidth: 960, mx: 'auto', width: '100%' }}>
        {activeTab === 'questions' && <QuestionsContent />}
        {activeTab === 'settings' && <SettingsContent />}
        {activeTab === 'distribution' && <DistributionContent />}
      </Box>

      {/* Notification */}
      <Snackbar open={notification.open} autoHideDuration={3000}
        onClose={() => setNotification(n => ({ ...n, open: false }))}
        anchorOrigin={{ vertical: 'top', horizontal: 'right' }}>
        <MuiAlert onClose={() => setNotification(n => ({ ...n, open: false }))}
          severity={notification.severity} sx={{ width: '100%' }}>
          {notification.message}
        </MuiAlert>
      </Snackbar>
    </Box>
  );
};

export default SurveyBuilderSimple;
