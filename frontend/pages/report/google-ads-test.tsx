// frontend/pages/report/google-ads-test.tsx
import React, { useState } from "react";
import { apiFetch } from '../../utils/api'; // Adjust path as needed

// Define a more specific type for the Google Ads test data
// This can be refined further if the structure of the API response is known
type GoogleAdsTestData = Record<string, unknown> | Array<Record<string, unknown>>;

export default function GoogleAdsTest() {
  const [data, setData] = useState<GoogleAdsTestData | null>(null);
  const [form, setForm] = useState({
    email: "",
    start_date: "",
    end_date: "",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    // The 'form' object is compatible with URLSearchParams constructor
    const params = new URLSearchParams(form).toString();
    try {
      const json = await apiFetch<GoogleAdsTestData>(`/api/google-ads/test/?${params}`);
      setData(json);
    } catch (error) {
      console.error("Error fetching Google Ads test data:", error);
      // Optionally, display an error message to the user
      // alert("Failed to fetch Google Ads data. Please try again.");
      setData(null); // Clear previous data on error
    }
  };

  return (
    <div style={{ padding: 40 }}>
      <h2>Google Ads Campaign Cost Test</h2>
      <form onSubmit={handleSubmit}>
        <input name="email" type="email" value={form.email} onChange={handleChange} required />
        <input name="start_date" type="date" value={form.start_date} onChange={handleChange} required />
        <input name="end_date" type="date" value={form.end_date} onChange={handleChange} required />
        <button type="submit">Get Campaigns</button>
      </form>
      <pre>{data ? JSON.stringify(data, null, 2) : null}</pre>
    </div>
  );
}
