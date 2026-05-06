/**
 * Dashboard access — covers:
 *   - Authenticated user can view the dashboard
 *   - Displays the correct email
 *   - Unauthenticated user is redirected to /login
 *   - Sign-out button is visible and functional
 */
import { test, expect } from "./helpers/fixtures";

test.describe("Dashboard access", () => {
  test("authenticated user can access /dashboard", async ({
    authedPage,
    testUser,
  }) => {
    await authedPage.goto("/dashboard");

    await expect(authedPage).toHaveURL(/\/dashboard/);
    await expect(
      authedPage.getByRole("heading", { name: /dashboard/i }),
    ).toBeVisible();
    await expect(authedPage.locator("text=" + testUser.email)).toBeVisible();
  });

  test("dashboard shows the signed-in user's email", async ({
    authedPage,
    testUser,
  }) => {
    await authedPage.goto("/dashboard");
    await expect(authedPage.locator(`text=${testUser.email}`)).toBeVisible();
  });

  test("sign-out button is present on dashboard", async ({ authedPage }) => {
    await authedPage.goto("/dashboard");
    await expect(
      authedPage.getByRole("button", { name: /sign out/i }),
    ).toBeVisible();
  });

  test("unauthenticated access to /dashboard redirects to /login", async ({
    page,
  }) => {
    await page.goto("/dashboard");
    await expect(page).toHaveURL(/\/login(\?|$)/);
  });

  test("redirect preserves ?next= param pointing to /dashboard", async ({
    page,
  }) => {
    await page.goto("/dashboard");
    // After redirect the login URL should carry the next param
    expect(page.url()).toMatch(/next=%2Fdashboard|next=\/dashboard/);
  });
});
