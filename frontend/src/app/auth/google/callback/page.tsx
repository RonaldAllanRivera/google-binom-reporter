'use client';

import { useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { CircularProgress, Box, Typography, Alert } from '@mui/material';

const GoogleCallback = () => {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { login } = useAuth();

  useEffect(() => {
    const email = searchParams.get('email');

    if (email) {
      login({ email });
      router.push('/');
    } else {
      console.error('Authentication failed: Email not found in URL.');
      router.push('/login?error=Authentication Failed');
    }
  }, [searchParams, login, router]);

  const error = searchParams.get('error');

  if (error) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <Alert severity="error">
          <Typography>Authentication Failed</Typography>
          <Typography variant="body2">{error}</Typography>
        </Alert>
      </Box>
    );
  }

  return (
    <Box display="flex" flexDirection="column" justifyContent="center" alignItems="center" minHeight="100vh">
      <CircularProgress />
      <Typography sx={{ mt: 2 }}>Finalizing authentication...</Typography>
    </Box>
  );
};

const SuspendedGoogleCallback = () => (
  <Suspense fallback={
    <Box display="flex" flexDirection="column" justifyContent="center" alignItems="center" minHeight="100vh">
      <CircularProgress />
      <Typography sx={{ mt: 2 }}>Loading...</Typography>
    </Box>
  }>
    <GoogleCallback />
  </Suspense>
);

export default SuspendedGoogleCallback;
