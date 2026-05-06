/**
 * Global setup — runs once before all test suites.
 * Creates the shared e2e test user so individual tests do not race on
 * user creation.
 */
import { test as setup } from "@playwright/test";
import { createTestUser } from "./helpers/api";

const TEST_USER = {
  email: process.env.TEST_USER_EMAIL ?? "e2e-user@modkit.test",
  password: process.env.TEST_USER_PASSWORD ?? "e2epassword1",
};

setup("create e2e test user", async () => {
  await createTestUser(TEST_USER);
});
