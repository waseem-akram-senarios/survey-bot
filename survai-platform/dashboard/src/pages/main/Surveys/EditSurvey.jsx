import React, { useState, useEffect } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  TextField,
  Button,
  Paper,
  CircularProgress,
  Snackbar,
  Alert,
  useMediaQuery,
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import SaveIcon from '@mui/icons-material/Save';
import SurveyService from '../../../services/Surveys/surveyService';

const EditSurvey = () => {
  const { surveyId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const isMobile = useMediaQuery('(max-width: 600px)');
  const surveyData = location.state?.surveyData || {};

  const [recipient, setRecipient] = useState(surveyData.Recipient || '');
  const [riderName, setRiderName] = useState(surveyData.RiderName || '');
  const [phone, setPhone] = useState(surveyData.Phone || '');
  const [saving, setSaving] = useState(false);
  const [questions, setQuestions] = useState([]);
  const [loadingQ, setLoadingQ] = useState(true);
  const [msg, setMsg] = useState('');
  const [showMsg, setShowMsg] = useState(false);

  useEffect(() => {
    const load = async () => {
      try {
        const qs = await SurveyService.fetchSurveyQuestions(surveyId);
        setQuestions(qs);
      } catch { /* ignore */ }
      setLoadingQ(false);
    };
    load();
  }, [surveyId]);

  const handleSave = async () => {
    setSaving(true);
    try {
      await SurveyService.updateSurveyDetails(surveyId, { recipient, riderName, phone });
      setMsg('Survey updated successfully');
      setShowMsg(true);
      setTimeout(() => navigate('/surveys/manage'), 1500);
    } catch (error) {
      setMsg(error.message);
      setShowMsg(true);
    }
    setSaving(false);
  };

  const fieldSx = {
    '& .MuiOutlinedInput-root': { borderRadius: '12px', fontFamily: 'Poppins, sans-serif' },
    '& .MuiInputLabel-root': { fontFamily: 'Poppins, sans-serif' },
  };

  return (
    <Box sx={{ backgroundColor: '#F9FBFC', flexGrow: 1, p: isMobile ? 2 : 4 }}>
      <Button
        startIcon={<ArrowBackIcon />}
        onClick={() => navigate('/surveys/manage')}
        sx={{ mb: 2, textTransform: 'none', fontFamily: 'Poppins, sans-serif', color: '#1958F7' }}
      >
        Back to Manage Surveys
      </Button>

      <Paper sx={{ p: isMobile ? 2 : 4, borderRadius: '20px', mb: 3 }}>
        <Typography sx={{ fontFamily: 'Poppins, sans-serif', fontWeight: 600, fontSize: '22px', mb: 3 }}>
          Edit Survey
        </Typography>
        <Typography sx={{ fontFamily: 'Poppins, sans-serif', fontSize: '14px', color: '#666', mb: 3 }}>
          Survey ID: {surveyId} &nbsp;|&nbsp; Template: {surveyData.Name || 'N/A'} &nbsp;|&nbsp; Status: {surveyData.Status || 'In-Progress'}
        </Typography>

        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2.5, maxWidth: 500 }}>
          <TextField label="Recipient" value={recipient} onChange={(e) => setRecipient(e.target.value)} fullWidth sx={fieldSx} />
          <TextField label="Rider Name" value={riderName} onChange={(e) => setRiderName(e.target.value)} fullWidth sx={fieldSx} />
          <TextField label="Phone" value={phone} onChange={(e) => setPhone(e.target.value)} fullWidth sx={fieldSx} />
        </Box>

        <Button
          variant="contained"
          startIcon={saving ? <CircularProgress size={18} sx={{ color: '#fff' }} /> : <SaveIcon />}
          onClick={handleSave}
          disabled={saving}
          sx={{
            mt: 3, textTransform: 'none', borderRadius: '12px', px: 4,
            fontFamily: 'Poppins, sans-serif', backgroundColor: '#1958F7',
            '&:hover': { backgroundColor: '#1445CC' },
          }}
        >
          {saving ? 'Saving...' : 'Save Changes'}
        </Button>
      </Paper>

      {loadingQ ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress size={40} sx={{ color: '#1958F7' }} />
        </Box>
      ) : questions.length > 0 && (
        <Paper sx={{ p: isMobile ? 2 : 4, borderRadius: '20px' }}>
          <Typography sx={{ fontFamily: 'Poppins, sans-serif', fontWeight: 600, fontSize: '18px', mb: 2 }}>
            Survey Questions ({questions.length})
          </Typography>
          {questions.map((q, i) => (
            <Box key={q.id || i} sx={{ mb: 2, p: 2, backgroundColor: '#F9FBFC', borderRadius: '12px' }}>
              <Typography sx={{ fontFamily: 'Poppins, sans-serif', fontWeight: 500, fontSize: '14px' }}>
                Q{i + 1}: {q.questionText || q.text || q.QueText || 'Question'}
              </Typography>
              <Typography sx={{ fontFamily: 'Poppins, sans-serif', fontSize: '12px', color: '#888', mt: 0.5 }}>
                Type: {q.type || q.criteria || 'open'} {q.answer ? `| Answer: ${q.answer}` : ''}
              </Typography>
            </Box>
          ))}
        </Paper>
      )}

      <Snackbar open={showMsg} autoHideDuration={4000} onClose={() => setShowMsg(false)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}>
        <Alert onClose={() => setShowMsg(false)} severity="success" variant="filled"
          sx={{ background: '#EFEFFD', color: '#1958F7' }}>
          {msg}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default EditSurvey;
