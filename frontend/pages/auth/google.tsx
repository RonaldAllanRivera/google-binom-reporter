// frontend/pages/auth/google.tsx
import React from 'react';
import { apiFetch } from '../../utils/api';
import { GoogleIcon } from '../../components/icons';
import { ThemeToggle } from '../../components/theme-toggle';

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
    <div className="w-full lg:grid lg:min-h-[100vh] lg:grid-cols-2 xl:min-h-[100vh]">
      <div className="hidden bg-muted lg:flex items-center justify-center flex-col text-center p-10 relative">
        <div className="absolute top-4 right-4">
          <ThemeToggle />
        </div>
        <div className="relative z-20">
          <h1 className="text-5xl font-bold">Google Binom Reporter</h1>
          <p className="text-xl text-muted-foreground mt-4">Automate. Analyze. Accelerate.</p>
          <p className="text-lg text-muted-foreground mt-2">Unified Google Ads and Binom reporting at your fingertips.</p>
        </div>
      </div>
      <div className="flex items-center justify-center py-12">
        <div className="mx-auto grid w-[350px] gap-6">
          <div className="grid gap-2 text-center">
            <h1 className="text-3xl font-bold">Connect Account</h1>
            <p className="text-balance text-muted-foreground">Please sign in with Google to continue</p>
          </div>
          <div className="grid gap-4">
            <button
              onClick={handleConnect}
              className="w-full inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2"
            >
              <GoogleIcon className="mr-2 h-4 w-4" />
              Sign in with Google
            </button>
          </div>
          <div className="mt-4 text-center text-sm">
            This will redirect you to Google's secure sign-in page.
          </div>
        </div>
      </div>
    </div>
  );
}
// This component handles the Google authentication flow
// It fetches the authentication URL from the Django backend and redirects the user to Google for login