'use client';

import { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import { getUserStatus, logout as logoutUser } from '@/services/api';

interface User {
  email: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (userData: User) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    let isMounted = true;
    
    const checkUserStatus = async () => {
      if (!isMounted) return;
      
      try {
        // This will never throw an error because of our interceptor
        const data = await getUserStatus();
        
        if (!isMounted) return;
        
        // Always set the user based on the response
        setUser(data?.isAuthenticated ? data.user : null);
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    // Small delay to prevent flashing of loading state
    const timer = setTimeout(() => {
      checkUserStatus();
    }, 100);

    // Cleanup function to prevent state updates on unmounted component
    return () => {
      isMounted = false;
      clearTimeout(timer);
    };
  }, []);

  const login = useCallback((userData: User) => {
    setUser(userData);
  }, []);

  const logout = useCallback(async () => {
    try {
      // Clear local storage and state first to ensure UI updates immediately
      localStorage.clear();
      sessionStorage.clear();
      setUser(null);
      
      // Call the backend logout endpoint
      await logoutUser();
      
      // Redirect to login page with a flag to prevent any auto-redirects
      router.push('/login?loggedOut=true');
      
      // Force a full page reload to ensure all application state is cleared
      window.location.href = '/login?loggedOut=true';
    } catch (error) {
      console.error('Backend logout failed:', error);
      // Even if backend logout fails, we still want to clear the local state
      localStorage.clear();
      sessionStorage.clear();
      setUser(null);
      router.push('/login?error=logout_failed');
    }
  }, [router]);

  const value = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    logout,
  };

  if (isLoading) {
    // You can render a loading spinner here if you want.
    // Returning null for now to ensure no mismatch during hydration.
    return null;
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
