import type { Session } from '../../contexts/SessionContext';
import { ACCESS_TOKEN_KEY } from './constant';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

interface LoginResponse {
  access_token: string;
  token_type: string;
}

interface UserResponse {
  id: number;
  email: string;
  first_name?: string;
  last_name?: string;
  is_active: boolean;
  is_superuser: boolean;
  is_verified: boolean;
}

interface AuthResult {
  success: boolean;
  session?: Session;
  error?: string;
}

/**
 * Sign in with email and password
 */
export async function signInWithCredentials(
  email: string,
  password: string
): Promise<AuthResult> {
  try {
    // Login to get JWT token
    const loginFormData = new URLSearchParams();
    loginFormData.append('username', email);
    loginFormData.append('password', password);

    const loginResponse = await fetch(`${API_BASE_URL}/auth/jwt/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: loginFormData.toString(),
    });

    if (!loginResponse.ok) {
      const errorData = await loginResponse.json().catch(() => ({}));
      return {
        success: false,
        error: errorData.detail || 'Invalid email or password',
      };
    }

    const loginData: LoginResponse = await loginResponse.json();

    // Get user data
    const userResponse = await fetch(`${API_BASE_URL}/users/me`, {
      headers: {
        Authorization: `Bearer ${loginData.access_token}`,
      },
    });

    if (!userResponse.ok) {
      return {
        success: false,
        error: 'Failed to fetch user data',
      };
    }

    const userData: UserResponse = await userResponse.json();

    // Store token in localStorage for persistence
    localStorage.setItem(ACCESS_TOKEN_KEY, loginData.access_token);

    const session: Session = {
      user: {
        id: String(userData.id), // Convert number to string
        email: userData.email,
        name: userData.first_name && userData.last_name 
          ? `${userData.first_name} ${userData.last_name}`
          : userData.first_name || userData.email,
        first_name: userData.first_name,
        last_name: userData.last_name,
        is_active: userData.is_active,
        is_superuser: userData.is_superuser,
        is_verified: userData.is_verified,
      },
      access_token: loginData.access_token,
    };

    return {
      success: true,
      session,
    };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'An error occurred during sign in',
    };
  }
}

/**
 * Register a new user
 */
export async function registerUser(
  email: string,
  password: string,
  firstName?: string,
  lastName?: string
): Promise<AuthResult> {
  try {
    const registerResponse = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email,
        password,
        first_name: firstName,
        last_name: lastName,
      }),
    });

    if (!registerResponse.ok) {
      const errorData = await registerResponse.json().catch(() => ({}));
      return {
        success: false,
        error: errorData.detail || 'Registration failed',
      };
    }

    // After successful registration, log the user in
    return await signInWithCredentials(email, password);
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'An error occurred during registration',
    };
  }
}

/**
 * Sign out the current user
 */
export async function signOut(): Promise<{ success: boolean; error?: string }> {
  try {
    const token = localStorage.getItem(ACCESS_TOKEN_KEY);
    
    if (token) {
      // Call logout endpoint
      await fetch(`${API_BASE_URL}/auth/jwt/logout`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
    }

    // Clear token from localStorage
    localStorage.removeItem(ACCESS_TOKEN_KEY);

    return { success: true };
  } catch (error) {
    // Even if the API call fails, clear local storage
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'An error occurred during sign out',
    };
  }
}

/**
 * Get current user session from stored token
 */
export async function getCurrentSession(): Promise<Session | null> {
  try {
    const token = localStorage.getItem(ACCESS_TOKEN_KEY);
    
    if (!token) {
      return null;
    }

    // Verify token and get user data
    const userResponse = await fetch(`${API_BASE_URL}/users/me`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!userResponse.ok) {
      // Token is invalid, clear it
      localStorage.removeItem(ACCESS_TOKEN_KEY);
      return null;
    }

    const userData: UserResponse = await userResponse.json();

    const session: Session = {
      user: {
        id: String(userData.id), // Convert number to string
        email: userData.email,
        name: userData.first_name && userData.last_name 
          ? `${userData.first_name} ${userData.last_name}`
          : userData.first_name || userData.email,
        first_name: userData.first_name,
        last_name: userData.last_name,
        is_active: userData.is_active,
        is_superuser: userData.is_superuser,
        is_verified: userData.is_verified,
      },
      access_token: token,
    };

    return session;
  } catch {
    // If there's an error, clear the token
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    return null;
  }
}
