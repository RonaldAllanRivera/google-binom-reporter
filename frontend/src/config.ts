// This file centralizes all API paths for the application.
// The Next.js proxy in next.config.mjs will forward these requests to the backend.

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Keeping the full URL for Google Auth since it's a redirect
export const GOOGLE_AUTH_URL = `${API_BASE_URL}/api/auth/google/`;

// Use relative paths for API calls, as baseURL is set in axios instance
export const COMBINED_REPORT_URL = '/api/combined-report/';
export const BINOM_REPORT_URL = '/api/report/generate/';
export const GOOGLE_ADS_TEST_URL = '/api/google-ads/test/';
export const GOOGLE_ADS_MANAGER_CHECK_URL = '/api/google-ads/manager-check/';
