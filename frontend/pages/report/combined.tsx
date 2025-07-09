import React, { useState } from 'react';
import { Box, Button, Typography, Paper, Link, CircularProgress } from '@mui/material';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import dayjs from 'dayjs';

// Helper to format date as YYYY-MM-DD
const formatDate = (date: Date) => dayjs(date).format('YYYY-MM-DD');

const defaultStart = dayjs().startOf('month').toDate();
const defaultEnd = dayjs().endOf('month').toDate();

export default function CombinedReportPage() {
  const [startDate, setStartDate] = useState(formatDate(defaultStart));
  const [endDate, setEndDate] = useState(formatDate(defaultEnd));
  const [loading, setLoading] = useState(false);
  const [rows, setRows] = useState<any[]>([]);
  const [columns, setColumns] = useState<GridColDef[]>([]);
  const [sheetUrl, setSheetUrl] = useState<string | null>(null);
  const [sheetPreview, setSheetPreview] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchCombinedReport = async () => {
    setLoading(true);
    setError(null);
    setRows([]);
    setColumns([]);
    setSheetUrl(null);
    setSheetPreview(null);
    try {
      const res = await fetch(`/api/combined-report?start_date=${startDate}&end_date=${endDate}`);
      if (!res.ok) throw new Error('Failed to fetch combined report');
      const data = await res.json();
      // Assume data: { rows: [], columns: [], sheetUrl: string, sheetPreviewUrl?: string }
      setRows(data.rows || []);
      setColumns(data.columns || []);
      setSheetUrl(data.sheetUrl);
      setSheetPreview(data.sheetPreviewUrl || null);
    } catch (e: any) {
      setError(e.message || 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', py: 4 }}>
      <Typography variant="h4" gutterBottom>
        Combined Report
      </Typography>
      <Paper sx={{ p: 2, mb: 3, display: 'flex', gap: 2, alignItems: 'center' }}>
        <label>
          Start Date:
          <input
            type="date"
            value={startDate}
            onChange={e => setStartDate(e.target.value)}
            style={{ marginLeft: 8, marginRight: 16 }}
          />
        </label>
        <label>
          End Date:
          <input
            type="date"
            value={endDate}
            onChange={e => setEndDate(e.target.value)}
            style={{ marginLeft: 8, marginRight: 16 }}
          />
        </label>
        <Button variant="contained" onClick={fetchCombinedReport} disabled={loading}>
          Generate Combined Report
        </Button>
      </Paper>
      {loading && <CircularProgress />}
      {error && <Typography color="error">{error}</Typography>}
      {rows.length > 0 && columns.length > 0 && (
        <Box sx={{ height: 500, width: '100%', mb: 4 }}>
          <Typography variant="h6" gutterBottom>
            Local Google Sheets-like Table
          </Typography>
          <DataGrid 
            rows={rows} 
            columns={columns} 
            initialState={{
              pagination: {
                paginationModel: { pageSize: 20, page: 0 },
              },
            }}
            pageSizeOptions={[20, 50, 100]}
          />
        </Box>
      )}
      {sheetUrl && (
        <Box sx={{ mb: 4 }}>
          <Typography variant="h6" gutterBottom>
            Live Google Sheet
          </Typography>
          <Link href={sheetUrl} target="_blank" rel="noopener">
            Open in Google Sheets
          </Link>
          {sheetPreview && (
            <Box sx={{ mt: 2 }}>
              <iframe
                src={sheetPreview}
                width="100%"
                height="600"
                style={{ border: '1px solid #ccc' }}
                title="Google Sheet Preview"
                allowFullScreen
              />
            </Box>
          )}
        </Box>
      )}
    </Box>
  );
}
