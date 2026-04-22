import { test, expect, type Page, type Browser } from "@playwright/test";

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
 */

// ── Auth helpers ──────────────────────────────────────────────────────────────

/**
 * Register a fresh user and land on /dashboard.
 * Uses Date.now() inside the function — safe to call from any test since
 * Playwright may re-evaluate module-level code between tests.
 */
export async function registerAndLogin(page: Page, email: string, password: string, fullName?: string): Promise<void> {
  await page.goto("/register");
  if (fullName) await page.getByPlaceholder("Full name (optional)").fill(fullName);
  await page.getByPlaceholder("Email").fill(email);
  await page.getByPlaceholder("Password").fill(password);
  await page.getByRole("button", { name: "Create account" }).click();
  // waitForURL (not expect().toHaveURL) so we get a clear timeout message
  await page.waitForURL("**/dashboard", { timeout: 10000 });
}

/**
 * Log in an existing user and land on /dashboard.
 */
export async function loginAs(page: Page, email: string, password: string): Promise<void> {
  await page.goto("/login");
  await page.getByPlaceholder("Email").fill(email);
  await page.getByPlaceholder("Password").fill(password);
  await page.getByRole("button", { name: "Sign in" }).click();
  await page.waitForURL("**/dashboard", { timeout: 10000 });
}

/**
 * Create two isolated browser contexts (separate localStorage) — required
 * when a test needs two simultaneously-logged-in users, e.g. to test SSE
 * notifications sent from one user to another.
 *
 * Usage:
 *   test("...", async ({ browser }) => {
 *     const { ownerPage, memberPage, cleanup } = await twoUserContexts(browser);
 *     try { ... } finally { await cleanup(); }
 *   });
 *
 * NOTE: pages in separate contexts use absolute URLs — relative paths like
 * "/register" only work for the default fixture `page`. Use the full URL
 * "http://localhost:5173/register" or set baseURL on the context:
 *   const ctx = await browser.newContext({ baseURL: "http://localhost:5173" });
 */
export async function twoUserContexts(browser: Browser) {
  const ctx1 = await browser.newContext({ baseURL: "http://localhost:5173" });
  const ctx2 = await browser.newContext({ baseURL: "http://localhost:5173" });
  return {
    ownerPage: await ctx1.newPage(),
    memberPage: await ctx2.newPage(),
    cleanup: async () => { await ctx1.close(); await ctx2.close(); },
  };
}

// ── SSE timing note ───────────────────────────────────────────────────────────
//
// useSSEEvent() registers its handler inside a React useEffect, which fires
// *after* the component renders. When a test navigates to a page and then
// immediately triggers a server-side event, the handler may not be registered
// yet. Wait for a visible element that confirms the page is fully mounted
// (e.g. `await expect(page.getByText("To Do")).toBeVisible()`) before firing
// the event that should trigger the notification.

// ── Placeholder test ──────────────────────────────────────────────────────────

test("placeholder — replace with your feature tests", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveURL(/login|dashboard/);
});
