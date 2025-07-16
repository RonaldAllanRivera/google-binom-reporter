// frontend/utils/api.ts

export async function apiFetch<T = unknown>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const url = `${process.env.NEXT_PUBLIC_BACKEND_URL}${path}`;
  const defaultHeaders: HeadersInit = {
    // "Content-Type": "application/json", // Use this if you are SENDING a JSON body (e.g. POST, PUT)
    "Accept": "application/json",       // We generally EXPECT JSON responses
  };

  const res = await fetch(url, {
    ...options,
    credentials: 'include', // <-- IMPORTANT: This sends cookies with cross-origin requests
    headers: {
      ...defaultHeaders,
      ...(options?.headers || {}),
    },
  });

  if (!res.ok) {
    let errorBodyText = res.statusText; // Default error message
    try {
      const errorBody = await res.text(); // Try to get more details from the body
      if (errorBody) {
        // Attempt to parse as JSON for structured error messages (common in APIs)
        try {
          const parsedError = JSON.parse(errorBody);
          errorBodyText = parsedError.message || parsedError.detail || parsedError.error || errorBody;
        } catch { // Error object is not needed, so we can omit the binding
          // If not JSON, use the raw text
          errorBodyText = errorBody;
        }
      }
    } catch (e) {
      // Ignore if reading error body fails, stick to statusText
      console.warn("Could not read error response body for non-ok response", e);
    }
    throw new Error(`API error: ${res.status} - ${errorBodyText}`);
  }

  // Handle 204 No Content: successful request with no response body
  if (res.status === 204) {
    return undefined as T; // Caller should expect T to be compatible with undefined (e.g. void, or T | undefined)
  }

  try {
    return await res.json() as T; // Parse the response body as JSON
  } catch (parseError) {
    console.error(`API error: Failed to parse JSON response from ${path}. Status: ${res.status}`, parseError);
    throw new Error(`API error: Malformed JSON response from ${path}. Expected JSON. Status: ${res.status}.`);
  }
}
