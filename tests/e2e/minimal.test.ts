import { test, expect } from '@playwright/test';

test('basic test', async ({ page }) => {
  await page.goto('http://localhost:3000/docs/data/onboarding-neuro-chat.html');
  await expect(page).toHaveTitle(/Onboarding/);
});
