import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';

describe('Progress Tracking', () => {
  beforeEach(() => {
    // Reset DOM and mocks before each test
    jest.clearAllMocks();
    localStorage.clear();
  });

  test('tracks cognitive progress correctly', async () => {
    document.body.innerHTML = await fetch('docs/data/onboarding-neuro-chat.html').then(res => res.text());
    const chat = document.querySelector('[x-data="neuroChatbot"]');

    // Simulate multiple cognitive test results
    const testResults = [
      { reactionTime: 250, accuracy: 0.85, complexity: 3 },
      { reactionTime: 245, accuracy: 0.87, complexity: 3 },
      { reactionTime: 240, accuracy: 0.88, complexity: 3 },
      { reactionTime: 235, accuracy: 0.90, complexity: 3 }
    ];

    testResults.forEach(result => {
      chat.__x.$data.updateCognitiveProgress(result);
    });

    const progress = chat.__x.$data.getCognitiveProgress();
    expect(progress.current).toBeGreaterThan(progress.initial);
    expect(progress.trend).toBeDefined();
    expect(progress.prediction).toBeGreaterThan(progress.current);
  });

  test('tracks physical progress correctly', async () => {
    document.body.innerHTML = await fetch('docs/data/onboarding-neuro-chat.html').then(res => res.text());
    const chat = document.querySelector('[x-data="neuroChatbot"]');

    // Simulate multiple physical exercise results
    const exerciseResults = [
      { heartRate: 120, duration: 1800, intensity: 4 },
      { heartRate: 125, duration: 1900, intensity: 4 },
      { heartRate: 122, duration: 2000, intensity: 4 },
      { heartRate: 120, duration: 2100, intensity: 4 }
    ];

    exerciseResults.forEach(result => {
      chat.__x.$data.updatePhysicalProgress(result);
    });

    const progress = chat.__x.$data.getPhysicalProgress();
    expect(progress.current).toBeGreaterThan(progress.initial);
    expect(progress.trend).toBeDefined();
    expect(progress.prediction).toBeGreaterThan(progress.current);
  });

  test('generates progress summary correctly', async () => {
    document.body.innerHTML = await fetch('docs/data/onboarding-neuro-chat.html').then(res => res.text());
    const chat = document.querySelector('[x-data="neuroChatbot"]');

    // Add some test data
    chat.__x.$data.updateProgress({
      cognitive: { current: 75, initial: 65, trend: 5 },
      physical: { current: 80, initial: 70, trend: 3 }
    });

    const summary = chat.__x.$data.generateProgressSummary();
    expect(summary).toBeDefined();
    expect(summary.cognitive).toBeDefined();
    expect(summary.physical).toBeDefined();
    expect(summary.recommendations).toBeDefined();
    expect(Array.isArray(summary.recommendations)).toBe(true);
  });

  test('persists progress data correctly', async () => {
    document.body.innerHTML = await fetch('docs/data/onboarding-neuro-chat.html').then(res => res.text());
    const chat = document.querySelector('[x-data="neuroChatbot"]');

    const progressData = {
      cognitive: { current: 75, initial: 65, trend: 5 },
      physical: { current: 80, initial: 70, trend: 3 },
      timestamp: Date.now()
    };

    chat.__x.$data.persistProgress(progressData);

    const storedData = JSON.parse(localStorage.getItem('progressHistory'));
    expect(storedData).toBeDefined();
    expect(Array.isArray(storedData)).toBe(true);
    expect(storedData).toContainEqual(progressData);
  });

  test('updates progress display correctly', async () => {
    document.body.innerHTML = await fetch('docs/data/onboarding-neuro-chat.html').then(res => res.text());
    const chat = document.querySelector('[x-data="neuroChatbot"]');

    const progressData = {
      cognitive: { current: 75, initial: 65, trend: 5 },
      physical: { current: 80, initial: 70, trend: 3 }
    };

    chat.__x.$data.updateProgressDisplay(progressData);

    await waitFor(() => {
      const progressMessage = document.querySelector('.chat-message.progress');
      expect(progressMessage).toBeInTheDocument();
      expect(progressMessage.querySelector('.cognitive-progress')).toHaveTextContent('75%');
      expect(progressMessage.querySelector('.physical-progress')).toHaveTextContent('80%');
      expect(progressMessage.querySelector('.cognitive-trend')).toHaveTextContent('+5%');
      expect(progressMessage.querySelector('.physical-trend')).toHaveTextContent('+3%');
    });
  });

  test('generates recommendations based on progress', async () => {
    document.body.innerHTML = await fetch('docs/data/onboarding-neuro-chat.html').then(res => res.text());
    const chat = document.querySelector('[x-data="neuroChatbot"]');

    const progressData = {
      cognitive: { current: 75, initial: 65, trend: 5 },
      physical: { current: 80, initial: 70, trend: 3 }
    };

    const recommendations = chat.__x.$data.generateRecommendations(progressData);
    expect(recommendations).toBeDefined();
    expect(Array.isArray(recommendations)).toBe(true);
    expect(recommendations.length).toBeGreaterThan(0);
    recommendations.forEach(rec => {
      expect(rec).toHaveProperty('type');
      expect(rec).toHaveProperty('description');
    });
  });
});
