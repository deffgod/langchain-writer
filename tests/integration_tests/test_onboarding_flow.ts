import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';

describe('Onboarding Flow Integration', () => {
  beforeEach(() => {
    // Reset DOM and mocks before each test
    jest.clearAllMocks();
    localStorage.clear();
  });

  test('completes full onboarding flow', async () => {
    // Initialize chat
    document.body.innerHTML = await fetch('docs/data/onboarding-neuro-chat.html').then(res => res.text());
    const chat = document.querySelector('[x-data="neuroChatbot"]');

    // Verify initial state
    expect(chat.__x.$data.wsStatus).toBe('connecting');
    expect(chat.__x.$data.messages).toHaveLength(0);

    // Start chat and verify welcome messages
    chat.__x.$data.startChat();

    await waitFor(() => {
      const messages = document.querySelectorAll('.chat-message');
      expect(messages).toHaveLength(3);
      expect(messages[0]).toHaveTextContent('Добро пожаловать');
      expect(messages[1]).toHaveTextContent('персонализированную программу');
      expect(messages[2]).toHaveTextContent('Готовы начать');
    });

    // Verify options are displayed
    const options = document.querySelectorAll('.option-button');
    expect(options).toHaveLength(2);
    expect(options[0]).toHaveTextContent('Начать');
    expect(options[1]).toHaveTextContent('Что такое нейрофитнес');

    // Choose to start
    fireEvent.click(options[0]);

    // Verify cognitive test introduction
    await waitFor(() => {
      const messages = document.querySelectorAll('.chat-message');
      expect(messages[messages.length - 1]).toHaveTextContent('оценим ваши текущие когнитивные способности');
    });

    // Complete cognitive test
    chat.__x.$data.completeCognitiveTest({
      reactionTime: 250,
      accuracy: 0.85,
      complexity: 3
    });

    // Verify cognitive results
    await waitFor(() => {
      const messages = document.querySelectorAll('.chat-message');
      const progressMessage = document.querySelector('.chat-message.progress');
      expect(progressMessage).toBeInTheDocument();
      expect(progressMessage.querySelector('.cognitive-load')).toBeTruthy();
    });

    // Start physical assessment
    const continueButton = document.querySelector('.option-button');
    fireEvent.click(continueButton);

    // Verify physical assessment introduction
    await waitFor(() => {
      const messages = document.querySelectorAll('.chat-message');
      expect(messages[messages.length - 1]).toHaveTextContent('оценим вашу физическую форму');
    });

    // Complete physical assessment
    chat.__x.$data.completePhysicalAssessment({
      heartRate: 120,
      duration: 1800,
      intensity: 4
    });

    // Verify physical results
    await waitFor(() => {
      const messages = document.querySelectorAll('.chat-message');
      const progressMessage = document.querySelector('.chat-message.progress');
      expect(progressMessage).toBeInTheDocument();
      expect(progressMessage.querySelector('.physical-load')).toBeTruthy();
    });

    // Generate plan
    const generatePlanButton = document.querySelector('.option-button');
    fireEvent.click(generatePlanButton);

    // Verify plan generation
    await waitFor(() => {
      const messages = document.querySelectorAll('.chat-message');
      expect(messages[messages.length - 1]).toHaveTextContent('ваш персональный план');
    });

    // Verify WebSocket communication
    expect(chat.__x.$data.wsStatus).toBe('connected');
    expect(localStorage.getItem('metricsHistory')).toBeTruthy();
    expect(localStorage.getItem('progressHistory')).toBeTruthy();
  });

  test('handles network interruption during onboarding', async () => {
    document.body.innerHTML = await fetch('docs/data/onboarding-neuro-chat.html').then(res => res.text());
    const chat = document.querySelector('[x-data="neuroChatbot"]');

    // Start chat
    chat.__x.$data.startChat();

    // Simulate network interruption
    const mockWs = chat.__x.$data.ws;
    const closeHandler = mockWs.addEventListener.mock.calls.find(call => call[0] === 'close')[1];
    closeHandler();

    // Verify offline status
    await waitFor(() => {
      const statusIndicator = document.querySelector('.ws-status');
      expect(statusIndicator).toHaveTextContent('Офлайн');
    });

    // Complete cognitive test during offline
    chat.__x.$data.completeCognitiveTest({
      reactionTime: 250,
      accuracy: 0.85,
      complexity: 3
    });

    // Verify data is queued
    expect(localStorage.getItem('pendingUpdates')).toBeTruthy();

    // Simulate reconnection
    const openHandler = mockWs.addEventListener.mock.calls.find(call => call[0] === 'open')[1];
    openHandler();

    // Verify queued data is sent
    await waitFor(() => {
      expect(localStorage.getItem('pendingUpdates')).toBeNull();
      expect(mockWs.send).toHaveBeenCalled();
    });
  });

  test('persists progress across sessions', async () => {
    document.body.innerHTML = await fetch('docs/data/onboarding-neuro-chat.html').then(res => res.text());
    const chat = document.querySelector('[x-data="neuroChatbot"]');

    // Complete first session
    chat.__x.$data.startChat();
    chat.__x.$data.completeCognitiveTest({
      reactionTime: 250,
      accuracy: 0.85,
      complexity: 3
    });

    // Store progress
    const firstSessionProgress = chat.__x.$data.getCognitiveProgress();

    // Clear DOM and simulate new session
    document.body.innerHTML = await fetch('docs/data/onboarding-neuro-chat.html').then(res => res.text());
    const newChat = document.querySelector('[x-data="neuroChatbot"]');
    newChat.__x.$data.startChat();

    // Verify progress is restored
    const restoredProgress = newChat.__x.$data.getCognitiveProgress();
    expect(restoredProgress).toEqual(firstSessionProgress);
  });
});
