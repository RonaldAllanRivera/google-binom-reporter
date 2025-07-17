// e:\fullstack\google-binom-reporter\frontend\components\documentation.tsx
import React from 'react';
import ReactMarkdown from 'react-markdown';

// The full content from your README.md file
const markdownContent = `
# Welcome to the Google Binom Reporter

This is a full-stack application designed to automate reporting by integrating data from Google Ads and Binom Tracker.

---

## How to Get Started

1.  **Login**: Click the **Go to Login Page** button in the top right to authenticate with your Google Account. This is required to access the reporting features.

2.  **Connect Accounts**: Once logged in, you will be guided to connect your Google Ads (MCC) and Binom accounts.

3.  **Generate Reports**: After connecting your accounts, you can generate combined reports, view analytics, and automate email delivery.

---

## Project Purpose

This system solves the complex task of aggregating marketing data from multiple sources, providing a unified dashboard for performance analysis. It's built with a modern tech stack to be robust, scalable, and easy to maintain.
`;

export default function Documentation() {
  return (
    <div className="prose dark:prose-invert max-w-none p-6">
      <ReactMarkdown>{markdownContent}</ReactMarkdown>
    </div>
  );
}