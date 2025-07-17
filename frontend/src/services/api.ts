import axios from 'axios';
import { Dayjs } from 'dayjs';
import {
  COMBINED_REPORT_URL,
  GOOGLE_ADS_TEST_URL,
  GOOGLE_ADS_MANAGER_CHECK_URL,
  BINOM_REPORT_URL,
  GOOGLE_AUTH_URL,
} from '@/config';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  withCredentials: true, // Send cookies with requests
  headers: {
    'Content-Type': 'application/json',
  },
});

// Helper function to get a cookie by name
const getCookie = (name: string): string | null => {
  if (typeof document === 'undefined') {
    return null;
  }
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
};

// Add a request interceptor to include the CSRF token
api.interceptors.request.use(
  (config) => {
    const token = getCookie('csrftoken');
    if (token) {
      config.headers['X-CSRFToken'] = token;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

const formatDate = (date: Dayjs) => date.format('YYYY-MM-DD');

export const getGoogleAuthUrl = async () => {
  const response = await api.get(GOOGLE_AUTH_URL);
  return response.data;
};

export const getUserStatus = async () => {
  const response = await api.get('/api/auth/user/');
  return response.data;
};

export const logout = async () => {
  const response = await api.post('/api/auth/logout/');
  return response.data;
};

export const getCombinedReport = async (startDate: Dayjs, endDate: Dayjs) => {
  const params = {
    start_date: formatDate(startDate),
    end_date: formatDate(endDate),
  };
  const response = await api.get(COMBINED_REPORT_URL, { params });
  return response.data;
};

export const getGoogleAdsTest = async (email: string, startDate: Dayjs, endDate: Dayjs) => {
  const params = {
    email,
    start_date: formatDate(startDate),
    end_date: formatDate(endDate),
  };
  const response = await api.get(GOOGLE_ADS_TEST_URL, { params });
  return response.data;
};

export const getGoogleAdsManagerCheck = async (email: string) => {
  const params = { email };
  const response = await api.get(GOOGLE_ADS_MANAGER_CHECK_URL, { params });
  return response.data;
};

export const getBinomReport = async (startDate: Dayjs, endDate: Dayjs) => {
  const params = {
    start_date: formatDate(startDate),
    end_date: formatDate(endDate),
  };
  const response = await api.get(BINOM_REPORT_URL, { params });
  return response.data;
};

export default api;

