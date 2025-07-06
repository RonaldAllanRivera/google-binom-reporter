// frontend/pages/auth/google.tsx
import React from "react";
import { apiFetch } from '../../utils/api'; // Adjust path as needed


// Define the expected structure of the API response
interface GoogleAuthUrlResponse {
  auth_url?: string; // The API is expected to return an object with an auth_url property
}

export default function GoogleAuth() {
  const handleConnect = async () => {
    try {
        const data = await apiFetch<GoogleAuthUrlResponse>("/api/auth/google/?redirect=frontend");
        if (data.auth_url) window.location.href = data.auth_url;
    } catch (error) {
        console.error("Error fetching Google Auth URL:", error); // Log the full error for debugging
        let errorMessage = "Failed to get Google Auth URL. Please try again.";
        if (error instanceof Error) {
            errorMessage = error.message;
        }
        alert(errorMessage);
    }
   };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-900 text-white">
      <div className="bg-gray-800 shadow-xl rounded-2xl p-8 w-full max-w-sm border border-gray-700">
        <h2 className="text-2xl font-bold mb-6 text-center text-white">
          Connect Google Account
        </h2>
        <button
          className="w-full flex items-center justify-center gap-2 bg-white hover:bg-gray-100 text-gray-800 font-semibold py-3 rounded-lg shadow transition"
          onClick={handleConnect}
        >
          <img
            src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg"
            alt="Google logo"
            className="w-5 h-5"
          />
          Sign in with Google
        </button>
      </div>
    </div>
);


}
// This component handles the Google authentication flow
// It fetches the authentication URL from the Django backend and redirects the user to Google for login