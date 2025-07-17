'use client';

import React, { useState } from 'react';
import { Typography, Paper, Box, Button, CircularProgress, Alert } from '@mui/material';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import dayjs, { Dayjs } from 'dayjs';
import { ButtonGroup } from '@mui/material';
import { getCombinedReport } from '@/services/api';
import { useDateRangePresets } from '@/hooks/useDateRangePresets';

const columns: GridColDef[] = [
  { field: 'id', headerName: 'ID', width: 90 },
  { field: 'accountName', headerName: 'Account Name', width: 150 },
  { field: 'campaignName', headerName: 'Campaign Name', width: 150 },
  { field: 'totalSpend', headerName: 'Total Spend', type: 'number', width: 110 },
  { field: 'revenue', headerName: 'Revenue', type: 'number', width: 110 },
];

const CombinedReportPage = () => {
  const [startDate, setStartDate] = useState<Dayjs | null>(dayjs().subtract(7, 'day'));
  const [endDate, setEndDate] = useState<Dayjs | null>(dayjs());
  const [rows, setRows] = useState<any[]>([]);
  const [googleSheetLink, setGoogleSheetLink] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { handleSetDateRange } = useDateRangePresets(setStartDate, setEndDate);

  const handleGenerateReport = async () => {
    if (!startDate || !endDate) {
      setError('Please select both a start and end date.');
      return;
    }

    if (startDate.isAfter(endDate)) {
      setError('Start date cannot be after end date.');
      return;
    }

    setLoading(true);
    setError(null);
    setGoogleSheetLink(null);

    try {
      const data = await getCombinedReport(startDate, endDate);
      setRows(data.results.map((item: any, index: number) => ({ id: index, ...item })));
      setGoogleSheetLink(data.google_sheet_link);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDayjs}>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Combined Report
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 2, mb: 3, alignItems: 'center' }}>
          <DatePicker
            label="Start Date"
            value={startDate}
            onChange={(newValue) => setStartDate(newValue)}
            maxDate={endDate ?? undefined}
          />
          <DatePicker
            label="End Date"
            value={endDate}
            onChange={(newValue) => setEndDate(newValue)}
            minDate={startDate ?? undefined}
          />
          <Button variant="contained" onClick={handleGenerateReport} disabled={loading}>
            {loading ? <CircularProgress size={24} /> : 'Generate Report'}
          </Button>
        </Box>

        <Box sx={{ display: 'flex', gap: 1, my: 2 }}>
          <ButtonGroup variant="outlined" aria-label="Date range presets">
            <Button onClick={() => handleSetDateRange('last7days')}>Last 7 Days</Button>
            <Button onClick={() => handleSetDateRange('last30days')}>Last 30 Days</Button>
            <Button onClick={() => handleSetDateRange('thisMonth')}>This Month</Button>
            <Button onClick={() => handleSetDateRange('lastMonth')}>Last Month</Button>
          </ButtonGroup>
        </Box>

        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

        {googleSheetLink && (
          <Box sx={{ my: 2 }}>
            <Button 
              variant="contained" 
              color="success"
              onClick={() => window.open(googleSheetLink, '_blank')}
            >
              Open Google Sheet
            </Button>
          </Box>
        )}

        <Box sx={{ height: 400, width: '100%' }}>
          <DataGrid
            rows={rows}
            columns={columns}
            loading={loading}
            initialState={{
              pagination: {
                paginationModel: { page: 0, pageSize: 5 },
              },
            }}
            pageSizeOptions={[5, 10]}
            checkboxSelection
          />
        </Box>
      </Paper>
    </LocalizationProvider>
  );
};

export default CombinedReportPage;
