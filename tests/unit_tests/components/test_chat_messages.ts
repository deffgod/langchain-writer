import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';

describe('Chat Messages', () => {
  beforeEach(() => {
    // Reset DOM and mocks before each test
    jest.clearAllMocks();
    localStorage.clear();
  });

  test('renders bot message correctly', async () => {
    document.body.innerHTML = await fetch('docs/data/onboarding-neuro-chat.html').then(res => res.text());
    const chat = document.querySelector('[x-data="neuroChatbot"]');

    chat.__x.$data.addBotMessage({
      type: 'text',
      content: 'Test bot message',
      isLast: true
    });

    await waitFor(() => {
      const message = document.querySelector('.chat-message.bot');
      expect(message).toBeInTheDocument();
      expect(message).toHaveTextContent('Test bot message');
    });
  });

  test('renders user message correctly', async () => {
    document.body.innerHTML = await fetch('docs/data/onboarding-neuro-chat.html').then(res => res.text());
    const chat = document.querySelector('[x-data="neuroChatbot"]');

    chat.__x.$data.addUserMessage('Test user message');

    await waitFor(() => {
      const message = document.querySelector('.chat-message.user');
      expect(message).toBeInTheDocument();
      expect(message).toHaveTextContent('Test user message');
    });
  });

  test('renders error message correctly', async () => {
    document.body.innerHTML = await fetch('docs/data/onboarding-neuro-chat.html').then(res => res.text());
    const chat = document.querySelector('[x-data="neuroChatbot"]');

    chat.__x.$data.addBotMessage({
      type: 'error',
      content: 'Test error message',
      retryAction: () => {},
      isLast: true
    });

    await waitFor(() => {
      const message = document.querySelector('.chat-message.error');
      expect(message).toBeInTheDocument();
      expect(message).toHaveTextContent('Test error message');
      expect(message.querySelector('.retry-button')).toBeInTheDocument();
    });
  });

  test('renders progress message correctly', async () => {
    document.body.innerHTML = await fetch('docs/data/onboarding-neuro-chat.html').then(res => res.text());
    const chat = document.querySelector('[x-data="neuroChatbot"]');

    chat.__x.$data.addBotMessage({
      type: 'progress',
      content: {
        cognitiveLoad: 75,
        physicalLoad: 60,
        cognitiveChange: 5,
        physicalChange: -2,
        predictions: {
          cognitive: 80,
          physical: 65
        }
      },
      isLast: true
    });

    await waitFor(() => {
      const message = document.querySelector('.chat-message.progress');
      expect(message).toBeInTheDocument();
      expect(message.querySelector('.cognitive-load')).toHaveTextContent('75%');
      expect(message.querySelector('.physical-load')).toHaveTextContent('60%');
      expect(message.querySelector('.cognitive-trend')).toHaveTextContent('+5%');
      expect(message.querySelector('.physical-trend')).toHaveTextContent('-2%');
    });
  });

  test('handles user input submission', async () => {
    document.body.innerHTML = await fetch('docs/data/onboarding-neuro-chat.html').then(res => res.text());
    const chat = document.querySelector('[x-data="neuroChatbot"]');
    const input = document.querySelector('input[type="text"]');
    const form = document.querySelector('form');

    fireEvent.change(input, { target: { value: 'Test input' } });
    fireEvent.submit(form);

    await waitFor(() => {
      const message = document.querySelector('.chat-message.user');
      expect(message).toBeInTheDocument();
      expect(message).toHaveTextContent('Test input');
      expect(input.value).toBe('');
    });
  });

  test('renders options correctly', async () => {
    document.body.innerHTML = await fetch('docs/data/onboarding-neuro-chat.html').then(res => res.text());
    const chat = document.querySelector('[x-data="neuroChatbot"]');

    const options = [
      { text: 'Option 1', value: 'opt1' },
      { text: 'Option 2', value: 'opt2' }
    ];

    chat.__x.$data.setOptions(options);

    await waitFor(() => {
      const optionButtons = document.querySelectorAll('.option-button');
      expect(optionButtons).toHaveLength(2);
      expect(optionButtons[0]).toHaveTextContent('Option 1');
      expect(optionButtons[1]).toHaveTextContent('Option 2');
    });
  });

  test('handles option selection', async () => {
    document.body.innerHTML = await fetch('docs/data/onboarding-neuro-chat.html').then(res => res.text());
    const chat = document.querySelector('[x-data="neuroChatbot"]');

    const options = [
      { text: 'Option 1', value: 'opt1' },
      { text: 'Option 2', value: 'opt2' }
    ];

    chat.__x.$data.setOptions(options);

    await waitFor(() => {
      const optionButtons = document.querySelectorAll('.option-button');
      fireEvent.click(optionButtons[0]);
    });

    await waitFor(() => {
      const message = document.querySelector('.chat-message.user');
      expect(message).toBeInTheDocument();
      expect(message).toHaveTextContent('Option 1');
      expect(document.querySelectorAll('.option-button')).toHaveLength(0);
    });
  });
});
