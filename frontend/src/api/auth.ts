import client from "./client";
import type { TokenResponse, User } from "../types";

export async function register(
  email: string,
  password: string,
  fullName?: string
): Promise<TokenResponse> {
  const { data } = await client.post<TokenResponse>("/auth/register", {
    email,
    password,
    full_name: fullName,
  });
  return data;
}

export async function login(email: string, password: string): Promise<TokenResponse> {
  const { data } = await client.post<TokenResponse>("/auth/login", { email, password });
  return data;
}

export async function getGoogleAuthUrl(): Promise<string> {
  const { data } = await client.get<{ auth_url: string }>("/auth/google/login");
  return data.auth_url;
}

export async function getCurrentUser(): Promise<User> {
  const { data } = await client.get<User>("/users/me");
  return data;
}

export function saveToken(token: string): void {
  localStorage.setItem("access_token", token);
}

export function clearToken(): void {
  localStorage.removeItem("access_token");
}

export function getToken(): string | null {
  return localStorage.getItem("access_token");
}
