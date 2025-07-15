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

## Frontend Architecture & Design Plan

This plan outlines a scalable and maintainable architecture for the React frontend, using Material-UI for components and React Router for navigation.

### 1. Component Structure
Organize components into a logical folder structure:

- **`src/`**
  - **`components/`**: Reusable UI components.
    - **`layout/`**: `Navbar.js`, `Sidebar.js`, `Layout.js` (wraps pages).
    - **`common/`**: `DatePicker.js`, `Loader.js`, `ErrorMessage.js`, `InfoTooltip.js`.
    - **`auth/`**: `LoginButton.js`, `UserInfo.js` (displays user name/avatar).
    - **`table/`**: `DataTable.js` (a wrapper for AG Grid or MUI DataGrid, configured for our needs).
  - **`pages/`**: Top-level page components.
    - `LoginPage.js`: Handles the Google OAuth flow.
    - `BinomReportPage.js`: Contains date picker and `DataTable` for Binom data.
    - `GoogleAdsReportPage.js`: Contains date picker and `DataTable` for Google Ads data.
    - `CombinedReportPage.js`: The main page, featuring date picker, `DataTable` for local data, and a section to display the Google Sheet link.
  - **`contexts/`**: For React Context API state management.
    - `AuthContext.js`: Manages user authentication state, token, and profile.
    - `ReportContext.js`: Manages shared state for reports, like the date range, loading status, and errors.
  - **`services/`**: For external communication.
    - `api.js`: A centralized Axios or Fetch instance with base URL and interceptors for adding the auth token to requests.
  - **`hooks/`**: Custom hooks for reusable logic.
    - `useAuth.js`: A hook to easily access `AuthContext`.
    - `useReports.js`: A hook to fetch and manage report data.
  - **`App.js`**: Main component, sets up routing.
  - **`index.js`**: Renders the `App` component.

### 2. Routing (`react-router-dom`)
Define the application's routes:

- **`/login`**: `LoginPage` (Public route).
- **`/`**: `CombinedReportPage` (Protected route, redirects to `/login` if not authenticated).
- **`/reports/binom`**: `BinomReportPage` (Protected route).
- **`/reports/google-ads`**: `GoogleAdsReportPage` (Protected route).

A `ProtectedRoute` component will be created to handle authentication checks for the protected routes.

### 3. State Management (React Context API)
For a project of this size, the built-in Context API is a lightweight and effective choice:

- **`AuthContext`**: 
  - **State**: `user`, `token`, `isAuthenticated`, `isLoading`, `error`.
  - **Actions**: `login()`, `logout()`, `loadUser()`.
  - The `App` will be wrapped in an `AuthProvider` to make auth state available globally.

- **`ReportContext`**:
  - **State**: `dateRange`, `loading`, `error`.
  - **Actions**: `setDateRange()`.
  - This context will wrap the main `Layout` component so that all report pages can share the selected date range and display a consistent loading state.

### 4. API Service Layer
Create a dedicated service for backend communication:

- An `api.js` file will configure a base Axios instance.
- It will include an interceptor to automatically attach the JWT token from `AuthContext` to the headers of all outgoing requests.
- Functions for each endpoint will be defined:
  - `loginWithGoogle(code)`
  - `getBinomReport(dateRange)`
  - `getGoogleAdsReport(dateRange)`
  - `getCombinedReport(dateRange)`
  - `fetchGoogleSheetLink(reportId)`

### 5. UI/UX Flow

1. **Login**: User lands on `/login`. Clicks "Login with Google," is redirected to Google, and upon success, is redirected back to the app. The app exchanges the code for a token with the backend and stores it, then navigates to the home page (`/`).
2. **Main View (`/`)**: The `CombinedReportPage` is shown. A sidebar allows navigation to other reports. A shared date picker is prominent.
3. **Fetching Data**: When the user selects a date and clicks "Generate Report," a loading indicator appears. The `useReports` hook calls the relevant API service. Data is displayed in the `DataTable` upon success; an error message is shown on failure.
4. **Combined Report**: On this page, after the report is generated, a card or section will appear with the link to the live Google Sheet. A "Copy Link" button will be provided for convenience.
