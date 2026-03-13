import React, { useState, useRef } from 'react';
import {
  Box,
  Typography,
  Button,
  TextField,
  MenuItem,
  Select,
  FormControl,
  InputAdornment,
  Grid,
  CircularProgress,
  Card,
  CardContent,
  Snackbar,
  Alert,
  Chip,
  Paper,
  Popper,
  ClickAwayListener,
  Grow,
} from '@mui/material';
import {
  Plus,
  Search,
  Star,
  PhoneCall,
  Users,
  AlertCircle,
  BarChart3,
  MoreVertical,
  Globe,
  QrCode,
  Phone,
  BarChart2,
  Edit,
  BarChart,
  UserPlus,
  Copy,
  CalendarClock,
  Trash2,
  TrendingUp,
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useDashboard } from '../hooks/Surveys/useSurveyTable';
import { useAuth } from '../context/AuthContext';

// ─── Status config ────────────────────────────────────────────────────────────
const statusColors = {
  Active: { bg: '#ecfdf5', color: '#059669', label: 'Active' },
  Completed: { bg: '#ecfdf5', color: '#059669', label: 'Completed' },
  'In-Progress': { bg: '#eef2ff', color: '#4f46e5', label: 'In-Progress' },
  Draft: { bg: '#fff7ed', color: '#d97706', label: 'Draft' },
  Pending: { bg: '#fefce8', color: '#ca8a04', label: 'Pending' },
};

// ─── Inline StatCard — text LEFT, icon RIGHT with proper gap ─────────────────
const StatCard = ({ title, value, subValue, icon: Icon, color, trend }) => (
  <Card sx={{
    borderRadius: '14px',
    border: '1px solid #e5e7eb',
    boxShadow: '0 1px 4px rgba(0,0,0,0.06)',
    height: '100%',
  }}>
    <Box sx={{ height: 4, borderRadius: '14px 14px 0 0', bgcolor: color }} />
    <CardContent sx={{ p: 2.5 }}>
      {/* Row: text LEFT — icon RIGHT */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 2 }}>
        {/* Left side */}
        <Box sx={{ minWidth: 0, flex: 1 }}>
          <Typography
            variant="caption"
            sx={{
              fontWeight: 700,
              color: '#9ca3af',
              fontSize: '11px',
              letterSpacing: '0.08em',
              textTransform: 'uppercase',
              display: 'block',
              mb: 0.75,
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
            }}
          >
            {title}
          </Typography>
          <Typography
            variant="h4"
            sx={{ fontWeight: 800, color: '#111827', fontSize: '2rem', lineHeight: 1.1 }}
          >
            {value}
          </Typography>
        </Box>

        {/* Right side: colored icon */}
        <Box sx={{
          bgcolor: color,
          borderRadius: '12px',
          width: 52,
          height: 52,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0,
          boxShadow: `0 4px 14px ${color}55`,
        }}>
          <Icon size={24} color="#fff" />
        </Box>
      </Box>

      {/* Sub value */}
      <Typography variant="body2" sx={{ color: '#6b7280', fontSize: '12px', mt: 1 }}>
        {subValue}
      </Typography>

      {/* Trend */}
      {trend > 0 && (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mt: 0.75 }}>
          <TrendingUp size={13} color="#10b981" />
          <Typography variant="caption" sx={{ color: '#10b981', fontWeight: 700 }}>
            +{trend}%
          </Typography>
        </Box>
      )}
    </CardContent>
  </Card>
);

// ─── Context Dropdown Menu 
const SurveyContextMenu = ({ anchorEl, open, onClose, actions }) => (
  <Popper open={open} anchorEl={anchorEl} placement="bottom-end" transition style={{ zIndex: 1400 }}>
    {({ TransitionProps }) => (
      <Grow {...TransitionProps} timeout={120}>
        <Paper
          elevation={6}
          sx={{
            borderRadius: '10px',
            minWidth: 210,
            overflow: 'hidden',
            border: '1px solid #f3f4f6',
            boxShadow: '0 8px 30px rgba(0,0,0,0.14)',
            mt: 0.5,
          }}
        >
          <ClickAwayListener onClickAway={onClose}>
            <Box sx={{ py: 0.75 }}>
              {actions.map((item, idx) =>
                item.divider ? (
                  <Box key={idx} sx={{ my: 0.5, borderTop: '1px solid #f3f4f6' }} />
                ) : (
                  <Box
                    key={idx}
                    onClick={(e) => { e.stopPropagation(); item.action?.(); onClose(); }}
                    sx={{
                      display: 'flex', alignItems: 'center', gap: 1.5,
                      px: 2, py: 1, cursor: 'pointer',
                      color: item.danger ? '#ef4444' : '#1f2937',
                      fontSize: '14px', fontWeight: 500,
                      '&:hover': { bgcolor: item.danger ? '#fff5f5' : '#f9fafb' },
                      transition: 'background 0.12s',
                    }}
                  >
                    <Box sx={{ color: item.danger ? '#ef4444' : '#6b7280', display: 'flex', alignItems: 'center' }}>
                      {item.icon}
                    </Box>
                    {item.label}
                  </Box>
                )
              )}
            </Box>
          </ClickAwayListener>
        </Paper>
      </Grow>
    )}
  </Popper>
);

// ─── Survey Card 
const SurveyCard = ({ survey, onView, onEdit, onDelete, onCopyLink, onAnalytics, onContacts, onSchedule }) => {
  const [menuOpen, setMenuOpen] = useState(false);
  const menuAnchorRef = useRef(null);

  const name = survey.name || survey.Name || 'Untitled';
  const recipient = survey.recipient || survey.Recipient || 'Recipients';
  const description = survey.description || survey.Description || '';
  const status = survey.status || survey.Status || 'Draft';
  const questions = survey.questions || survey.Questions || survey.questionCount || 0;
  const responses = survey.responses || survey.Responses || survey.responseCount || 0;
  const surveyId = survey.surveyId || survey.SurveyId || survey.id || '';
  const statusStyle = statusColors[status] || statusColors.Draft;

  const accentGradient =
    statusStyle.color === '#059669' ? 'linear-gradient(90deg,#10b981,#34d399)' :
      statusStyle.color === '#4f46e5' ? 'linear-gradient(90deg,#6366f1,#818cf8)' :
        statusStyle.color === '#d97706' ? 'linear-gradient(90deg,#f59e0b,#fbbf24)' :
          'linear-gradient(90deg,#e5e7eb,#d1d5db)';

  const menuActions = [
    { icon: <Edit size={16} />, label: 'Edit Survey', action: () => onEdit?.(surveyId, survey) },
    { icon: <BarChart size={16} />, label: 'View Analytics', action: () => onAnalytics?.(surveyId, survey) },
    { icon: <UserPlus size={16} />, label: 'Manage Contacts', action: () => onContacts?.(surveyId, survey) },
    { icon: <Copy size={16} />, label: 'Copy Survey Link', action: () => onCopyLink?.(surveyId) },
    { divider: true },
    { icon: <CalendarClock size={16} />, label: 'Mark Scheduled', action: () => onSchedule?.(surveyId, survey) },
    { divider: true },
    { icon: <Trash2 size={16} />, label: 'Delete', action: () => onDelete?.(surveyId, survey), danger: true },
  ];

  return (
    <>
      <Card
        sx={{
          borderRadius: '12px', border: '1px solid #e5e7eb',
          boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
          transition: 'box-shadow 0.2s, transform 0.2s',
          '&:hover': { boxShadow: '0 4px 16px rgba(0,0,0,0.10)', transform: 'translateY(-2px)' },
          cursor: 'pointer', overflow: 'visible',
        }}
        onClick={() => onView(surveyId, survey)}
      >
        <Box sx={{ height: 4, borderRadius: '12px 12px 0 0', background: accentGradient }} />

        <CardContent sx={{ p: 2.5 }}>
          {/* Title + status + ⋮ */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 0.5 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap', flex: 1, mr: 1 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 700, color: '#111827', fontSize: '15px' }}>
                {name}
              </Typography>
              <Chip
                label={statusStyle.label} size="small"
                sx={{ bgcolor: statusStyle.bg, color: statusStyle.color, fontWeight: 700, fontSize: '11px', borderRadius: '20px', height: 22, px: 0.5 }}
              />
            </Box>

            {/* ⋮ button — click opens dropdown */}
            <Box
              ref={menuAnchorRef}
              onClick={(e) => { e.stopPropagation(); setMenuOpen((p) => !p); }}
              sx={{
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                width: 28, height: 28, borderRadius: '6px', cursor: 'pointer', flexShrink: 0,
                color: '#9ca3af',
                '&:hover': { bgcolor: '#f3f4f6', color: '#374151' },
                transition: 'background 0.15s',
              }}
            >
              <MoreVertical size={16} />
            </Box>
          </Box>

          <Typography variant="body2" sx={{ color: '#6b7280', mb: 0.5, fontSize: '13px' }}>{recipient}</Typography>

          {description && (
            <Typography variant="body2" sx={{ color: '#9ca3af', mb: 1.5, fontSize: '12px', lineHeight: 1.4 }}>
              {description.length > 80 ? description.slice(0, 80) + '…' : description}
            </Typography>
          )}

          {/* Stat icons */}
          <Box sx={{ display: 'flex', gap: 1.5, mb: 1.5, flexWrap: 'wrap' }}>
            {[BarChart2, Star, Phone].map((Icon, i) => (
              <Box key={i} sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <Box sx={{ bgcolor: '#f3f4f6', borderRadius: '6px', p: 0.6, display: 'flex' }}>
                  <Icon size={14} color="#6b7280" />
                </Box>
                <Typography variant="caption" sx={{ color: '#9ca3af' }}>—</Typography>
              </Box>
            ))}
          </Box>

          {/* Channel icons */}
          <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
            {[Phone, Globe, QrCode].map((Icon, i) => (
              <Box key={i} sx={{ bgcolor: '#f3f4f6', borderRadius: '6px', p: 0.6, display: 'flex' }}>
                <Icon size={14} color="#9ca3af" />
              </Box>
            ))}
          </Box>

          {/* Response area */}
          {responses === 0 ? (
            <Box sx={{ bgcolor: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '8px', p: 1.5, mb: 2 }}>
              <Typography variant="body2" sx={{ color: '#374151', fontWeight: 600, mb: 0.5, fontSize: '13px' }}>
                No responses yet
              </Typography>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Typography variant="caption"
                  onClick={(e) => { e.stopPropagation(); onCopyLink?.(surveyId); }}
                  sx={{ color: '#059669', textDecoration: 'underline', cursor: 'pointer', fontWeight: 500 }}>
                  Share survey link
                </Typography>
                <Typography variant="caption" sx={{ color: '#9ca3af' }}>·</Typography>
                <Typography variant="caption"
                  onClick={(e) => { e.stopPropagation(); onContacts?.(surveyId, survey); }}
                  sx={{ color: '#059669', textDecoration: 'underline', cursor: 'pointer', fontWeight: 500 }}>
                  Manage contacts
                </Typography>
              </Box>
            </Box>
          ) : (
            <Box sx={{ bgcolor: '#eef2ff', borderRadius: '8px', p: 1.5, mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
              <Users size={14} color="#6366f1" />
              <Typography variant="body2" sx={{ color: '#4f46e5', fontWeight: 600, fontSize: '13px' }}>
                {responses} response{responses !== 1 ? 's' : ''}
              </Typography>
            </Box>
          )}

          {/* Footer */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="caption" sx={{ color: '#9ca3af' }}>
              {questions} question{questions !== 1 ? 's' : ''}
            </Typography>
            <Button
              size="small" startIcon={<BarChart2 size={14} />}
              onClick={(e) => { e.stopPropagation(); onAnalytics?.(surveyId, survey); }}
              variant="outlined"
              sx={{
                textTransform: 'none', fontWeight: 600, fontSize: '12px',
                borderRadius: '8px', borderColor: '#e5e7eb', color: '#374151',
                py: 0.5, px: 1.5,
                '&:hover': { bgcolor: '#f9fafb', borderColor: '#d1d5db' },
              }}
            >
              Analytics
            </Button>
          </Box>
        </CardContent>
      </Card>

      <SurveyContextMenu
        anchorEl={menuAnchorRef.current}
        open={menuOpen}
        onClose={() => setMenuOpen(false)}
        actions={menuActions}
      />
    </>
  );
};

// ─── Empty State 
const EmptyState = ({ hasFilters, onCreateSurvey }) => (
  <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', py: 10, px: 4 }}>
    <Box sx={{ bgcolor: '#eef2ff', borderRadius: '20px', p: 3, mb: 3, display: 'inline-flex' }}>
      <BarChart2 size={48} color="#6366f1" />
    </Box>
    <Typography variant="h5" sx={{ fontWeight: 700, mb: 1.5, color: '#1f2937' }}>
      {hasFilters ? 'No matching surveys found' : 'No surveys yet'}
    </Typography>
    <Typography variant="body1" sx={{ color: '#6b7280', mb: 4, textAlign: 'center', maxWidth: 360 }}>
      {hasFilters ? "Try adjusting your search or filters." : 'Create your first survey to start collecting rider feedback.'}
    </Typography>
    {!hasFilters && (
      <Button
        variant="contained" startIcon={<Plus size={18} />} onClick={onCreateSurvey}
        sx={{
          py: 1.5, px: 4, borderRadius: '10px', background: '#6366f1',
          textTransform: 'none', fontWeight: 600, fontSize: '15px',
          boxShadow: '0 4px 14px rgba(99,102,241,0.4)',
          '&:hover': { background: '#4f46e5' },
        }}
      >
        Create Your First Survey
      </Button>
    )}
  </Box>
);

// ─── Main Dashboard
const DashboardNew = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { statsData, tableData, tableLoading, tableError, globalLoading } = useDashboard();

  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });

  const showNotification = (message, severity = 'success') =>
    setNotification({ open: true, message, severity });

  const filteredSurveys = (tableData || []).filter(survey => {
    const matchesSearch =
      searchTerm === '' ||
      (survey.name || survey.Name || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (survey.recipient || survey.Recipient || '').toLowerCase().includes(searchTerm.toLowerCase());
    const status = survey.status || survey.Status || '';
    const matchesFilter = statusFilter === 'all' || status.toLowerCase() === statusFilter.toLowerCase();
    return matchesSearch && matchesFilter;
  });


  const totalSurveys = statsData?.Total_Surveys ?? statsData?.totalSurveys ?? tableData?.length ?? 0;
  const activeSurveys = statsData?.Active_Surveys ?? statsData?.activeSurveys ?? 0;
  const completedSurveys = statsData?.Total_Completed_Surveys ?? statsData?.completedSurveys ?? 0;
  const totalTemplates = statsData?.Total_Templates ?? statsData?.totalTemplates ?? 0;
  const publishedTemplates = statsData?.Published_Templates ?? statsData?.publishedTemplates ?? 0;

  const handleView = (id, s) => id && navigate(`/surveys/status/${id}`, { state: { surveyData: s } });
  const handleEdit = (id, s) => id && navigate(`/surveys/edit/${id}`, { state: { surveyData: s } });
  const handleAnalytics = (id, s) => id && navigate(`/surveys/status/${id}`, { state: { surveyData: s } });
  const handleContacts = (id, s) => id && navigate(`/surveys/contacts/${id}`, { state: { surveyData: s } });
  const handleSchedule = () => showNotification('Survey marked as scheduled');
  const handleDelete = () => showNotification('Delete feature coming soon', 'warning');
  const handleCopyLink = (id) => {
    const link = `${window.location.origin}/survey/${id}`;
    navigator.clipboard?.writeText(link).then(() => showNotification('Survey link copied!'));
  };

  if (globalLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '70vh' }}>
        <CircularProgress size={60} sx={{ color: '#6366f1' }} />
      </Box>
    );
  }

  const hasFilters = searchTerm !== '' || statusFilter !== 'all';

  return (
    <Box sx={{ p: { xs: 2, md: 4 }, maxWidth: 1400, mx: 'auto', width: '100%' }}>

      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" sx={{ fontWeight: 800, color: '#1f2937', mb: 1, fontSize: { xs: '2rem', md: '2.5rem' } }}>
          Dashboard
        </Typography>
        <Typography variant="h6" sx={{ color: '#6b7280', fontWeight: 400 }}>
          Welcome back{user?.username ? `, ${user.username}` : ''} — Survey Management Overview
        </Typography>
      </Box>

      {/* Stat Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={2.4}>
          <StatCard title="TOTAL SURVEYS" value={totalSurveys} subValue={`${activeSurveys} active`} icon={BarChart3} color="#6366f1" trend={totalSurveys > 0 ? 12 : 0} />
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <StatCard title="ACTIVE SURVEYS" value={activeSurveys} subValue={`${completedSurveys} completed`} icon={Users} color="#10b981" trend={activeSurveys > 0 ? 5 : 0} />
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <StatCard title="TEMPLATES" value={totalTemplates} subValue={`${publishedTemplates} published`} icon={Star} color="#f59e0b" trend={totalTemplates > 0 ? 8 : 0} />
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <StatCard
            title="COMPLETION RATE"
            value={totalSurveys > 0 ? Math.round((completedSurveys / totalSurveys) * 100) + '%' : '0%'}
            subValue={`${completedSurveys} completed`}
            icon={PhoneCall} color="#8b5cf6" trend={completedSurveys > 0 ? 15 : 0}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <StatCard title="FLAGGED" value="0" subValue="No issues" icon={AlertCircle} color="#ef4444" trend={0} />
        </Grid>
      </Grid>

      {/* Quick Actions + Recent Activity */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={8}>
          <Card sx={{ borderRadius: '12px', border: '1px solid #e5e7eb' }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ fontWeight: 700, mb: 3, color: '#1f2937' }}>Quick Actions</Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6} md={4}>
                  <Button variant="contained" startIcon={<Plus size={18} />}
                    onClick={() => navigate('/surveys/launch')}
                    sx={{
                      width: '100%', py: 2,
                      background: 'linear-gradient(135deg,#667eea 0%,#764ba2 100%)',
                      textTransform: 'none', fontWeight: 600, borderRadius: '8px',
                      boxShadow: '0 4px 14px 0 rgba(79,70,229,0.39)',
                      '&:hover': { transform: 'translateY(-2px)', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)' },
                    }}>
                    Launch Survey
                  </Button>
                </Grid>
                <Grid item xs={12} sm={6} md={4}>
                  <Button variant="outlined" startIcon={<Plus size={18} />}
                    onClick={() => navigate('/templates/create')}
                    sx={{
                      width: '100%', py: 2, borderColor: '#6366f1', color: '#6366f1',
                      textTransform: 'none', fontWeight: 600, borderRadius: '8px',
                      '&:hover': { borderColor: '#4f46e5', bgcolor: '#f3f4f6' },
                    }}>
                    Create Template
                  </Button>
                </Grid>
                <Grid item xs={12} sm={6} md={4}>
                  <Button variant="text" startIcon={<BarChart3 size={18} />}
                    onClick={() => navigate('/analytics')}
                    sx={{
                      width: '100%', py: 2, color: '#374151',
                      textTransform: 'none', fontWeight: 600, borderRadius: '8px',
                      '&:hover': { bgcolor: '#f9fafb' },
                    }}>
                    View Analytics
                  </Button>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card sx={{ borderRadius: '12px', border: '1px solid #e5e7eb', height: '100%' }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ fontWeight: 700, mb: 2, color: '#1f2937' }}>Recent Activity</Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                {[
                  { color: '#10b981', text: `${totalSurveys} surveys loaded` },
                  { color: '#6366f1', text: `${totalTemplates} templates available` },
                  { color: '#f59e0b', text: 'Backend connected' },
                ].map((item, i) => (
                  <Box key={i} sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: item.color, flexShrink: 0 }} />
                    <Typography variant="body2" sx={{ color: '#6b7280' }}>{item.text}</Typography>
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Search & Filter */}
      <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between' }}>
        <Typography variant="h6" sx={{ fontWeight: 700, color: '#1f2937' }}>Recent Surveys</Typography>
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <TextField
            placeholder="Search surveys..." value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)} size="small"
            sx={{ minWidth: 240, '& .MuiOutlinedInput-root': { bgcolor: '#fff', borderRadius: '8px', '& fieldset': { borderColor: '#e5e7eb' } } }}
            InputProps={{ startAdornment: <InputAdornment position="start"><Search size={18} color="#9ca3af" /></InputAdornment> }}
          />
          <FormControl size="small" sx={{ minWidth: 140, bgcolor: '#fff', borderRadius: '8px' }}>
            <Select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}
              sx={{ borderRadius: '8px', '& .MuiOutlinedInput-notchedOutline': { borderColor: '#e5e7eb' } }}>
              <MenuItem value="all">All Statuses</MenuItem>
              <MenuItem value="active">Active</MenuItem>
              <MenuItem value="draft">Draft</MenuItem>
              <MenuItem value="completed">Completed</MenuItem>
            </Select>
          </FormControl>
        </Box>
      </Box>

      {/* Survey Cards */}
      {tableLoading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress size={48} sx={{ color: '#6366f1' }} />
        </Box>
      ) : tableError ? (
        <Card sx={{ borderRadius: '12px', border: '1px solid #e5e7eb' }}>
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <AlertCircle size={48} color="#ef4444" style={{ marginBottom: 16 }} />
            <Typography variant="h6" sx={{ mb: 1, color: '#1f2937' }}>Error Loading Surveys</Typography>
            <Typography variant="body2" sx={{ color: '#6b7280' }}>{tableError}</Typography>
          </Box>
        </Card>
      ) : filteredSurveys.length === 0 ? (
        <Card sx={{ borderRadius: '12px', border: '1px solid #e5e7eb' }}>
          <EmptyState hasFilters={hasFilters} onCreateSurvey={() => navigate('/surveys/launch')} />
        </Card>
      ) : (
        <>
          <Grid container spacing={3}>
            {filteredSurveys.slice(0, 12).map((survey, idx) => {
              const surveyId = survey.surveyId || survey.SurveyId || survey.id || idx;
              return (
                <Grid item xs={12} sm={6} md={4} key={surveyId}>
                  <SurveyCard
                    survey={survey}
                    onView={handleView}
                    onEdit={handleEdit}
                    onAnalytics={handleAnalytics}
                    onContacts={handleContacts}
                    onSchedule={handleSchedule}
                    onDelete={handleDelete}
                    onCopyLink={handleCopyLink}
                  />
                </Grid>
              );
            })}
          </Grid>
          {filteredSurveys.length > 12 && (
            <Box sx={{ mt: 3, textAlign: 'center' }}>
              <Button onClick={() => navigate('/surveys/manage')} variant="outlined"
                sx={{ textTransform: 'none', color: '#6366f1', fontWeight: 600, borderColor: '#6366f1', borderRadius: '8px', px: 4 }}>
                View All {filteredSurveys.length} Surveys →
              </Button>
            </Box>
          )}
        </>
      )}

      {/* Snackbar */}
      <Snackbar open={notification.open} autoHideDuration={4000}
        onClose={() => setNotification(n => ({ ...n, open: false }))}
        anchorOrigin={{ vertical: 'top', horizontal: 'right' }}>
        <Alert onClose={() => setNotification(n => ({ ...n, open: false }))}
          severity={notification.severity} sx={{ width: '100%' }}>
          {notification.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default DashboardNew;