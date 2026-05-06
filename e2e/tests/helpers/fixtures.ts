import { test as base, type Page } from "@playwright/test";
import { createTestUser, apiLogin, type UserCredentials } from "./api";

export { expect } from "@playwright/test";

/** Page-object for the Login page. */
export class LoginPage {
  constructor(private page: Page) {}

  async goto() {
    await this.page.goto("/login");
  }

  async fillEmail(email: string) {
    await this.page.getByLabel("Email").fill(email);
  }

  async fillPassword(password: string) {
    await this.page.getByLabel("Password").fill(password);
  }

  async submit() {
    await this.page.getByRole("button", { name: /sign in/i }).click();
  }

  async login(email: string, password: string) {
    await this.goto();
    await this.fillEmail(email);
    await this.fillPassword(password);
    await this.submit();
  }

  errorMessage() {
    return this.page.locator("p.text-red-600");
  }
}

/** Page-object for the Dashboard page. */
export class DashboardPage {
  constructor(private page: Page) {}

  async goto() {
    await this.page.goto("/dashboard");
  }

  signedInAs() {
    return this.page.locator("span.font-medium");
  }

  signOutButton() {
    return this.page.getByRole("button", { name: /sign out/i });
  }

  async logout() {
    await this.signOutButton().click();
  }
}

/** Test-scoped fixture type extensions. */
interface Fixtures {
  loginPage: LoginPage;
  dashboardPage: DashboardPage;
  testUser: UserCredentials;
  /** Authenticated page — cookies injected directly without UI login. */
  authedPage: Page;
}

const TEST_USER: UserCredentials = {
  email: process.env.TEST_USER_EMAIL ?? "e2e-user@modkit.test",
  password: process.env.TEST_USER_PASSWORD ?? "e2epassword1",
};

export const test = base.extend<Fixtures>({
  testUser: async ({}, use) => {
    await createTestUser(TEST_USER);
    await use(TEST_USER);
  },

  loginPage: async ({ page }, use) => {
    await use(new LoginPage(page));
  },

  dashboardPage: async ({ page }, use) => {
    await use(new DashboardPage(page));
  },

  /**
   * An authenticated browser context — injects cookies via the API so we
   * skip the UI login flow in tests that only care about post-auth behaviour.
   */
  authedPage: async ({ browser, testUser }, use) => {
    const setCookies = await apiLogin(testUser);
    const context = await browser.newContext();

    const cookies = setCookies.flatMap((header) => {
      const parts = header.split(";").map((p) => p.trim());
      const [name, ...valueParts] = parts[0].split("=");
      const value = valueParts.join("=");
      const domain = "localhost";
      const path = "/";
      const httpOnly = parts.some(
        (p) => p.toLowerCase() === "httponly",
      );
      const secure = parts.some(
        (p) => p.toLowerCase() === "secure",
      );
      if (!name || !value) return [];
      return [{ name, value, domain, path, httpOnly, secure }];
    });

    await context.addCookies(cookies);
    const page = await context.newPage();
    await use(page);
    await context.close();
  },
});
