import apiFetch from "@/lib/api";
import type { User } from "@/lib/types";

export interface LoginPayload {
  email: string;
  password: string;
}

export interface RegisterPayload {
  email: string;
  password: string;
  full_name?: string;
}

export const authApi = {
  register: (data: RegisterPayload) =>
    apiFetch<User>("/auth/register", { method: "POST", json: data }),

  login: (data: LoginPayload) =>
    apiFetch<{ message: string }>("/auth/login", { method: "POST", json: data }),

  logout: () =>
    apiFetch<void>("/auth/logout", { method: "POST" }),

  refresh: () =>
    apiFetch<{ message: string }>("/auth/refresh", { method: "POST" }),

  me: () =>
    apiFetch<User>("/auth/me"),
};
