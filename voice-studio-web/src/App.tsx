import { Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import ProtectedRoute from "./components/ProtectedRoute";

import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import SignupPage from "./pages/SignupPage";
import ModelSelectPage from "./pages/ModelSelectPage";
import TurboPage from "./pages/TurboPage";
import MultilingualPage from "./pages/MultilingualPage";
import DashboardPage from "./pages/DashboardPage";
import NotFoundPage from "./pages/NotFoundPage";

export default function App() {
  return (
    <Layout>
      <Routes>
        {/* Public routes */}
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />

        {/* Protected routes */}
        <Route
          path="/models"
          element={
            <ProtectedRoute>
              <ModelSelectPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/turbo"
          element={
            <ProtectedRoute>
              <TurboPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/multilingual"
          element={
            <ProtectedRoute>
              <MultilingualPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          }
        />

        {/* 404 */}
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </Layout>
  );
}