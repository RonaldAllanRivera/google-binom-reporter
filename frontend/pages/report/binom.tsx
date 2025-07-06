// frontend/pages/report/binom.tsx
import React, { useState } from "react";
import { apiFetch } from "../../utils/api"; // Assuming apiFetch is correctly imported

// Define a more specific type for the report data
// This can be refined further if the structure of the Binom report is known
type BinomReportData = Record<string, unknown> | Array<Record<string, unknown>>;

export default function BinomReport() {
  const [data, setData] = useState<BinomReportData | null>(null);
  const [form, setForm] = useState({
    start_date: "",
    end_date: "",
    trafficSourceIds: "1,6",
    dateType: "custom-time",
    timezone: "America/Atikokan",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    // The 'form' object is compatible with URLSearchParams constructor
    const params = new URLSearchParams(form).toString();
    try {
      // If apiFetch is generic (e.g., apiFetch<T>()), you can use:
      // const json = await apiFetch<BinomReportData>(`/api/report/generate/?${params}`);
      // Otherwise, if apiFetch returns Promise<any> or Promise<unknown>, json will be of that type.
      const json = await apiFetch(`/api/report/generate/?${params}`);
    setData(json);
    } catch (error) {
      console.error("Error fetching Binom report:", error);
      // Optionally, display an error message to the user
      // alert("Failed to fetch report. Please try again.");
      setData(null); // Clear previous data on error
    }
  };

  return (
    <div style={{ padding: 40 }}>
      <h2>Binom Raw Report</h2>
      <form onSubmit={handleSubmit}>
        <input name="start_date" type="date" value={form.start_date} onChange={handleChange} required />
        <input name="end_date" type="date" value={form.end_date} onChange={handleChange} required />
        <input name="trafficSourceIds" value={form.trafficSourceIds} onChange={handleChange} />
        <input name="dateType" value={form.dateType} onChange={handleChange} />
        <input name="timezone" value={form.timezone} onChange={handleChange} />
        <button type="submit">Get Report</button>
      </form>
      <pre>{data ? JSON.stringify(data, null, 2) : null}</pre>
    </div>
  );
}
