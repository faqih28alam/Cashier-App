import { getToken, clearAuth } from "./auth";

const getBaseUrl = () => {
  if (typeof window === "undefined") return process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  return `http://${window.location.hostname}:8000`;
};

type RequestOptions = {
  method?: string;
  body?: unknown;
  params?: Record<string, string | number | boolean | undefined>;
};

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = "GET", body, params } = options;

  const url = new URL(`${getBaseUrl()}${path}`);
  if (params) {
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined) url.searchParams.set(k, String(v));
    });
  }

  const token = getToken();
  const headers: HeadersInit = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(url.toString(), {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    // Only treat 401 as "session expired" when we actually had a token.
    // Without a token it's a failed login — let the caller handle it.
    if (res.status === 401 && token) {
      clearAuth();
      window.location.href = "/login";
    }
    throw new Error(err.detail ?? "Request failed");
  }

  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export const api = {
  get: <T>(path: string, params?: RequestOptions["params"]) =>
    request<T>(path, { params }),
  post: <T>(path: string, body: unknown) =>
    request<T>(path, { method: "POST", body }),
  put: <T>(path: string, body: unknown) =>
    request<T>(path, { method: "PUT", body }),
  delete: <T>(path: string) =>
    request<T>(path, { method: "DELETE" }),
};
