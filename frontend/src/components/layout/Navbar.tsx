'use client';

import React from 'react';
import { AppBar, Toolbar, Typography, Box } from '@mui/material';
import { useAuth } from '@/contexts/AuthContext';

const drawerWidth = 240;

const Navbar = () => {
  const { user } = useAuth();

  return (
    <AppBar
      position="fixed"
      sx={{
        width: `calc(100% - ${drawerWidth}px)`,
        ml: `${drawerWidth}px`,
        backgroundColor: 'white',
        color: 'black',
        boxShadow: '0 1px 4px 0 rgba(0,0,0,0.1)',
      }}
    >
      <Toolbar>
        <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
          Google Binom Reporter
        </Typography>
        {user && (
          <Box>
            <Typography variant="body1">
              {user.first_name} {user.last_name}
            </Typography>
          </Box>
        )}
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;
