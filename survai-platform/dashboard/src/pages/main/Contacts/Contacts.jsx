import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  FormControl,
  Select,
  MenuItem,
  Paper,
  IconButton,
  CircularProgress,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
} from '@mui/material';
import { ChevronLeft, Phone } from 'lucide-react';
import { useAuth } from '../../../context/AuthContext';
import SurveyTableService from '../../../services/Surveys/surveyTableService';

const Contacts = () => {
  const { user } = useAuth();
  const [surveys, setSurveys] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedSurveyId, setSelectedSurveyId] = useState('');

  const tenantId = user?.tenantId ?? null;

  useEffect(() => {
    const fetchSurveys = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await SurveyTableService.getSurveyList(tenantId);
        setSurveys(Array.isArray(data) ? data : []);
      } catch (err) {
        console.error('Error fetching surveys for contacts:', err);
        setError('Failed to load surveys.');
        setSurveys([]);
      } finally {
        setLoading(false);
      }
    };
    fetchSurveys();
  }, [tenantId]);

  const selectedSurvey = selectedSurveyId
    ? surveys.find((s) => s.SurveyId === selectedSurveyId || s.id === selectedSurveyId)
    : null;

  return (
    <Box sx={{ p: { xs: 2, md: 6 }, maxWidth: 1400, mx: 'auto' }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 6, flexWrap: 'wrap', gap: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <IconButton sx={{ color: '#6b7280' }}>
            <ChevronLeft size={24} />
          </IconButton>
          <Box>
            <Typography variant="h4" sx={{ fontWeight: 800, color: '#111827' }}>
              Contact Lists
            </Typography>
            <Typography variant="body1" sx={{ color: '#6b7280' }}>
              Manage contacts for phone surveys
            </Typography>
          </Box>
        </Box>
        <FormControl size="small" sx={{ minWidth: 240, bgcolor: '#fff' }} disabled={loading}>
          <Select
            value={selectedSurveyId}
            onChange={(e) => setSelectedSurveyId(e.target.value)}
            displayEmpty
            renderValue={(v) => {
              if (!v) return 'Select survey';
              const s = surveys.find((x) => (x.SurveyId || x.id) === v);
              return s ? (s.Name || s.Recipient || s.SurveyId || v) : v;
            }}
          >
            <MenuItem value="" disabled>Select survey</MenuItem>
            {surveys.map((s) => {
              const id = s.SurveyId || s.id;
              const label = s.Name || s.Recipient || id;
              return (
                <MenuItem key={id} value={id}>{label}</MenuItem>
              );
            })}
          </Select>
        </FormControl>
      </Box>

      {error && (
        <Alert severity="warning" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Main Content Area */}
      <Paper
        sx={{
          p: selectedSurvey ? 3 : 8,
          borderRadius: 4,
          textAlign: selectedSurvey ? 'left' : 'center',
          border: '1px solid #f0f0f0',
          minHeight: 400,
          display: 'flex',
          flexDirection: 'column',
          justifyContent: selectedSurvey ? 'flex-start' : 'center',
          alignItems: selectedSurvey ? 'stretch' : 'center',
          boxShadow: 'none',
        }}
      >
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
            <CircularProgress size={48} sx={{ color: '#6366f1' }} />
          </Box>
        ) : !selectedSurveyId ? (
          <>
            <Box sx={{ bgcolor: '#f9fafb', p: 3, borderRadius: '50%', color: '#9ca3af', mb: 3, alignSelf: 'center' }}>
              <Phone size={48} />
            </Box>
            <Typography variant="h5" sx={{ fontWeight: 700, mb: 1 }}>
              Select a Survey
            </Typography>
            <Typography variant="body1" sx={{ color: '#6b7280', maxWidth: 400, alignSelf: 'center' }}>
              Choose a survey to manage its contact list
            </Typography>
          </>
        ) : selectedSurvey ? (
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 700, mb: 2 }}>
              Contact for this survey
            </Typography>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell sx={{ fontWeight: 600 }}>Recipient</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Phone</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Rider / Notes</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                <TableRow>
                  <TableCell>{selectedSurvey.Recipient || '—'}</TableCell>
                  <TableCell>{selectedSurvey.Phone || '—'}</TableCell>
                  <TableCell>{selectedSurvey.RiderName || selectedSurvey.Name || '—'}</TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </Box>
        ) : null}
      </Paper>
    </Box>
  );
};

export default Contacts;
