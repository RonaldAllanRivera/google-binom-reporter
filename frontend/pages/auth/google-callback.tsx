import { useRouter } from "next/router";
import React, { useEffect, useState } from "react";
import { apiFetch } from '../../utils/api';

interface AuthCallbackResponse {
  message?: string;
  error?: string;
}

export default function GoogleCallback() {
  const router = useRouter();
  const { code } = router.query;
  const [message, setMessage] = useState<string>("Authorizing...");

  useEffect(() => {
    if (code && typeof code === 'string') {
      apiFetch<AuthCallbackResponse>(`/api/auth/google/callback/?code=${encodeURIComponent(code)}&redirect=frontend`)
        .then(responseData => {
          setMessage(responseData.message || responseData.error || "Authorization complete. Check status.");
        })
        .catch(error => {
          console.error("Google auth callback failed:", error);
          let errorMessage = "Authentication failed. Please try again.";
          if (error instanceof Error) {
            errorMessage = error.message;
          }
          setMessage(errorMessage);
        });
    } else if (router.isReady && !code) {
      setMessage("Authorization code not found in URL.");
    }
  }, [code, router.isReady]);

  // Optional: Google sign-in button (redirects to /auth/google)
  const handleGoogleSignIn = () => {
    router.push('/auth/google');
  };

  return (
  <div className="flex min-h-screen items-center justify-center bg-gray-900 text-white">
    <div className="bg-gray-800 rounded-2xl shadow-lg p-8 w-full max-w-md flex flex-col items-center border border-gray-700">
      <h2 className="text-2xl font-bold mb-4 text-white">Google OAuth Callback</h2>
      <p
        className={`mb-6 text-center ${
          message?.toLowerCase().includes('error')
            ? 'text-red-500'
            : 'text-gray-300'
        }`}
      >
        {message}
      </p>
      <button
        className="flex items-center gap-2 px-6 py-2 rounded-full shadow transition bg-white border border-gray-200 hover:bg-gray-100 text-gray-800 font-semibold"
        onClick={handleGoogleSignIn}
      >
        <img
          src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg"
          alt="Google logo"
          className="w-5 h-5"
        />
        <span>Sign in with Google</span>
      </button>
    </div>
  </div>
);

}
