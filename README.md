# Google Ads + Binom Automated Reporting System

This project is a fully automated multi-platform reporting system that integrates Google Ads (MCC), Binom Tracking, Google Sheets, and Gmail APIs into a unified reporting backend.

The system is designed for marketing agencies and performance advertisers who manage multiple client accounts via Google Ads Manager (MCC). It automates the full reporting pipeline — from data extraction, processing, storage, Google Sheets export, and automated email delivery.

---

## Key Features

### 🆕 July 2025: Backend Refactor

The Google Ads authentication and reporting backend has been refactored for modularity and maintainability:

- **New modules:**
  - `backend/reports/auth_utils.py`: Handles Google OAuth URL building and token exchange.
  - `backend/reports/google_ads_client.py`: Handles Google Ads API client loading.
  - `backend/reports/google_ads_reports.py`: Handles campaign cost fetching and account hierarchy discovery.
- `backend/reports/google_auth_service.py` now acts as a thin facade, importing and exposing all main functions from the new modules.

**Benefits:**
- Improved code organization and readability.
- Easier to maintain, test, and extend Google Ads integration logic.
- Clear separation of authentication, client setup, and reporting logic.


### ✅ Data Cleaning & Output Filtering
- The `/api/combined-report/` endpoint now outputs only relevant campaign data:
  - Excludes entries where both "ACCOUNT NAME" and "CAMPAIGN NAME" are empty.
  - Excludes entries where both "TOTAL SPEND" and "REVENUE" are zero.
  - Removes formula fields (`P/L_FORMULA`, `ROI_FORMULA`) and the `"ROI_VALUE"` field from each output object for a cleaner, more relevant dataset.

✅ **Google Ads API (MCC Integration)**  
- Full Manager Account support (multi-client account discovery).
- Robust, recursive discovery of all client accounts, including those in nested multi-level manager hierarchies.
- Intelligently filters out manager accounts when fetching metrics to prevent API errors.
- **Stable Account Filtering**: Reliably filters and queries only `ENABLED` customer accounts, ensuring application stability by avoiding errors from deactivated or banned accounts.
- Retrieves campaign-level cost data using Google Ads API v18.
- Handles OAuth2 authentication, offline refresh tokens, and secure token storage.

✅ **Binom API Integration & Timezone Parity**  
- Connects with Binom Tracking API to retrieve revenue and lead data.
- API now supports full parity with Binom admin and Postman via the `timezone` query param.
- Supports both `timezone` (preferred, e.g. `America/Atikokan`) and `dateTimeZone` (legacy) query params for compatibility.
- Ensures all report values (including revenue, profit, clicks, etc.) match exactly what is shown in the Binom admin UI for the selected timezone.
- ⚠ **Note:** The timezone used will affect daily reporting boundaries and total revenue/click numbers. Default is `America/Atikokan`.


✅ **Automated Report Generation**  
- Merges and calculates key metrics: Spend, Revenue, Profit/Loss, ROI, Sales.
- Exports reports directly to Google Sheets using the Google Sheets API (Service Account).

✅ **Gmail API Integration (Automated Report Delivery)**  
- Automatically emails daily/weekly/monthly reports via Gmail API.
- Fully OAuth2 secured for safe automated email delivery.

✅ **Fully Automated Scheduling (Cron-Ready)**  
- System is fully schedulable via cron jobs or Render.com jobs.
- Backend management commands support fully automated daily reporting pipelines.

✅ **Enterprise-Grade Error Handling**  
- Robust error handling for all external APIs (Google Ads, Binom, Gmail), with a focus on stability and graceful failure.
- Built-in retry logic and token refresh handling.
- Supports multi-client account scaling.

✅ **Backend Technology Stack**  
- Django 5.x + Django Rest Framework (Python 3.13 compatible)
- PostgreSQL (Render-Ready)
- Google Ads API (v18)
- Google Ads Python SDK (v22.0.0)
- gRPC transport fully stabilized for Windows/Linux environments

✅ **API-First Architecture**  
- RESTful API endpoints for triggering report generation, sending email reports, and full admin access.
- Easily extendable for frontend admin dashboard (React.js + Tailwind ready).

---

## Tech Stack Summary

| Layer       | Stack                          |
| ----------- | ------------------------------- |
| Backend     | Django + DRF                    |
| Database    | PostgreSQL / SQLite (dev mode)  |
| Google Ads  | API v18 via Google Ads SDK v22  |
| Binom API   | REST API (API Key authentication) |
| Google Sheets | Service Account based         |
| Gmail API   | OAuth2 based email sending      |
| Deployment  | Local Windows 10 + Render.com Ready |

---

## Project Highlights

- Fully production-grade, multi-client reporting automation system.
- Built for high-volume agency-style ad account structures.
- Solves real-world Google Ads MCC API complexities (manager discovery, filtering, customer ID parsing, gRPC handling, version locking, etc).
- Modular codebase that cleanly separates API integration, business logic, and reporting layers.

---

## Local Development with Docker

This project is fully containerized for easy and consistent local development. The entire stack (Backend + Frontend) can be launched with a single command.

**Prerequisites:**
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.

**To start the development environment:**

```bash
docker-compose up --build
```

- The backend will be available at `http://localhost:8000`.
- The frontend will be available at `http://localhost:3000`.

Hot-reloading is enabled for both services, so any changes you make to the code will be reflected automatically.

---

## Manual Usage

1. Clone the repository.
2. Setup virtual environment.
3. Install all pinned dependencies.
4. Create and configure `.env` with Google credentials, Binom API keys, Developer Token, etc.
5. Place `service_account.json` under `/backend/reports/` for Google Sheets.
6. Run Django backend locally (`python manage.py runserver`).
7. Authenticate via Google OAuth2 at `/api/auth/google/` to register Google Ads access.
8. Use API endpoints to trigger reporting and generate Sheets/emails.
9. To retrieve a Binom campaign report matching the Binom admin UI, use:
- GET /api/report/generate/?start_date=2025-05-01&end_date=2025-05-31&trafficSourceIds=1,6&dateType=custom-time&timezone=America/Atikokan
Or supply any supported Binom timezone string.
- The `timezone` parameter is required for parity with the Binom admin and affects all metric values.
- Changing the timezone will change daily cutoffs and revenue/click totals for the same date range.


---

## Future Extensions (Planned)

- Admin dashboard frontend (React.js + Tailwind CSS)
- Full Render.com deployment pipeline
- UI-based multi-account management and reporting logs

---

> ⚠ **This system is built as a portfolio-grade enterprise backend demonstration for large-scale automated reporting pipelines across multiple advertising and analytics platforms.**
