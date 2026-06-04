import { createContext, useContext, useState, useEffect, useCallback } from "react";
import type { ReactNode } from "react";
import { login as apiLogin, signup as apiSignup, me as apiMe } from "../api";
import { setToken, getToken, clearToken } from "../lib/auth";

/* ── Types ── */
type User = { id: number; email: string };

interface AuthState {
  user: User | null;
  token: string | null;
  isLoggedIn: boolean;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

/* ── Context ── */
const AuthContext = createContext<AuthState | null>(null);

/* ── Provider ── */
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setTokenState] = useState<string | null>(getToken());
  const [loading, setLoading] = useState(!!getToken()); // only loading if we have a stored token to validate

  /* Validate stored token on mount */
  useEffect(() => {
    const stored = getToken();
    if (!stored) {
      setLoading(false);
      return;
    }
    apiMe()
      .then((u) => {
        setUser(u);
        setTokenState(stored);
      })
      .catch(() => {
        clearToken();
        setTokenState(null);
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const res = await apiLogin(email, password);
    setToken(res.access_token);
    setTokenState(res.access_token);
    const u = await apiMe();
    setUser(u);
  }, []);

  const signup = useCallback(async (email: string, password: string) => {
    await apiSignup(email, password);
    /* Auto-login after signup */
    const res = await apiLogin(email, password);
    setToken(res.access_token);
    setTokenState(res.access_token);
    const u = await apiMe();
    setUser(u);
  }, []);

  const logout = useCallback(() => {
    clearToken();
    setTokenState(null);
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isLoggedIn: !!user,
        loading,
        login,
        signup,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

/* ── Hook ── */
export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be inside <AuthProvider>");
  return ctx;
}
