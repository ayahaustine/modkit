/**
 * Refresh token cycle — covers:
 *   - POST /api/v1/auth/refresh issues a new access + refresh token pair
 *   - The new access token is a valid JWT shape (3 segments)
 *   - The old refresh token cannot be reused after rotation (replay attack)
 *   - Missing refresh token returns 401
 */
import { test, expect } from "./helpers/fixtures";
import { apiLogin, extractCookie } from "./helpers/api";

test.describe("Refresh token cycle", () => {
  test("refresh returns new access and refresh tokens", async ({
    testUser,
    page,
  }) => {
    const setCookies = await apiLogin(testUser);
    const oldRefresh = extractCookie(setCookies, "refresh_token");
    expect(oldRefresh).toBeDefined();

    const res = await page.request.post("/api/v1/auth/refresh", {
      headers: { Cookie: `refresh_token=${oldRefresh}` },
    });

    expect(res.status()).toBe(200);

    // New tokens should be present in Set-Cookie
    const newCookieHeaders = res.headers()["set-cookie"];
    expect(newCookieHeaders).toBeTruthy();
    const newCookies = newCookieHeaders
      .split(/,(?=[^ ])/)
      .map((h) => h.trim());

    const newAccess = extractCookie(newCookies, "access_token");
    const newRefresh = extractCookie(newCookies, "refresh_token");
    expect(newAccess).toBeDefined();
    expect(newRefresh).toBeDefined();

    // New access token must be a well-formed JWT (3 dot-separated segments)
    expect(newAccess!.split(".").length).toBe(3);
  });

  test("old refresh token is invalidated after rotation (replay attack)", async ({
    testUser,
    page,
  }) => {
    const setCookies = await apiLogin(testUser);
    const oldRefresh = extractCookie(setCookies, "refresh_token");
    expect(oldRefresh).toBeDefined();

    // First use — valid
    const firstRes = await page.request.post("/api/v1/auth/refresh", {
      headers: { Cookie: `refresh_token=${oldRefresh}` },
    });
    expect(firstRes.status()).toBe(200);

    // Second use of the same token — must be rejected
    const replayRes = await page.request.post("/api/v1/auth/refresh", {
      headers: { Cookie: `refresh_token=${oldRefresh}` },
    });
    expect(replayRes.status()).toBe(401);
  });

  test("refresh without cookie returns 401", async ({ page }) => {
    const res = await page.request.post("/api/v1/auth/refresh");
    expect(res.status()).toBe(401);
  });

  test("refresh with tampered token returns 401", async ({ page }) => {
    const res = await page.request.post("/api/v1/auth/refresh", {
      headers: { Cookie: "refresh_token=invalid.token.value" },
    });
    expect(res.status()).toBe(401);
  });

  test("refreshed token grants dashboard access", async ({
    testUser,
    browser,
  }) => {
    const setCookies = await apiLogin(testUser);
    const oldRefresh = extractCookie(setCookies, "refresh_token");

    // Rotate tokens
    const refreshRes = await fetch(
      `${process.env.API_URL ?? "http://localhost/api/v1"}/auth/refresh`,
      {
        method: "POST",
        headers: { Cookie: `refresh_token=${oldRefresh}` },
      },
    );
    expect(refreshRes.status).toBe(200);
    const newSetCookies = refreshRes.headers.getSetCookie();

    // Inject the NEW cookies into a fresh context and visit /dashboard
    const context = await browser.newContext();
    const cookies = newSetCookies.flatMap((header: string) => {
      const parts = header.split(";").map((p: string) => p.trim());
      const [name, ...valueParts] = parts[0].split("=");
      const value = valueParts.join("=");
      if (!name || !value) return [];
      return [
        {
          name,
          value,
          domain: "localhost",
          path: "/",
          httpOnly: parts.some((p: string) => p.toLowerCase() === "httponly"),
          secure: parts.some((p: string) => p.toLowerCase() === "secure"),
        },
      ];
    });
    await context.addCookies(cookies);
    const page = await context.newPage();

    await page.goto("/dashboard");
    await expect(page).toHaveURL(/\/dashboard/);
    await expect(page.getByRole("heading", { name: /dashboard/i })).toBeVisible();

    await context.close();
  });
});
