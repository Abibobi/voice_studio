import { Navigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isLoggedIn, loading } = useAuth();

  if (loading) {
    return (
      <div className="auth-loading">
        <span className="spinner spinner--lg" />
        <p>Verifying session…</p>
      </div>
    );
  }

  if (!isLoggedIn) return <Navigate to="/login" replace />;
  return children;
}