/**
 * Login flow — covers:
 *   - Successful login redirects to /dashboard
 *   - Access token cookie is set
 *   - Wrong password shows error
 *   - Unauthenticated /dashboard redirects to /login
 *   - Login with ?next= param honours the redirect
 */
import { test, expect } from "./helpers/fixtures";

test.describe("Login flow", () => {
  test("successful login redirects to dashboard", async ({
    loginPage,
    testUser,
    page,
  }) => {
    await loginPage.login(testUser.email, testUser.password);

    await expect(page).toHaveURL(/\/dashboard/);
    await expect(page.getByRole("heading", { name: /dashboard/i })).toBeVisible();
  });

  test("access_token cookie is set after login", async ({
    loginPage,
    testUser,
    context,
  }) => {
    await loginPage.login(testUser.email, testUser.password);

    const cookies = await context.cookies();
    const accessToken = cookies.find((c) => c.name === "access_token");
    expect(accessToken).toBeDefined();
    expect(accessToken!.httpOnly).toBe(true);
  });

  test("refresh_token cookie is set after login", async ({
    loginPage,
    testUser,
    context,
  }) => {
    await loginPage.login(testUser.email, testUser.password);

    const cookies = await context.cookies();
    const refreshToken = cookies.find((c) => c.name === "refresh_token");
    expect(refreshToken).toBeDefined();
    expect(refreshToken!.httpOnly).toBe(true);
  });

  test("wrong password shows error message", async ({
    loginPage,
    testUser,
    page,
  }) => {
    await loginPage.goto();
    await loginPage.fillEmail(testUser.email);
    await loginPage.fillPassword("wrongpassword!");
    await loginPage.submit();

    await expect(loginPage.errorMessage()).toBeVisible();
    await expect(page).toHaveURL(/\/login/);
  });

  test("unknown email shows error message", async ({ loginPage, page }) => {
    await loginPage.goto();
    await loginPage.fillEmail("nobody@modkit.test");
    await loginPage.fillPassword("somepassword1");
    await loginPage.submit();

    await expect(loginPage.errorMessage()).toBeVisible();
    await expect(page).toHaveURL(/\/login/);
  });

  test("unauthenticated request to /dashboard redirects to /login", async ({
    page,
  }) => {
    await page.goto("/dashboard");
    await expect(page).toHaveURL(/\/login/);
  });

  test("login with ?next= redirects to the target route", async ({
    loginPage,
    testUser,
    page,
  }) => {
    await page.goto("/login?next=/dashboard");
    await loginPage.fillEmail(testUser.email);
    await loginPage.fillPassword(testUser.password);
    await loginPage.submit();

    await expect(page).toHaveURL(/\/dashboard/);
  });

  test("already authenticated user visiting /login is redirected to dashboard", async ({
    authedPage,
  }) => {
    await authedPage.goto("/login");
    await expect(authedPage).toHaveURL(/\/dashboard/);
  });
});
