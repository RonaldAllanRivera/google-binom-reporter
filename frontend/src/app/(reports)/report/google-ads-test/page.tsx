'use client';

import React, { useState } from 'react';
import { Typography, Paper, Box, Button, CircularProgress, Alert } from '@mui/material';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { getGoogleAdsTest } from '@/services/api';

const columns: GridColDef[] = [
  { field: 'id', headerName: 'ID', width: 90 },
  { field: 'customer_id', headerName: 'Customer ID', width: 150 },
  { field: 'campaign_id', headerName: 'Campaign ID', width: 150 },
  { field: 'campaign_name', headerName: 'Campaign Name', width: 250 },
  { field: 'ad_group_id', headerName: 'Ad Group ID', width: 150 },
  { field: 'ad_group_name', headerName: 'Ad Group Name', width: 250 },
];

const GoogleAdsTestPage = () => {
  const [rows, setRows] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleRunTest = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await getGoogleAdsTest();
      setRows(data.map((item: any, index: number) => ({ id: index, ...item })));
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Google Ads API Test
      </Typography>
      
      <Box sx={{ mb: 3 }}>
        <Button variant="contained" onClick={handleRunTest} disabled={loading}>
          {loading ? <CircularProgress size={24} /> : 'Run Test'}
        </Button>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      <Box sx={{ height: 600, width: '100%' }}>
        <DataGrid
          rows={rows}
          columns={columns}
          loading={loading}
          initialState={{
            pagination: {
              paginationModel: { page: 0, pageSize: 10 },
            },
          }}
          pageSizeOptions={[10, 25, 50]}
        />
      </Box>
    </Paper>
  );
};

export default GoogleAdsTestPage;
