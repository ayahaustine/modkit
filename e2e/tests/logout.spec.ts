/**
 * Logout flow — covers:
 *   - Sign-out button clears cookies and redirects to /login
 *   - After logout, /dashboard redirects to /login
 *   - After logout, browser cannot reuse the old refresh token
 */
import { test, expect } from "./helpers/fixtures";
import { apiLogin, extractCookie } from "./helpers/api";

test.describe("Logout flow", () => {
  test("sign-out clears cookies and redirects to /login", async ({
    authedPage,
    context,
  }) => {
    await authedPage.goto("/dashboard");
    await expect(authedPage.getByRole("heading", { name: /dashboard/i })).toBeVisible();

    await authedPage.getByRole("button", { name: /sign out/i }).click();

    await expect(authedPage).toHaveURL(/\/login/);

    const cookies = await context.cookies();
    const accessToken = cookies.find((c) => c.name === "access_token");
    const refreshToken = cookies.find((c) => c.name === "refresh_token");
    // Cookies should be gone (cleared by the server via Max-Age=0)
    expect(accessToken).toBeUndefined();
    expect(refreshToken).toBeUndefined();
  });

  test("after logout /dashboard is inaccessible", async ({
    authedPage,
    context,
  }) => {
    await authedPage.goto("/dashboard");
    await authedPage.getByRole("button", { name: /sign out/i }).click();
    await expect(authedPage).toHaveURL(/\/login/);

    // Navigate to dashboard on the same context — cookies are gone
    await authedPage.goto("/dashboard");
    await expect(authedPage).toHaveURL(/\/login/);
  });

  test("old refresh token is invalidated after logout", async ({
    testUser,
    page,
  }) => {
    // Step 1: log in via API to capture the refresh token value
    const setCookies = await apiLogin(testUser);
    const refreshTokenValue = extractCookie(setCookies, "refresh_token");
    expect(refreshTokenValue).toBeDefined();

    // Step 2: inject cookies into browser and log out via UI
    await page.context().addCookies(
      setCookies.flatMap((header) => {
        const parts = header.split(";").map((p) => p.trim());
        const [name, ...valueParts] = parts[0].split("=");
        const value = valueParts.join("=");
        if (!name || !value) return [];
        return [
          {
            name,
            value,
            domain: "localhost",
            path: "/",
            httpOnly: parts.some((p) => p.toLowerCase() === "httponly"),
            secure: parts.some((p) => p.toLowerCase() === "secure"),
          },
        ];
      }),
    );
    await page.goto("/dashboard");
    await page.getByRole("button", { name: /sign out/i }).click();
    await expect(page).toHaveURL(/\/login/);

    // Step 3: try to use the old refresh token directly against the API
    const refreshRes = await page.request.post("/api/v1/auth/refresh", {
      headers: { Cookie: `refresh_token=${refreshTokenValue}` },
    });
    expect(refreshRes.status()).toBe(401);
  });
});
