import { test, expect } from "@playwright/test";

// Unique email per test run so tests don't conflict with existing DB rows
const email = `test_${Date.now()}@example.com`;
const password = "Password123!";
const fullName = "Test User";

test.describe("Auth — register", () => {
  test("registers a new user and lands on dashboard", async ({ page }) => {
    await page.goto("/register");

    await page.getByPlaceholder("Full name (optional)").fill(fullName);
    await page.getByPlaceholder("Email").fill(email);
    await page.getByPlaceholder("Password").fill(password);
    await page.getByRole("button", { name: "Create account" }).click();

    await expect(page).toHaveURL("/dashboard");
    // Dashboard should show the user's email
    await expect(page.getByText(email)).toBeVisible();
  });
});

test.describe("Auth — login", () => {
  test("logs in with registered credentials and lands on dashboard", async ({ page }) => {
    await page.goto("/login");

    await page.getByPlaceholder("Email").fill(email);
    await page.getByPlaceholder("Password").fill(password);
    await page.getByRole("button", { name: "Sign in" }).click();

    await expect(page).toHaveURL("/dashboard");
    await expect(page.getByText(email)).toBeVisible();
  });

  test("shows error on wrong password", async ({ page }) => {
    await page.goto("/login");

    await page.getByPlaceholder("Email").fill(email);
    await page.getByPlaceholder("Password").fill("wrongpassword");
    await page.getByRole("button", { name: "Sign in" }).click();

    await expect(page.getByText("Invalid email or password")).toBeVisible();
    await expect(page).toHaveURL("/login");
  });
});

test.describe("Auth — protected routes", () => {
  test("redirects unauthenticated user from /dashboard to /login", async ({ page }) => {
    // Clear any stored token
    await page.goto("/login");
    await page.evaluate(() => localStorage.removeItem("access_token"));

    await page.goto("/dashboard");
    await expect(page).toHaveURL("/login");
  });
});

test.describe("Auth — logout", () => {
  test("logs out and redirects to login", async ({ page }) => {
    // Log in first
    await page.goto("/login");
    await page.getByPlaceholder("Email").fill(email);
    await page.getByPlaceholder("Password").fill(password);
    await page.getByRole("button", { name: "Sign in" }).click();
    await expect(page).toHaveURL("/dashboard");

    // Log out
    await page.getByRole("button", { name: "Sign out" }).click();
    await expect(page).toHaveURL("/login");

    // Confirm token is gone — protected route redirects again
    await page.goto("/dashboard");
    await expect(page).toHaveURL("/login");
  });
});
