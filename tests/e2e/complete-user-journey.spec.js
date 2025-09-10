import { test, expect } from "@playwright/test";

const API_BASE = "http://localhost:8000";
const FRONTEND_URL = "http://localhost:5173";

test.describe("RazorFlow AI - Complete User Journey", () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto(FRONTEND_URL);

    // Wait for the application to load
    await page.waitForLoadState("networkidle");
  });

  test("should load the application and display bot selection", async ({
    page,
  }) => {
    // Check if the page title is correct
    await expect(page).toHaveTitle(/RazorFlow AI/);

    // Check if the main heading is visible
    await expect(page.locator("h1")).toContainText("RazorFlow AI");

    // Check if bot selection buttons are present
    await expect(page.locator('button:has-text("Finance Bot")')).toBeVisible();
    await expect(page.locator('button:has-text("Sales Bot")')).toBeVisible();
    await expect(
      page.locator('button:has-text("Scheduler Bot")')
    ).toBeVisible();
  });

  test("should select Finance Bot and display dashboard", async ({ page }) => {
    // Click on Finance Bot
    await page.click('button:has-text("Finance Bot")');

    // Wait for data to load
    await page.waitForSelector('[data-testid="dashboard"]', { timeout: 10000 });

    // Check if Finance dashboard is displayed
    await expect(page.locator("text=Finance Dashboard")).toBeVisible();

    // Check for key metrics
    await expect(page.locator("text=$125,000")).toBeVisible(); // Revenue
    await expect(page.locator("text=$78,000")).toBeVisible(); // Expenses
    await expect(page.locator("text=$47,000")).toBeVisible(); // Profit
    await expect(page.locator("text=12%")).toBeVisible(); // Growth

    // Check for insights section
    await expect(page.locator("text=Key Insights")).toBeVisible();
    await expect(page.locator("text=Recommendations")).toBeVisible();
  });

  test("should select Sales Bot and display sales metrics", async ({
    page,
  }) => {
    // Click on Sales Bot
    await page.click('button:has-text("Sales Bot")');

    // Wait for data to load
    await page.waitForSelector('[data-testid="dashboard"]', { timeout: 10000 });

    // Check if Sales dashboard is displayed
    await expect(page.locator("text=Sales Dashboard")).toBeVisible();

    // Check for sales metrics
    await expect(page.locator("text=234")).toBeVisible(); // Leads
    await expect(page.locator("text=56")).toBeVisible(); // Conversions
    await expect(page.locator("text=24%")).toBeVisible(); // Conversion Rate
    await expect(page.locator("text=$2.1M")).toBeVisible(); // Pipeline Value
  });

  test("should select Scheduler Bot and display scheduling data", async ({
    page,
  }) => {
    // Click on Scheduler Bot
    await page.click('button:has-text("Scheduler Bot")');

    // Wait for data to load
    await page.waitForSelector('[data-testid="dashboard"]', { timeout: 10000 });

    // Check if Scheduler dashboard is displayed
    await expect(page.locator("text=Scheduler Dashboard")).toBeVisible();

    // Check for scheduling metrics
    await expect(page.locator("text=8")).toBeVisible(); // Today's Meetings
    await expect(page.locator("text=23")).toBeVisible(); // This Week
    await expect(page.locator("text=89%")).toBeVisible(); // Utilization
  });

  test("should switch between different bots seamlessly", async ({ page }) => {
    // Start with Finance Bot
    await page.click('button:has-text("Finance Bot")');
    await page.waitForSelector("text=Finance Dashboard", { timeout: 10000 });

    // Switch to Sales Bot
    await page.click('button:has-text("Sales Bot")');
    await page.waitForSelector("text=Sales Dashboard", { timeout: 10000 });

    // Switch to Scheduler Bot
    await page.click('button:has-text("Scheduler Bot")');
    await page.waitForSelector("text=Scheduler Dashboard", { timeout: 10000 });

    // Switch back to Finance Bot
    await page.click('button:has-text("Finance Bot")');
    await page.waitForSelector("text=Finance Dashboard", { timeout: 10000 });
  });

  test("should open and use chat interface", async ({ page }) => {
    // Select a bot first
    await page.click('button:has-text("Finance Bot")');
    await page.waitForSelector('[data-testid="dashboard"]', { timeout: 10000 });

    // Look for chat interface
    await expect(page.locator('[data-testid="chat"]')).toBeVisible();

    // Check for message input
    const messageInput = page.locator('textarea[placeholder*="Ask"]');
    await expect(messageInput).toBeVisible();

    // Type a message
    await messageInput.fill("What is my current revenue?");

    // Click send button
    await page.click('button[type="submit"]');

    // Wait for response
    await page.waitForSelector(".message", { timeout: 10000 });

    // Check if message was sent
    await expect(
      page.locator("text=What is my current revenue?")
    ).toBeVisible();

    // Check for bot response
    await expect(page.locator(".message").last()).toBeVisible();
  });

  test("should handle API errors gracefully", async ({ page }) => {
    // Mock API failure
    await page.route(`${API_BASE}/api/finance`, (route) => {
      route.fulfill({
        status: 500,
        contentType: "application/json",
        body: JSON.stringify({ error: "Internal Server Error" }),
      });
    });

    // Try to select Finance Bot
    await page.click('button:has-text("Finance Bot")');

    // Should show error message
    await expect(page.locator("text=Error loading data")).toBeVisible();
  });

  test("should display loading states", async ({ page }) => {
    // Mock slow API response
    await page.route(`${API_BASE}/api/finance`, (route) => {
      setTimeout(() => {
        route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            revenue: 125000,
            expenses: 78000,
            profit: 47000,
            growth: 12,
          }),
        });
      }, 2000);
    });

    // Click Finance Bot
    await page.click('button:has-text("Finance Bot")');

    // Should show loading indicator
    await expect(page.locator("text=Loading")).toBeVisible();

    // Wait for data to load
    await page.waitForSelector("text=Finance Dashboard", { timeout: 15000 });
  });

  test("should test performance monitoring component", async ({ page }) => {
    // Wait for page to load
    await page.waitForLoadState("networkidle");

    // Look for Performance Monitor
    await expect(page.locator("text=Performance Monitor")).toBeVisible();

    // Check initial metrics
    await expect(page.locator("text=API Status")).toBeVisible();
    await expect(page.locator("text=Response Time")).toBeVisible();

    // Start monitoring
    await page.click('button:has-text("Start Monitor")');

    // Wait a moment for monitoring to start
    await page.waitForTimeout(2000);

    // Should show monitoring active
    await expect(page.locator("text=Monitoring Active")).toBeVisible();

    // Stop monitoring
    await page.click('button:has-text("Stop")');

    // Should show monitoring stopped
    await expect(page.locator("text=Monitoring Stopped")).toBeVisible();
  });

  test("should perform load testing", async ({ page }) => {
    // Wait for page to load
    await page.waitForLoadState("networkidle");

    // Click Load Test button
    await page.click('button:has-text("Load Test")');

    // Wait for load test to complete
    await page.waitForTimeout(5000);

    // Check that request count increased
    const requestCount = await page
      .locator("text=Requests")
      .locator("..")
      .locator("p")
      .nth(1)
      .textContent();
    expect(parseInt(requestCount)).toBeGreaterThan(0);
  });

  test("should test chat functionality with all bot types", async ({
    page,
  }) => {
    const botTypes = ["Finance Bot", "Sales Bot", "Scheduler Bot"];
    const testMessages = [
      "What is my revenue?",
      "Show me sales data",
      "Schedule a meeting",
    ];

    for (let i = 0; i < botTypes.length; i++) {
      // Select bot
      await page.click(`button:has-text("${botTypes[i]}")`);
      await page.waitForSelector('[data-testid="dashboard"]', {
        timeout: 10000,
      });

      // Send message
      const messageInput = page.locator('textarea[placeholder*="Ask"]');
      await messageInput.fill(testMessages[i]);
      await page.click('button[type="submit"]');

      // Wait for response
      await page.waitForSelector(".message", { timeout: 10000 });

      // Verify message was sent
      await expect(page.locator(`text=${testMessages[i]}`)).toBeVisible();

      // Clear chat for next test
      await page.reload();
      await page.waitForLoadState("networkidle");
    }
  });

  test("should test responsive design on mobile viewport", async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });

    // Reload page
    await page.reload();
    await page.waitForLoadState("networkidle");

    // Check if layout adapts to mobile
    await expect(page.locator("h1")).toBeVisible();
    await expect(page.locator('button:has-text("Finance Bot")')).toBeVisible();

    // Test bot selection on mobile
    await page.click('button:has-text("Finance Bot")');
    await page.waitForSelector('[data-testid="dashboard"]', { timeout: 10000 });

    // Check if dashboard is responsive
    await expect(page.locator("text=Finance Dashboard")).toBeVisible();
  });

  test("should validate API health before running tests", async ({ page }) => {
    // Make direct API call to health endpoint
    const response = await page.request.get(`${API_BASE}/health`);
    expect(response.status()).toBe(200);

    const healthData = await response.json();
    expect(healthData.status).toBe("healthy");
  });

  test("should test keyboard navigation", async ({ page }) => {
    // Use Tab to navigate through bot selection buttons
    await page.keyboard.press("Tab");
    await page.keyboard.press("Tab");
    await page.keyboard.press("Enter"); // Should select first bot

    // Wait for dashboard to load
    await page.waitForSelector('[data-testid="dashboard"]', { timeout: 10000 });

    // Navigate to chat input using Tab
    await page.keyboard.press("Tab");
    const focused = await page.evaluate(() => document.activeElement.tagName);
    expect(["TEXTAREA", "INPUT"]).toContain(focused);
  });
});

test.describe("Performance Tests", () => {
  test("should measure page load performance", async ({ page }) => {
    const startTime = Date.now();

    await page.goto(FRONTEND_URL);
    await page.waitForLoadState("networkidle");

    const loadTime = Date.now() - startTime;

    // Page should load within 5 seconds
    expect(loadTime).toBeLessThan(5000);

    console.log(`Page load time: ${loadTime}ms`);
  });

  test("should measure API response times", async ({ page }) => {
    await page.goto(FRONTEND_URL);

    const apiStartTime = Date.now();

    // Make API request
    const response = await page.request.get(`${API_BASE}/api/finance`);

    const apiResponseTime = Date.now() - apiStartTime;

    // API should respond within 1 second
    expect(apiResponseTime).toBeLessThan(1000);
    expect(response.status()).toBe(200);

    console.log(`API response time: ${apiResponseTime}ms`);
  });

  test("should handle concurrent users simulation", async ({ browser }) => {
    const contexts = [];
    const pages = [];

    // Create 5 concurrent users
    for (let i = 0; i < 5; i++) {
      const context = await browser.newContext();
      const page = await context.newPage();
      contexts.push(context);
      pages.push(page);
    }

    // Navigate all users simultaneously
    const navigationPromises = pages.map((page) =>
      page.goto(FRONTEND_URL).then(() => page.waitForLoadState("networkidle"))
    );

    await Promise.all(navigationPromises);

    // All users select different bots
    const botSelections = [
      "Finance Bot",
      "Sales Bot",
      "Scheduler Bot",
      "Finance Bot",
      "Sales Bot",
    ];

    const botSelectionPromises = pages.map((page, index) =>
      page
        .click(`button:has-text("${botSelections[index]}")`)
        .then(() =>
          page.waitForSelector('[data-testid="dashboard"]', { timeout: 10000 })
        )
    );

    await Promise.all(botSelectionPromises);

    // Cleanup
    for (const context of contexts) {
      await context.close();
    }
  });
});
