import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';

describe('Data Analysis', () => {
  beforeEach(() => {
    // Reset DOM and mocks before each test
    jest.clearAllMocks();
    localStorage.clear();
  });

  test('initializes data analysis service', async () => {
    document.body.innerHTML = await fetch('docs/data/onboarding-neuro-chat.html').then(res => res.text());
    const chat = document.querySelector('[x-data="neuroChatbot"]');

    chat.__x.$data.initializeDataAnalysis();

    expect(chat.__x.$data.metrics).toBeDefined();
    expect(chat.__x.$data.trends).toBeDefined();
    expect(chat.__x.$data.predictions).toBeDefined();
  });

  test('calculates cognitive load correctly', async () => {
    document.body.innerHTML = await fetch('docs/data/onboarding-neuro-chat.html').then(res => res.text());
    const chat = document.querySelector('[x-data="neuroChatbot"]');

    const testData = {
      reactionTime: 250,
      accuracy: 0.85,
      complexity: 3
    };

    const load = chat.__x.$data.calculateCognitiveLoad(testData);
    expect(load).toBeDefined();
    expect(typeof load).toBe('number');
    expect(load).toBeGreaterThanOrEqual(0);
    expect(load).toBeLessThanOrEqual(100);
  });

  test('calculates physical load correctly', async () => {
    document.body.innerHTML = await fetch('docs/data/onboarding-neuro-chat.html').then(res => res.text());
    const chat = document.querySelector('[x-data="neuroChatbot"]');

    const testData = {
      heartRate: 120,
      duration: 1800,
      intensity: 4
    };

    const load = chat.__x.$data.calculatePhysicalLoad(testData);
    expect(load).toBeDefined();
    expect(typeof load).toBe('number');
    expect(load).toBeGreaterThanOrEqual(0);
    expect(load).toBeLessThanOrEqual(100);
  });

  test('analyzes trends correctly', async () => {
    document.body.innerHTML = await fetch('docs/data/onboarding-neuro-chat.html').then(res => res.text());
    const chat = document.querySelector('[x-data="neuroChatbot"]');

    const historicalData = [
      { cognitive: 65, physical: 70, timestamp: Date.now() - 7000 },
      { cognitive: 70, physical: 75, timestamp: Date.now() - 6000 },
      { cognitive: 72, physical: 73, timestamp: Date.now() - 5000 },
      { cognitive: 75, physical: 72, timestamp: Date.now() - 4000 },
      { cognitive: 78, physical: 70, timestamp: Date.now() - 3000 }
    ];

    const trends = chat.__x.$data.analyzeTrends(historicalData);
    expect(trends.cognitive).toBeDefined();
    expect(trends.physical).toBeDefined();
    expect(typeof trends.cognitive).toBe('number');
    expect(typeof trends.physical).toBe('number');
  });

  test('generates predictions correctly', async () => {
    document.body.innerHTML = await fetch('docs/data/onboarding-neuro-chat.html').then(res => res.text());
    const chat = document.querySelector('[x-data="neuroChatbot"]');

    const historicalData = [
      { cognitive: 65, physical: 70, timestamp: Date.now() - 7000 },
      { cognitive: 70, physical: 75, timestamp: Date.now() - 6000 },
      { cognitive: 72, physical: 73, timestamp: Date.now() - 5000 },
      { cognitive: 75, physical: 72, timestamp: Date.now() - 4000 },
      { cognitive: 78, physical: 70, timestamp: Date.now() - 3000 }
    ];

    const predictions = chat.__x.$data.generatePredictions(historicalData);
    expect(predictions.cognitive).toBeDefined();
    expect(predictions.physical).toBeDefined();
    expect(typeof predictions.cognitive).toBe('number');
    expect(typeof predictions.physical).toBe('number');
    expect(predictions.cognitive).toBeGreaterThan(0);
    expect(predictions.physical).toBeGreaterThan(0);
  });

  test('persists metrics data correctly', async () => {
    document.body.innerHTML = await fetch('docs/data/onboarding-neuro-chat.html').then(res => res.text());
    const chat = document.querySelector('[x-data="neuroChatbot"]');

    const testMetrics = {
      cognitive: 75,
      physical: 80,
      timestamp: Date.now()
    };

    chat.__x.$data.persistMetrics(testMetrics);

    const storedData = JSON.parse(localStorage.getItem('metricsHistory'));
    expect(storedData).toBeDefined();
    expect(Array.isArray(storedData)).toBe(true);
    expect(storedData).toContainEqual(testMetrics);
  });

  test('processes batch updates correctly', async () => {
    document.body.innerHTML = await fetch('docs/data/onboarding-neuro-chat.html').then(res => res.text());
    const chat = document.querySelector('[x-data="neuroChatbot"]');

    const batchUpdates = [
      { type: 'metrics', data: { cognitive: 75, physical: 80 } },
      { type: 'exercise', data: { completed: true, score: 85 } }
    ];

    await chat.__x.$data.processBatchUpdates(batchUpdates);

    expect(chat.__x.$data.metrics.cognitive).toBe(75);
    expect(chat.__x.$data.metrics.physical).toBe(80);
    expect(localStorage.getItem('metricsHistory')).toBeTruthy();
  });
});
