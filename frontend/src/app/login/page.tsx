'use client';

import React, { useState } from 'react';
import { Button, Container, Typography, Box, CircularProgress, Alert } from '@mui/material';
import { getGoogleAuthUrl } from '@/services/api';

const LoginPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async () => {
    setLoading(true);
    setError(null);
    try {
      const { auth_url } = await getGoogleAuthUrl();
      if (auth_url) {
        window.location.href = auth_url;
      } else {
        setError('Could not get authentication URL. Please try again.');
        setLoading(false);
      }
    } catch (err) {
      console.error('Login failed', err);
      setError('Login failed. Please check the console for details.');
      setLoading(false);
    }
  };

  return (
    <Container component="main" maxWidth="xs">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Typography component="h1" variant="h5">
          Sign In
        </Typography>
        {error && (
          <Alert severity="error" sx={{ width: '100%', mt: 2 }}>
            {error}
          </Alert>
        )}
        <Box sx={{ mt: 3, position: 'relative' }}>
          <Button
            fullWidth
            variant="contained"
            onClick={handleLogin}
            disabled={loading}
            sx={{
              backgroundColor: '#4285F4',
              color: 'white',
              '&:hover': { backgroundColor: '#357ae8' },
            }}
          >
            {loading ? 'Redirecting...' : 'Sign In with Google'}
          </Button>
          {loading && (
            <CircularProgress
              size={24}
              sx={{
                position: 'absolute',
                top: '50%',
                left: '50%',
                marginTop: '-12px',
                marginLeft: '-12px',
              }}
            />
          )}
        </Box>
      </Box>
    </Container>
  );
};

export default LoginPage;
