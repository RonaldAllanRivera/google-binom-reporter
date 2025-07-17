'use client';

import React from 'react';
import Layout from '@/components/layout/Layout';
import PrivateRoute from '@/components/PrivateRoute';

interface ReportsLayoutProps {
  children: React.ReactNode;
}

const ReportsLayout: React.FC<ReportsLayoutProps> = ({ children }) => {
  return (
    <PrivateRoute>
      <Layout>{children}</Layout>
    </PrivateRoute>
  );
};

export default ReportsLayout;
