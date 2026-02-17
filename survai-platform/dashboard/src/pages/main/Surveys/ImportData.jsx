import React, { useState, useRef } from 'react';
import {
  Box, Typography, Button, Paper, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, Alert, CircularProgress,
  Chip, IconButton, Divider
} from '@mui/material';
import { CloudUpload, Download, CheckCircle, Error as ErrorIcon, ArrowBack } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import ApiBaseHelper from '../../../network/apiBaseHelper';
import ApiLinks from '../../../network/apiLinks';
import { exportAllSurveys, exportTranscripts } from '../../../utils/exportHelper';

const ImportData = () => {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState([]);
  const [headers, setHeaders] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFileSelect = (event) => {
    const selectedFile = event.target.files[0];
    if (!selectedFile) return;

    if (!selectedFile.name.endsWith('.csv')) {
      setError('Please select a CSV file.');
      return;
    }

    setFile(selectedFile);
    setError(null);
    setResult(null);

    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target.result;
      const lines = text.split('\n').filter(l => l.trim());
      if (lines.length > 0) {
        const hdrs = lines[0].split(',').map(h => h.trim().replace(/"/g, ''));
        setHeaders(hdrs);
        const rows = lines.slice(1, Math.min(6, lines.length)).map(line => {
          const cells = line.split(',').map(c => c.trim().replace(/"/g, ''));
          return cells;
        });
        setPreview(rows);
      }
    };
    reader.readAsText(selectedFile);
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await ApiBaseHelper.axiosInstance.post(
        ApiLinks.IMPORT_RIDERS,
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );

      setResult(response.data);
    } catch (err) {
      console.error('Upload error:', err);
      setError(err.response?.data?.detail || 'Upload failed. Please check your CSV format.');
    } finally {
      setUploading(false);
    }
  };

  const handleBulkSurveys = async () => {
    if (!file) return;
    setUploading(true);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await ApiBaseHelper.axiosInstance.post(
        ApiLinks.IMPORT_BULK_SURVEYS,
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );

      setResult(response.data);
    } catch (err) {
      console.error('Bulk survey error:', err);
      setError(err.response?.data?.detail || 'Bulk survey creation failed. Please check your CSV format.');
    } finally {
      setUploading(false);
    }
  };

  const downloadTemplate = () => {
    const csvContent = "name,phone,email\nJason Smith,123-456-7890,jason@example.com\nErika Sampson,321-654-0987,erika@example.com\nSamantha Ferguson,789-456-1230,samantha@example.com";
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'rider_import_template.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  const downloadBulkTemplate = () => {
    const csvContent = "rider_name,phone,email,template_name\nJason Smith,123-456-7890,jason@example.com,Demo\nErika Sampson,321-654-0987,erika@example.com,Demo";
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'bulk_survey_template.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <Box sx={{ p: 4 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3, gap: 2 }}>
        <IconButton onClick={() => navigate(-1)}><ArrowBack /></IconButton>
        <Typography sx={{ fontFamily: 'Poppins, sans-serif', fontWeight: 600, fontSize: '24px', color: '#333' }}>
          Import Data
        </Typography>
      </Box>

      <Paper sx={{ p: 4, borderRadius: '16px', mb: 3 }}>
        <Typography sx={{ fontFamily: 'Poppins, sans-serif', fontWeight: 500, fontSize: '18px', mb: 2 }}>
          Upload Rider Data (CSV)
        </Typography>
        <Typography sx={{ fontFamily: 'Poppins, sans-serif', fontSize: '14px', color: '#666', mb: 3 }}>
          Upload a CSV file with rider information. Required columns: <b>name</b>, <b>phone</b>. Optional: <b>email</b>.
        </Typography>

        <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
          <Button variant="outlined" startIcon={<Download />} onClick={downloadTemplate}
            sx={{ textTransform: 'none', borderRadius: '10px', fontFamily: 'Poppins, sans-serif' }}>
            Download Rider Template
          </Button>
          <Button variant="outlined" startIcon={<Download />} onClick={downloadBulkTemplate}
            sx={{ textTransform: 'none', borderRadius: '10px', fontFamily: 'Poppins, sans-serif' }}>
            Download Bulk Survey Template
          </Button>
        </Box>

        <input ref={fileInputRef} type="file" accept=".csv" onChange={handleFileSelect} style={{ display: 'none' }} />

        <Box
          onClick={() => fileInputRef.current?.click()}
          sx={{
            border: '2px dashed #ccc', borderRadius: '16px', p: 4, textAlign: 'center',
            cursor: 'pointer', transition: 'all 0.3s', mb: 3,
            '&:hover': { borderColor: '#1958F7', backgroundColor: '#f8faff' },
            ...(file && { borderColor: '#4CAF50', backgroundColor: '#f8fff8' }),
          }}
        >
          <CloudUpload sx={{ fontSize: 48, color: file ? '#4CAF50' : '#999', mb: 1 }} />
          <Typography sx={{ fontFamily: 'Poppins, sans-serif', fontWeight: 500, color: '#555' }}>
            {file ? file.name : 'Click to select a CSV file'}
          </Typography>
          {file && (
            <Typography sx={{ fontFamily: 'Poppins, sans-serif', fontSize: '12px', color: '#888', mt: 1 }}>
              {(file.size / 1024).toFixed(1)} KB
            </Typography>
          )}
        </Box>

        {preview.length > 0 && (
          <Box sx={{ mb: 3 }}>
            <Typography sx={{ fontFamily: 'Poppins, sans-serif', fontWeight: 500, fontSize: '14px', mb: 1 }}>
              Preview (first {preview.length} rows):
            </Typography>
            <TableContainer sx={{ borderRadius: '8px', border: '1px solid #eee' }}>
              <Table size="small">
                <TableHead>
                  <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
                    {headers.map((h, i) => (
                      <TableCell key={i} sx={{ fontFamily: 'Poppins, sans-serif', fontWeight: 600, fontSize: '13px' }}>{h}</TableCell>
                    ))}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {preview.map((row, i) => (
                    <TableRow key={i}>
                      {row.map((cell, j) => (
                        <TableCell key={j} sx={{ fontFamily: 'Poppins, sans-serif', fontSize: '13px' }}>{cell}</TableCell>
                      ))}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        )}

        {error && <Alert severity="error" sx={{ mb: 2, borderRadius: '10px' }}>{error}</Alert>}
        {result && (
          <Alert severity="success" icon={<CheckCircle />} sx={{ mb: 2, borderRadius: '10px' }}>
            {result.message || `Successfully imported ${result.inserted || result.created || 0} records.`}
          </Alert>
        )}

        <Divider sx={{ my: 2 }} />

        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="contained" onClick={handleUpload} disabled={!file || uploading}
            startIcon={uploading ? <CircularProgress size={20} color="inherit" /> : <CloudUpload />}
            sx={{
              textTransform: 'none', borderRadius: '10px', fontFamily: 'Poppins, sans-serif',
              background: 'linear-gradient(180deg, #1958F7 0%, #3D69D9 100%)', px: 4,
            }}
          >
            {uploading ? 'Uploading...' : 'Import Riders'}
          </Button>
          <Button
            variant="contained" onClick={handleBulkSurveys} disabled={!file || uploading}
            startIcon={uploading ? <CircularProgress size={20} color="inherit" /> : <CloudUpload />}
            sx={{
              textTransform: 'none', borderRadius: '10px', fontFamily: 'Poppins, sans-serif',
              background: 'linear-gradient(180deg, #4CAF50 0%, #388E3C 100%)', px: 4,
            }}
          >
            {uploading ? 'Creating...' : 'Bulk Create Surveys'}
          </Button>
        </Box>
      </Paper>

      <Paper sx={{ p: 4, borderRadius: '16px' }}>
        <Typography sx={{ fontFamily: 'Poppins, sans-serif', fontWeight: 500, fontSize: '18px', mb: 2 }}>
          Export Data (CSV)
        </Typography>
        <Typography sx={{ fontFamily: 'Poppins, sans-serif', fontSize: '14px', color: '#666', mb: 3 }}>
          Download survey responses and call transcripts as CSV files for analysis.
        </Typography>

        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <Button
            variant="contained" startIcon={<Download />}
            onClick={async () => {
              try { await exportAllSurveys(); } catch { setError('Failed to export survey data.'); }
            }}
            sx={{
              textTransform: 'none', borderRadius: '10px', fontFamily: 'Poppins, sans-serif',
              background: 'linear-gradient(180deg, #1958F7 0%, #3D69D9 100%)', px: 3,
            }}
          >
            Export All Survey Responses
          </Button>
          <Button
            variant="contained" startIcon={<Download />}
            onClick={async () => {
              try { await exportTranscripts(); } catch { setError('Failed to export transcripts.'); }
            }}
            sx={{
              textTransform: 'none', borderRadius: '10px', fontFamily: 'Poppins, sans-serif',
              background: 'linear-gradient(180deg, #7B1FA2 0%, #6A1B9A 100%)', px: 3,
            }}
          >
            Export Call Transcripts
          </Button>
        </Box>
      </Paper>
    </Box>
  );
};

export default ImportData;
