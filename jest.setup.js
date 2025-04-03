import '@testing-library/jest-dom';

// Mock WebSocket
class MockWebSocket {
  constructor(url) {
    this.url = url;
    this.readyState = WebSocket.CONNECTING;
  }

  addEventListener() {}
  removeEventListener() {}
  close() {}
  send() {}
}

global.WebSocket = MockWebSocket;

// Mock requestAnimationFrame
global.requestAnimationFrame = callback => setTimeout(callback, 0);

// Mock IntersectionObserver
class MockIntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
}

global.IntersectionObserver = MockIntersectionObserver;
