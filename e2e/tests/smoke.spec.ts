/**
 * Smoke tests — a minimal subset that runs on every browser project
 * (including mobile-chrome) to verify the app loads and core routes respond.
 */
import { test, expect } from "./helpers/fixtures";

test.describe("Smoke", () => {
  test("home page loads", async ({ page }) => {
    await page.goto("/");
    await expect(page).toHaveTitle(/modkit/i);
    await expect(page.getByRole("link", { name: /sign in/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /register/i })).toBeVisible();
  });

  test("login page renders the form", async ({ page }) => {
    await page.goto("/login");
    await expect(page.getByLabel("Email")).toBeVisible();
    await expect(page.getByLabel("Password")).toBeVisible();
    await expect(page.getByRole("button", { name: /sign in/i })).toBeVisible();
  });

  test("register page renders the form", async ({ page }) => {
    await page.goto("/register");
    await expect(page.getByLabel(/email/i)).toBeVisible();
  });

  test("health endpoint responds", async ({ page }) => {
    const res = await page.request.get("/api/v1/health");
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body.status).toBe("ok");
  });
});
