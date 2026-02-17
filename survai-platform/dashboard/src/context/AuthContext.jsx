import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

const DEFAULT_USERS = [
  { username: 'admin', password: 'admin123', role: 'admin', tenantId: 'itcurves', orgName: 'IT Curves' },
  { username: 'ozark', password: 'ozark123', role: 'admin', tenantId: 'ozark', orgName: 'Ozark Regional Transit' },
  { username: 'newbraunfels', password: 'nb123', role: 'admin', tenantId: 'newbraunfels', orgName: 'New Braunfels Transit' },
  { username: 'demo', password: 'demo', role: 'viewer', tenantId: 'demo', orgName: 'Demo Agency' },
];

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const stored = localStorage.getItem('survai_user');
    if (stored) {
      try {
        setUser(JSON.parse(stored));
      } catch {
        localStorage.removeItem('survai_user');
      }
    }
    setLoading(false);
  }, []);

  const login = (username, password) => {
    const found = DEFAULT_USERS.find(
      u => u.username === username && u.password === password
    );
    if (found) {
      const userData = { username: found.username, role: found.role, tenantId: found.tenantId, orgName: found.orgName };
      setUser(userData);
      localStorage.setItem('survai_user', JSON.stringify(userData));
      return { success: true };
    }
    return { success: false, error: 'Invalid username or password' };
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('survai_user');
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}

export default AuthContext;
