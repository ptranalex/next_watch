/**
 * Authentication API types
 */

/**
 * Login credentials interface
 */
export interface LoginCredentials {
  email: string;
  password: string;
}

/**
 * User registration data interface
 */
export interface RegisterData {
  email: string;
  username?: string;
  password: string;
  password_confirm: string;
}

/**
 * Authentication tokens interface
 */
export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

/**
 * User data interface
 */
export interface UserData {
  id: number;
  email: string;
  username?: string;
}

/**
 * Token refresh request interface
 */
export interface TokenRefreshRequest {
  refresh_token: string;
}
