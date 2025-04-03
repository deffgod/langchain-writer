import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';

describe('WebSocket Connection', () => {
  beforeEach(() => {
    // Reset WebSocket mock before each test
    jest.clearAllMocks();
  });

  test('initializes WebSocket connection', async () => {
    const mockWs = {
      readyState: WebSocket.CONNECTING,
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
      close: jest.fn(),
      send: jest.fn(),
    };

    global.WebSocket = jest.fn().mockImplementation(() => mockWs);

    // Initialize chat
    document.body.innerHTML = await fetch('docs/data/onboarding-neuro-chat.html').then(res => res.text());
    const chat = document.querySelector('[x-data="neuroChatbot"]');

    expect(global.WebSocket).toHaveBeenCalledWith('wss://your-websocket-server.com');
    expect(mockWs.addEventListener).toHaveBeenCalledWith('open', expect.any(Function));
    expect(mockWs.addEventListener).toHaveBeenCalledWith('close', expect.any(Function));
    expect(mockWs.addEventListener).toHaveBeenCalledWith('error', expect.any(Function));
    expect(mockWs.addEventListener).toHaveBeenCalledWith('message', expect.any(Function));
  });

  test('handles connection status updates', async () => {
    const mockWs = {
      readyState: WebSocket.CONNECTING,
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
      close: jest.fn(),
      send: jest.fn(),
    };

    global.WebSocket = jest.fn().mockImplementation(() => mockWs);

    document.body.innerHTML = await fetch('docs/data/onboarding-neuro-chat.html').then(res => res.text());
    const chat = document.querySelector('[x-data="neuroChatbot"]');

    // Simulate connection open
    const openHandler = mockWs.addEventListener.mock.calls.find(call => call[0] === 'open')[1];
    openHandler();

    await waitFor(() => {
      const statusIndicator = document.querySelector('.ws-status');
      expect(statusIndicator).toHaveTextContent('Онлайн');
      expect(statusIndicator).toHaveClass('bg-green-500');
    });

    // Simulate connection close
    const closeHandler = mockWs.addEventListener.mock.calls.find(call => call[0] === 'close')[1];
    closeHandler();

    await waitFor(() => {
      const statusIndicator = document.querySelector('.ws-status');
      expect(statusIndicator).toHaveTextContent('Офлайн');
      expect(statusIndicator).toHaveClass('bg-red-500');
    });
  });

  test('implements reconnection logic', async () => {
    const mockWs = {
      readyState: WebSocket.CONNECTING,
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
      close: jest.fn(),
      send: jest.fn(),
    };

    global.WebSocket = jest.fn().mockImplementation(() => mockWs);
    jest.useFakeTimers();

    document.body.innerHTML = await fetch('docs/data/onboarding-neuro-chat.html').then(res => res.text());
    const chat = document.querySelector('[x-data="neuroChatbot"]');

    // Simulate connection close
    const closeHandler = mockWs.addEventListener.mock.calls.find(call => call[0] === 'close')[1];
    closeHandler();

    // Fast-forward timers to trigger reconnection attempts
    jest.advanceTimersByTime(1000); // First attempt
    expect(global.WebSocket).toHaveBeenCalledTimes(2);

    jest.advanceTimersByTime(2000); // Second attempt
    expect(global.WebSocket).toHaveBeenCalledTimes(3);

    jest.advanceTimersByTime(4000); // Third attempt
    expect(global.WebSocket).toHaveBeenCalledTimes(4);

    jest.useRealTimers();
  });

  test('handles message queuing during disconnection', async () => {
    const mockWs = {
      readyState: WebSocket.CONNECTING,
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
      close: jest.fn(),
      send: jest.fn(),
    };

    global.WebSocket = jest.fn().mockImplementation(() => mockWs);

    document.body.innerHTML = await fetch('docs/data/onboarding-neuro-chat.html').then(res => res.text());
    const chat = document.querySelector('[x-data="neuroChatbot"]');

    // Simulate disconnection
    const closeHandler = mockWs.addEventListener.mock.calls.find(call => call[0] === 'close')[1];
    closeHandler();

    // Attempt to send message during disconnection
    chat.__x.$data.queueUpdate({ type: 'test', data: 'test message' });

    // Verify message is queued
    expect(localStorage.getItem('pendingUpdates')).toBeTruthy();
    const pendingUpdates = JSON.parse(localStorage.getItem('pendingUpdates'));
    expect(pendingUpdates).toContainEqual({ type: 'test', data: 'test message' });

    // Simulate reconnection
    const openHandler = mockWs.addEventListener.mock.calls.find(call => call[0] === 'open')[1];
    openHandler();

    // Verify queued messages are sent
    expect(mockWs.send).toHaveBeenCalledWith(JSON.stringify({ type: 'test', data: 'test message' }));
    expect(localStorage.getItem('pendingUpdates')).toBeNull();
  });
});
