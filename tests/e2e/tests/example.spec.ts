import { test, expect } from "@playwright/test";

/**
 * Placeholder for feature-specific tests.
 *
 * When building a new feature, add a new spec file here following the
 * pattern in auth.spec.ts:
 *
 *   tests/
 *     auth.spec.ts        ← baseline (do not modify)
 *     tasks.spec.ts       ← your feature tests
 *     projects.spec.ts    ← another feature
 *
 * Helpers for logging in programmatically (faster than going through the UI):
 *
 *   async function loginAs(page, email, password) {
 *     await page.goto("/login");
 *     await page.getByPlaceholder("Email").fill(email);
 *     await page.getByPlaceholder("Password").fill(password);
 *     await page.getByRole("button", { name: "Sign in" }).click();
 *     await page.waitForURL("/dashboard");
 *   }
 */

test("placeholder — replace with your feature tests", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveURL(/login|dashboard/);
});
