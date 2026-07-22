import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Loader from '../components/Loader';

import Login from '../pages/Login';
import Dashboard from '../pages/Dashboard';

/**
 * PublicRoute: Redirects authenticated users away from /login to the dashboard.
 */
const PublicRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  if (loading) return <Loader fullScreen />;
  return isAuthenticated ? <Navigate to="/" replace /> : children;
};

/**
 * PrivateRoute: Redirects unauthenticated users to /login.
 */
const PrivateRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  if (loading) return <Loader fullScreen />;
  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

const AppRoutes = () => {
  return (
    <Routes>
      {/* Public: Login */}
      <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />

      {/* Protected: Dashboard (single page — no layout wrapper) */}
      <Route path="/" element={<PrivateRoute><Dashboard /></PrivateRoute>} />

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

export default AppRoutes;
