import axios from "axios";
import { ACCESS_TOKEN_KEY } from "../features/auth/constant";

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
  headers: {
    "Content-Type": "application/json",
    // Possibly add auth token header if you have one
  },
});

// Add a request interceptor to include access token if available
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem(ACCESS_TOKEN_KEY);
  if (token) {
    config.headers = config.headers || {};
    config.headers["Authorization"] = `Bearer ${token}`;
  }
  return config;
});

// Add a response interceptor to handle 401 errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear the access token from localStorage
      localStorage.removeItem(ACCESS_TOKEN_KEY);
      // Redirect to login page
      window.location.href = "/sign-in";
    }
    return Promise.reject(error);
  }
);

export default apiClient;