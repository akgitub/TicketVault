import axios, { AxiosError } from "axios";

export const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000",
  headers: { "Content-Type": "application/json" },
  timeout: 15000,
});

export function setAuthToken(token: string | null) {
  if (token) {
    api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common["Authorization"];
  }
}

// Normalize API errors globally
api.interceptors.response.use(
  (res) => res,
  (err: AxiosError<{ detail: string }>) => {
    const detail = err.response?.data?.detail;
    const status = err.response?.status;
    if (status === 401) {
      console.warn("[api] 401 — token may be expired");
    }
    return Promise.reject(new Error(detail ?? err.message ?? "Unknown error"));
  }
);
