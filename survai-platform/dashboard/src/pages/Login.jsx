import React, { useState } from 'react';
import { Box, TextField, Button, Typography, Paper, Alert, CircularProgress } from '@mui/material';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import logo from '../assets/logo.png';

const Login = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const result = login(username, password);
    if (result.success) {
      navigate('/dashboard');
    } else {
      setError(result.error);
    }
    setLoading(false);
  };

  return (
    <Box sx={{
      minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    }}>
      <Paper sx={{ p: 5, borderRadius: '20px', width: '100%', maxWidth: 420, textAlign: 'center' }}>
        <Box sx={{ mb: 3 }}>
          <img src={logo} alt="SurvAI" style={{ width: '140px', marginBottom: '8px' }} />
          <Typography sx={{ fontFamily: 'Poppins, sans-serif', fontSize: '14px', color: '#888' }}>
            Agency Login
          </Typography>
        </Box>

        {error && <Alert severity="error" sx={{ mb: 2, borderRadius: '10px' }}>{error}</Alert>}

        <form onSubmit={handleSubmit}>
          <TextField
            fullWidth label="Username" value={username} onChange={e => setUsername(e.target.value)}
            sx={{ mb: 2, '& .MuiOutlinedInput-root': { borderRadius: '12px' } }}
            required autoFocus
          />
          <TextField
            fullWidth label="Password" type="password" value={password} onChange={e => setPassword(e.target.value)}
            sx={{ mb: 3, '& .MuiOutlinedInput-root': { borderRadius: '12px' } }}
            required
          />
          <Button
            type="submit" fullWidth variant="contained" disabled={loading}
            sx={{
              height: '48px', borderRadius: '12px', textTransform: 'none',
              fontFamily: 'Poppins, sans-serif', fontSize: '16px', fontWeight: 500,
              background: 'linear-gradient(180deg, #1958F7 0%, #3D69D9 100%)',
            }}
          >
            {loading ? <CircularProgress size={24} color="inherit" /> : 'Sign In'}
          </Button>
        </form>

        <Typography sx={{ mt: 3, fontFamily: 'Poppins, sans-serif', fontSize: '12px', color: '#aaa' }}>
          Contact your administrator for access credentials
        </Typography>
      </Paper>
    </Box>
  );
};

export default Login;
