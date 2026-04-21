import { createContext, useContext, useEffect, useState } from "react";
import { clearToken, getCurrentUser, getToken, saveToken } from "../api/auth";
import type { User } from "../types";

interface AuthContextValue {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (token: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = getToken();
    if (!token) { setIsLoading(false); return; }
    getCurrentUser()
      .then(setUser)
      .catch(() => clearToken())
      .finally(() => setIsLoading(false));
  }, []);

  async function login(token: string) {
    saveToken(token);
    const me = await getCurrentUser();
    setUser(me);
  }

  function logout() {
    clearToken();
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, isLoading, isAuthenticated: !!user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}
