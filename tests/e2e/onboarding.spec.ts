import { test, expect } from '@playwright/test';

test.describe('Onboarding Experience', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the onboarding chat
    await page.goto('http://localhost:3000/docs/data/onboarding-neuro-chat.html');

    // Wait for Alpine.js to load
    await page.waitForFunction(() => window.Alpine !== undefined);
  });

  test('completes full onboarding journey', async ({ page }) => {
    // Wait for chat to initialize
    await page.waitForSelector('[x-data="neuroChatbot"]', { timeout: 5000 });

    // Verify WebSocket connection status element exists
    const wsStatus = await page.waitForSelector('[class*="ws-status"]', { timeout: 5000 });
    expect(wsStatus).toBeTruthy();

    // Verify welcome messages
    const messages = await page.$$('.chat-message');
    expect(messages.length).toBeGreaterThan(0);

    // Start onboarding
    const startButton = await page.getByText('Начать');
    await startButton.click();

    // Complete cognitive assessment
    await page.waitForSelector('text=когнитивные способности', { timeout: 5000 });

    // Simulate cognitive test
    for (let i = 0; i < 10; i++) {
      await page.click('.test-target');
      await page.waitForTimeout(250);
    }

    // Verify cognitive results
    await page.waitForSelector('.chat-message.progress', { timeout: 5000 });
    const cognitiveLoad = await page.$('.cognitive-load');
    expect(cognitiveLoad).toBeTruthy();

    // Continue to physical assessment
    await page.click('text=Продолжить');

    // Complete physical assessment
    await page.waitForSelector('text=физическую форму', { timeout: 5000 });

    // Simulate physical exercises
    for (let i = 0; i < 5; i++) {
      await page.click('.exercise-complete');
      await page.waitForTimeout(500);
    }

    // Verify physical results
    const physicalLoad = await page.$('.physical-load');
    expect(physicalLoad).toBeTruthy();

    // Generate personalized plan
    await page.click('text=Создать план');

    // Verify plan generation
    await page.waitForSelector('text=ваш персональный план', { timeout: 5000 });

    // Check progress persistence
    await page.reload();
    await page.waitForSelector('[x-data="neuroChatbot"]', { timeout: 5000 });

    const progressHistory = await page.evaluate(() => localStorage.getItem('progressHistory'));
    expect(progressHistory).toBeTruthy();
  });

  test('handles offline mode gracefully', async ({ page, context }) => {
    // Navigate to chat
    await page.goto('http://localhost:3000/docs/data/onboarding-neuro-chat.html');
    await page.waitForSelector('[x-data="neuroChatbot"]');

    // Simulate offline mode
    await context.setOffline(true);

    // Verify offline status
    const wsStatus = await page.waitForSelector('.ws-status');
    await expect(wsStatus).toHaveText('Офлайн');

    // Complete cognitive test offline
    await page.click('text=Начать');
    await page.waitForSelector('text=когнитивные способности');

    for (let i = 0; i < 10; i++) {
      await page.click('.test-target');
      await page.waitForTimeout(250);
    }

    // Verify data queuing
    const pendingUpdates = await page.evaluate(() => localStorage.getItem('pendingUpdates'));
    expect(pendingUpdates).toBeTruthy();

    // Restore connection
    await context.setOffline(false);

    // Verify sync
    await page.waitForSelector('.ws-status:text("Онлайн")');
    const syncedUpdates = await page.evaluate(() => localStorage.getItem('pendingUpdates'));
    expect(syncedUpdates).toBeNull();
  });

  test('adapts to different screen sizes', async ({ page }) => {
    // Test desktop layout
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.goto('http://localhost:3000/docs/data/onboarding-neuro-chat.html');
    await page.waitForSelector('[x-data="neuroChatbot"]');

    const desktopChat = await page.$('.chat-container');
    const desktopStyle = await desktopChat.evaluate(el => window.getComputedStyle(el).maxWidth);
    expect(desktopStyle).not.toBe('100%');

    // Test mobile layout
    await page.setViewportSize({ width: 375, height: 667 });
    await page.reload();

    const mobileChat = await page.$('.chat-container');
    const mobileStyle = await mobileChat.evaluate(el => window.getComputedStyle(el).maxWidth);
    expect(mobileStyle).toBe('100%');

    // Verify mobile navigation
    const menuButton = await page.$('.mobile-menu-button');
    expect(menuButton).toBeTruthy();
  });

  test('maintains state during navigation', async ({ page }) => {
    await page.goto('http://localhost:3000/docs/data/onboarding-neuro-chat.html');
    await page.waitForSelector('[x-data="neuroChatbot"]');

    // Start onboarding
    await page.click('text=Начать');
    await page.waitForSelector('text=когнитивные способности');

    // Navigate away
    await page.goto('/some-other-page');

    // Navigate back
    await page.goto('http://localhost:3000/docs/data/onboarding-neuro-chat.html');
    await page.waitForSelector('[x-data="neuroChatbot"]');

    // Verify state is preserved
    const messages = await page.$$('.chat-message');
    const lastMessage = messages[messages.length - 1];
    await expect(lastMessage).toContainText('когнитивные способности');
  });

  test('handles errors appropriately', async ({ page }) => {
    await page.goto('http://localhost:3000/docs/data/onboarding-neuro-chat.html');
    await page.waitForSelector('[x-data="neuroChatbot"]');

    // Simulate failed WebSocket connection
    await page.evaluate(() => {
      window.WebSocket = class extends WebSocket {
        constructor() {
          super('wss://invalid-url');
          setTimeout(() => this.onerror(new Error('Connection failed')), 100);
        }
      };
    });

    // Verify error message
    await page.waitForSelector('.chat-message.error');
    const errorMessage = await page.$('.chat-message.error');
    await expect(errorMessage).toContainText('Ошибка подключения');

    // Verify retry button
    const retryButton = await page.$('.retry-button');
    expect(retryButton).toBeTruthy();
  });
});
