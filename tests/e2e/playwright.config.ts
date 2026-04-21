import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./tests",
  fullyParallel: false,   // run serially — tests share a live DB
  retries: 0,
  workers: 1,
  reporter: "list",

  use: {
    baseURL: "http://localhost:5173",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
    trace: "retain-on-failure",
  },

  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],

  // Expects frontend (5173) and backend (8000) to already be running.
  // Start them with:
  //   cd backend && uvicorn app.main:app --reload
  //   cd frontend && npm run dev
});
