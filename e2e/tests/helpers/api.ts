/**
 * Helpers for interacting with the backend API directly from tests.
 * Used to set up / tear down test users without going through the UI.
 */

const API = process.env.API_URL ?? "http://localhost/api/v1";

export interface UserCredentials {
  email: string;
  password: string;
}

/** Create a test user via the registration API and return their credentials. */
export async function createTestUser(
  credentials: UserCredentials,
): Promise<void> {
  const res = await fetch(`${API}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email: credentials.email,
      password: credentials.password,
    }),
  });
  // 409 means the user already exists from a previous run — that is fine.
  if (!res.ok && res.status !== 409) {
    const body = await res.text();
    throw new Error(
      `Failed to create test user (${res.status}): ${body}`,
    );
  }
}

/** Log in and return the raw Set-Cookie headers (access + refresh tokens). */
export async function apiLogin(
  credentials: UserCredentials,
): Promise<string[]> {
  const res = await fetch(`${API}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(credentials),
  });
  if (!res.ok) {
    throw new Error(`Login failed (${res.status})`);
  }
  return res.headers.getSetCookie();
}

/** Extract a named cookie value from raw Set-Cookie header strings. */
export function extractCookie(
  setCookieHeaders: string[],
  name: string,
): string | undefined {
  for (const header of setCookieHeaders) {
    const parts = header.split(";").map((p) => p.trim());
    const pair = parts[0];
    const [cookieName, ...valueParts] = pair.split("=");
    if (cookieName.trim() === name) {
      return valueParts.join("=");
    }
  }
  return undefined;
}
