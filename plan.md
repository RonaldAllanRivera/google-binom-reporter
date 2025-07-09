# Fullstack Google Binom Reporter – Development Plan

## Project Overview
This project provides a modern web frontend and backend for managing Google Ads and Binom campaign reports. It features Authentication, Report Generation, Google Ads Test, and a Combined Report with Google Sheets integration. Data is displayed in a Google Sheets-like table locally, and also exported live to Google Sheets (with formulas), making sharing and further analysis easy.

---

## Features & Flow

### 1. Authentication
- Google OAuth2 login (backend endpoint)
- Frontend shows login button and user info

### 2. Report Generation
- User selects date range (other params from .env)
- Fetches Binom report via API
- Displays results in a modern, interactive table

### 3. Google Ads Test
- User selects date range (other params from .env)
- Fetches Google Ads data via API
- Displays results in a modern, interactive table

### 4. Combined Report
- User selects date range
- Backend merges Binom & Google Ads data
- Stores result in DB
- Pushes data + formulas to Google Sheet
- Returns combined data & Google Sheet link
- Frontend displays:
  - Local Google Sheets-like table
  - Button/link to live Google Sheet (optionally embed preview)

### 5. Output Data Cleaning (Completed)
- [x] Backend filters out entries where both "ACCOUNT NAME" and "CAMPAIGN NAME" are empty
- [x] Backend filters out entries where both "TOTAL SPEND" and "REVENUE" are zero
- [x] Removes formula fields (`P/L_FORMULA`, `ROI_FORMULA`) and `ROI_VALUE` from API output
- [x] API now returns only clean, relevant campaign data

### 5. Google Sheets Integration
- Backend uses Google Sheets API
- Auth via service account
- Writes data & formulas to sheet
- Returns shareable link

---

## Technical Stack
- **Frontend:** React + Material-UI (or Ant Design), AG Grid or MUI DataGrid
- **Backend:** Django + Django REST Framework
- **Google Sheets API:** Python client, service account
- **Database:** Existing DB for storing combined reports and ROI
- **.env:** Stores constants (email, trafficSourceIds, etc.)

---

## Task Breakdown

### Frontend
- [ ] Modern UI with Material-UI/Ant Design
- [ ] Authentication page
- [ ] Report Generation page (date range input, table)
- [ ] Google Ads Test page (date range input, table)
- [ ] Combined Report page:
  - [ ] Date range input
  - [ ] Local table for combined data
  - [ ] Show live Google Sheet link & preview

### Backend
- [ ] Store constants in .env
- [ ] Combined report endpoint (merge, store, push to Google Sheets, return link)
- [ ] Google Sheets API integration (service account, formulas)
- [ ] ROI calculation logic
- [ ] Database schema for combined reports

### Google Sheets Integration
- [ ] Set up Google Cloud project & service account
- [ ] Implement sheet creation/updating logic
- [ ] Apply formulas in sheet
- [ ] Ensure shareable link returned

### Testing & Polish
- [ ] Test with provided sample data (CSV/JSON)
- [ ] Error handling & loading states
- [ ] UI/UX polish, mobile responsiveness

---

## Notes
- Only date range is user input; all other params are constants
- Combined report must be exportable and live in Google Sheets
- Local and live views both available for combined report
- Google Sheet link is retrievable for sharing/email
- All features use a modern, consistent design

---

## Next Step
- Design frontend UI wireframes and architecture
