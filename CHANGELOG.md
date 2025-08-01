# CHANGELOG

## Version 2.2.0 - July 2025: Authentication Security & Global Logout

### 🔒 Authentication & Logout Improvements
- **Fullstack Auth Security Confirmed:**
  - Django backend and React/Next.js frontend now provide robust, secure authentication using session cookies and CSRF protection.
  - All sensitive API and admin endpoints are protected by session authentication and permission classes.
- **Global Logout:**
  - Frontend logout button calls the backend logout endpoint, which destroys the session server-side and deletes session cookies for all paths/domains.
  - Logging out from the frontend logs the user out everywhere, including the Django admin and all browser tabs.
  - Frontend clears all local state and redirects to login after logout.
- **Best Practices:**
  - HttpOnly cookies are never manipulated by JS; all session destruction is handled by the backend.
  - Cross-origin/CORS and cookie settings are configured for secure development and production environments.

## Version 2.1.0 - July 2025: Combined Report Enhancementsor & Test Improvements

### 🚀 Frontend Architecture
- **Project Restructuring**: Moved to a modular `src/` based structure for better code organization
- **Component Library**: Added Material-UI components and icons for a consistent UI
- **State Management**: Implemented React Context for theme management
- **API Integration**: Added Axios for API requests with proper error handling

### 🧪 Testing
- **Backend Tests**: Added comprehensive test cases for report generation
- **Mocking**: Implemented proper mocking for external API calls
- **Test Coverage**: Improved test coverage for critical paths

### 🛠️ Developer Experience
- **Dependency Updates**: Upgraded to latest versions of key packages
- **TypeScript**: Enhanced type safety throughout the application
- **Documentation**: Updated README with new setup instructions

## Version 2.0.0 - July 2025: Frontend Refactor & Test Improvements

### 🚀 Frontend Architecture
- **Project Restructuring**: Moved to a modular `src/` based structure for better code organization
- **Component Library**: Added Material-UI components and icons for a consistent UI
- **State Management**: Implemented React Context for theme management
- **API Integration**: Added Axios for API requests with proper error handling

### 🧪 Testing
- **Backend Tests**: Added comprehensive test cases for report generation
- **Mocking**: Implemented proper mocking for external API calls
- **Test Coverage**: Improved test coverage for critical paths

### 🛠️ Developer Experience
- **Dependency Updates**: Upgraded to latest versions of key packages
- **TypeScript**: Enhanced type safety throughout the application
- **Documentation**: Updated README with new setup instructions

## Version 1.9.0 - July 2025: Backend API Authentication

### ✨ New Feature: Secure API Endpoints
- **Implemented Session-Based Authentication**: Secured all sensitive data-reporting endpoints (`/api/report/generate/`, `/api/google-ads/test/`, etc.) to protect them from public access.
- **Custom Permission Class**: Created a new `IsGoogleOrSuperuser` permission in Django REST Framework. Access is now restricted to users authenticated via Google OAuth or to Django superusers.
- **Django Session Login**: The Google OAuth callback now logs the user into a Django session, enabling them to access the newly secured endpoints after authenticating.

### 🔧 Configuration & Bug Fixes
- **Cross-Origin Resource Sharing (CORS)**: Installed and configured `django-cors-headers` to allow the Next.js frontend (`localhost:3000`) to communicate with the Django backend (`localhost:8000`).
- **Cross-Origin Cookies**: Correctly configured `SESSION_COOKIE_SAMESITE = 'None'` and `CSRF_COOKIE_SAMESITE = 'None'` to allow the browser to send session and CSRF cookies across different origins.
- **HTTPS Development Server**: Added `django-extensions` and configured the backend to run over HTTPS (`runserver_plus --cert-file cert.pem --key-file key.pem`), a requirement for secure cross-origin cookies.
- **Frontend Credentials**: Updated the frontend `apiFetch` utility to include `credentials: 'include'` in all requests, ensuring session cookies are sent to the backend.

## Version 1.8.0 - July 2025: Dockerized Local Development

### ✨ New Feature: Dockerized Development Environment
- **Added `docker-compose.yml`** to orchestrate the entire application stack (backend and frontend).
- **Created `Dockerfile.dev`** for both Django and Next.js services, optimized for local development with hot-reloading.
- **Simplified Setup**: Developers can now run the entire application with a single command (`docker-compose up --build`), eliminating the need for manual environment setup.
- **Consistent Environment**: Ensures all developers work with the same dependencies and environment, reducing "it works on my machine" issues.

## Version 1.7.0 - July 2025: Backend Refactor & Modularization

### 🆕 Major Refactor: Google Ads Backend Modularization
- **Refactored all Google Ads authentication and reporting logic into separate modules:**
  - `backend/reports/auth_utils.py`: Google OAuth URL building and token exchange.
  - `backend/reports/google_ads_client.py`: Google Ads API client loader.
  - `backend/reports/google_ads_reports.py`: Campaign cost fetching & account hierarchy traversal.
- `backend/reports/google_auth_service.py` is now a thin facade, importing and exposing functions from the new modules.
- **Benefits:**
  - Improved maintainability and code organization.
  - Easier to extend and test Google Ads integration logic.
  - Clear separation of authentication, client setup, and reporting logic.

## Version 1.6.0 - Output Data Cleaning & API Refinement

### ✅ Data Cleaning & API Output Improvements
- The `/api/combined-report/` backend endpoint now:
  - Excludes entries with both "ACCOUNT NAME" and "CAMPAIGN NAME" empty.
  - Excludes entries with both "TOTAL SPEND" and "REVENUE" equal to zero.
  - Removes `"P/L_FORMULA"`, `"ROI_FORMULA"`, and `"ROI_VALUE"` fields from all output objects.
- Output is now cleaner and more relevant for downstream processing and reporting.

## Version 1.5.0 - Application Stability & Final Data Verification

### ✅ Critical Fixes & Stability Improvements
- **Resolved Application Crashes**: Fixed a critical and persistent `AttributeError` that caused the server to crash when fetching data for deactivated or banned Google Ads accounts.
- **Simplified Error Handling**: Removed the complex and faulty error-handling logic that attempted to process deactivated accounts. The system now relies on a more robust and stable approach.
- **Restored `ENABLED` Account Filtering**: The account discovery process now strictly queries for accounts with `status = 'ENABLED'`, preventing API errors and ensuring application stability.

### ✅ Data Integrity & Finalization
- **Verified Data Accuracy**: The final campaign cost report is now stable and has been verified to be correct for all active and accessible accounts.
- **Finalized JSON Output**: The system now reliably produces the exact JSON output required, sorted correctly by Account and Campaign name. Deactivated accounts are now correctly excluded from the final report to ensure stability.

---

## Version 1.4.0 - Google Ads Data Completeness & Finalization

### ✅ Google Ads Data Integrity and Reporting Fixes
- **Recursive Account Discovery**: Implemented a robust, recursive discovery function (`get_all_accounts_in_hierarchy`) to reliably find all client accounts, including those nested under multiple manager levels.
- **Manager Account Filtering**: Fixed critical API errors by intelligently filtering out manager accounts (`is_manager=False`) before requesting campaign metrics, as the API disallows metric queries on manager accounts.
- **Handled Banned Accounts**: Confirmed that the system correctly excludes banned or disabled accounts (e.g., "Polar Cooling") from discovery, ensuring the final report only contains active, billable accounts.
- **Finalized JSON Output**: Adjusted the campaign cost report to exactly match the user's required format, including `Account`, `CustomerID` (with hyphens), `Campaign`, `Currency`, and `Cost`.
- **Production-Ready Logging**: Replaced all temporary `print` statements with structured `logging` for better error tracking and maintainability.

---


## Version 1.3.1 - Frontend OAuth & Dual-Callback Integration

### ✅ Google OAuth (Dual Callback) and Next.js Integration
- Integrated Google OAuth dual-callback flow: both backend and frontend can handle OAuth redirects.
- Next.js frontend now supports Google login and authorization callback at `/auth/google-callback`.
- All four required endpoints are now available and fully working in both backend and frontend:
  * /api/auth/google/
  * /api/auth/google/callback/
  * /api/report/generate/
  * /api/google-ads/test/
- Google account can be authorized from either Django or React/Next.js UI.

### 🚧 Known Issues / Pending
- Google Ads “leaf”/client account data is still returning cost = 0 for all campaigns. **(Root cause: Developer token is Basic Access; must wait for Google Standard Access approval.)**
- Full multi-account MCC reporting is blocked until Standard Access is granted.
- All removed backend functions and files (merged report, email, Google Sheets, etc.) will be restored after Google approves Standard Access for the developer token.

---

## Updated Daily Task List

- [x] Connect Google OAuth from both backend and frontend (dual-callback) ✅
- [x] Implement working React/Next.js pages for all required endpoints ✅
- [x] Match backend and frontend OAuth redirect URIs (localhost only, per Google policy) ✅
- [x] Confirm Binom reporting works in the UI ✅
- [x] Confirm Google Ads campaign data loads in the UI (cost=0 with Basic Access) ✅
- [ ] **Wait for Google Ads API Standard Access approval for real cross-account data** ⏳
- [ ] Restore merged report, Sheets, and email endpoints after approval
- [ ] (Optional) Improve frontend UI/UX, add dashboard and navigation
- [ ] Document setup for new devs

---

**Once Google Standard Access is approved, full multi-client Google Ads data will be available, and you can re-enable advanced backend features.**


## Version 1.3.0 - Minimal Backend Refactor for Google/Binom Reporting

### ✅ Temporary Cleanup for Core Endpoints Only
- **Removed**: All unused files and functions related to merged reports, Google Sheets, and email sending.
- **Exposed Only**: Four required endpoints:
  * /api/auth/google/
  * /api/auth/google/callback/
  * /api/report/generate/
  * /api/google-ads/test/
- **Note**: All removed files and functions will be restored after resolving Google API access/permissions issues.

### 🛠 Internal Refactoring & Docs
- Updated backend codebase for maximum clarity and maintainability.
- Added detailed docstrings to each API endpoint for internal onboarding.
- Cleaned up all unused URL routes and modules.

---

## Daily Task List (Next Steps)
- [ ] **Implement frontend UI for all 4 endpoints using Next.js + React**
    - Google OAuth login and callback
    - Campaign cost reporting UI (Google Ads test)
    - Binom raw report UI
- [ ] Add loading/error states for all API interactions
- [ ] Write frontend API client hooks
- [ ] Prepare for restoring email, merging, and Google Sheets features after Google API approval
- [ ] QA: Test all endpoints with real data in production-like environment

---

*Once Google Ads API standard access is restored, all removed backend logic will be re-enabled and integrated into the production pipeline.*


## Version 1.2.0 - Binom API Timezone Support & Parity

### ✅ Binom API Timezone Parameter Support
- API now fully supports `timezone` param, matching Binom admin and JS include.
- Accepts both `timezone` and legacy `dateTimeZone` query params (with `timezone` preferred).
- Always passes through the user’s selected timezone value to Binom as `timezone=...`.
- Output now matches Binom admin and Postman reports exactly, including metrics like revenue and clicks.

### ✅ Bug Fixes & Improvements
- Fixed issue where reporting endpoint silently defaulted to a fallback timezone, causing metric mismatches.
- Added explicit documentation of timezone effect on daily/period revenue totals.
- Backend now enforces a single, user-specified timezone per request for full parity.

### ⚠️ Timezone Documentation
- Note: Reporting numbers (revenue, clicks, etc.) will differ depending on the `timezone` used.
- Default timezone is now `America/Atikokan` for consistent agency-wide reporting, unless overridden via API.


## Version 1.1.0 - MCC Google Ads API Full Integration

### ✅ OAuth2 Google Authentication
- Google OAuth2 fully implemented with offline refresh token handling.
- User email extracted via userinfo API.
- Secure storage of tokens in GoogleAccount model.

### ✅ Google Ads API Full Multi-Account Discovery
- Implemented GoogleAdsClient with MCC (Manager Account) support.
- Dynamic discovery of accessible clients under MCC using CustomerService.
- Correctly extract customer IDs from resource names.
- Filtered ENABLED customer accounts only.
- Excluded inactive, suspended, and canceled sub-accounts.
- Fully compatible with Google Ads API v18.

### ✅ Error Handling & Stability Improvements
- Fully resolved gRPC transport issues.
- Stabilized SDK version management (google-ads 22.0.0).
- Corrected ID parsing, query formats, and resource name handling.
- Fully stable GRPC streaming for SearchStream API calls.

### ✅ Development Environment Stabilization
- Locked dependency versions for Windows compatibility.
- grpcio / grpcio-status / google-ads fully version pinned for 2025 standards.

---

## Day 1 - Project Bootstrap

- Initialized Django backend
- Initialized React frontend
- Setup Tailwind CSS
- Created .env, .gitignore, README, CHANGELOG
