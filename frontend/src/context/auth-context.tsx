"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { authApi } from "@/lib/auth-api";
import type { User } from "@/lib/types";

interface AuthState {
  user: User | null;
  loading: boolean;
}

interface AuthContextValue extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => Promise<void>;
  refresh: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({ user: null, loading: true });

  const fetchMe = useCallback(async () => {
    try {
      const user = await authApi.me();
      setState({ user, loading: false });
    } catch {
      setState({ user: null, loading: false });
    }
  }, []);

  // Hydrate on mount
  useEffect(() => {
    fetchMe();
  }, [fetchMe]);

  const login = useCallback(async (email: string, password: string) => {
    await authApi.login({ email, password });
    await fetchMe();
  }, [fetchMe]);

  const register = useCallback(
    async (email: string, password: string, fullName?: string) => {
      await authApi.register({ email, password, full_name: fullName });
      await login(email, password);
    },
    [login],
  );

  const logout = useCallback(async () => {
    await authApi.logout();
    setState({ user: null, loading: false });
  }, []);

  const refresh = useCallback(async () => {
    await authApi.refresh();
    await fetchMe();
  }, [fetchMe]);

  return (
    <AuthContext.Provider value={{ ...state, login, register, logout, refresh }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside <AuthProvider>");
  return ctx;
}
