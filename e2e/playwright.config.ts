import { defineConfig, devices } from "@playwright/test";

/**
 * Base URL: the stack is exposed by nginx on port 80 in Docker (make up),
 * or directly on port 3000 in local dev (make dev-frontend).
 * Override with BASE_URL env var in CI.
 */
const BASE_URL = process.env.BASE_URL ?? "http://localhost";

export default defineConfig({
  testDir: "./tests",
  fullyParallel: false, // auth state is sequential by nature
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ["list"],
    ["html", { outputFolder: "playwright-report", open: "never" }],
    ["junit", { outputFile: "test-results/results.xml" }],
  ],
  use: {
    baseURL: BASE_URL,
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
  },
  projects: [
    // Setup project — creates a reusable authenticated session
    {
      name: "setup",
      testMatch: /global\.setup\.ts/,
    },
    // Main chromium suite — depends on setup
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
      dependencies: ["setup"],
    },
    // Mobile smoke
    {
      name: "mobile-chrome",
      use: { ...devices["Pixel 5"] },
      dependencies: ["setup"],
      testMatch: /smoke\.spec\.ts/,
    },
  ],
  outputDir: "test-results",
});
