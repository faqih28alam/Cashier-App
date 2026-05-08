import Cookies from "js-cookie";

const TOKEN_KEY = "cashier_token";
const USER_KEY = "cashier_user";

export interface AuthUser {
  id: number;
  username: string;
  nama: string;
  role: "kasir" | "admin" | "owner";
  is_active: boolean;
}

export function saveAuth(token: string, user: AuthUser) {
  Cookies.set(TOKEN_KEY, token, { expires: 0.5 }); // 12 hours
  Cookies.set(USER_KEY, JSON.stringify(user), { expires: 0.5 });
}

export function getToken(): string | undefined {
  return Cookies.get(TOKEN_KEY);
}

export function getUser(): AuthUser | null {
  const raw = Cookies.get(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as AuthUser;
  } catch {
    return null;
  }
}

export function clearAuth() {
  Cookies.remove(TOKEN_KEY);
  Cookies.remove(USER_KEY);
}

export function isAuthenticated(): boolean {
  return !!getToken();
}
