"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import AuthTokenManager from "@/src/utils/authTokenManager";
import { postData } from "@/src/services/api-client";

// User type definition
export interface User {
  id: string;
  name: string;
  email: string;
  role?: string;
}

// Auth context interface
interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
  error: string | null;
  isAuthenticated: boolean;
}

// Create the auth context with default values
const AuthContext = createContext<AuthContextType>({
  user: null,
  login: async () => {},
  logout: () => {},
  isLoading: false,
  error: null,
  isAuthenticated: false,
});

// Hook to use the auth context
export const useAuth = () => useContext(AuthContext);

// Props for the auth provider
interface AuthProviderProps {
  children: ReactNode;
}

// Auth provider component
export const AuthProvider = ({ children }: AuthProviderProps) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Check if the user is logged in on component mount
  useEffect(() => {
    const checkAuthState = async () => {
      try {
        // Check if token is valid
        if (AuthTokenManager.isTokenValid()) {
          // Get user info from the token
          const userInfo = AuthTokenManager.getUserInfo();

          if (userInfo) {
            // Set the user info from token
            setUser({
              id: userInfo.id,
              name: userInfo.name || "User",
              email: userInfo.email || "",
              role: userInfo.role,
            });
            setIsAuthenticated(true);
          } else {
            // Clear invalid token
            AuthTokenManager.removeToken();
          }
        }
      } catch (err) {
        console.error("Error checking auth state:", err);
        setError("Authentication check failed");
        AuthTokenManager.removeToken();
      } finally {
        setIsLoading(false);
      }
    };

    checkAuthState();
  }, []);

  // Login function
  const login = async (email: string, password: string) => {
    setIsLoading(true);
    setError(null);

    try {
      // Call the login API
      const response = await postData<{ token: string; user: User }>(
        "/auth/login",
        { email, password }
      );

      // Store the token
      AuthTokenManager.setToken(response.token);

      // Set user data
      setUser(response.user);
      setIsAuthenticated(true);
    } catch (err) {
      console.error("Login error:", err);
      setError("Login failed. Please check your credentials and try again.");

      // For development/testing without a backend
      if (process.env.NODE_ENV === "development") {
        // Mock user data for development
        const mockUser: User = {
          id: "user123",
          name: "Demo User",
          email,
          role: "user",
        };

        // Mock token with 1 hour expiration
        const mockToken =
          "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyMTIzIiwibmFtZSI6IkRlbW8gVXNlciIsImVtYWlsIjoiZGVtb0BleGFtcGxlLmNvbSIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxOTcyOTAxNjAwfQ.mockSignature";

        AuthTokenManager.setToken(mockToken);
        setUser(mockUser);
        setIsAuthenticated(true);
        setError(null);
      } else {
        throw err;
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Logout function
  const logout = () => {
    setUser(null);
    setIsAuthenticated(false);
    AuthTokenManager.removeToken();
  };

  // Provide the auth context to children components
  return (
    <AuthContext.Provider
      value={{
        user,
        login,
        logout,
        isLoading,
        error,
        isAuthenticated,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
