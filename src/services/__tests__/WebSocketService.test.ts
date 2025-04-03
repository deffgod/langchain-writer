import { WebSocketService } from '../WebSocketService';
import { Exercise } from '../CognitiveLoadManager';
import { IntegratedMetrics } from '../../types/metrics';

describe('WebSocketService', () => {
  let service: WebSocketService;
  const mockUrl = 'ws://localhost:8080';

  beforeEach(() => {
    service = new WebSocketService({
      url: mockUrl,
      reconnectInterval: 1000,
      maxReconnectAttempts: 3
    });
  });

  afterEach(() => {
    service.disconnect();
  });

  describe('connection management', () => {
    it('should connect to WebSocket server', () => {
      expect(service['ws']).toBeTruthy();
      expect(service['ws']?.url).toBe(mockUrl);
    });

    it('should handle reconnection on disconnect', () => {
      const mockReconnect = jest.spyOn(service as any, 'handleReconnect');
      service['ws']?.onclose?.({} as CloseEvent);
      expect(mockReconnect).toHaveBeenCalled();
    });

    it('should respect max reconnection attempts', () => {
      const mockConnect = jest.spyOn(service, 'connect');
      for (let i = 0; i < 5; i++) {
        service['handleReconnect']();
      }
      expect(mockConnect).toHaveBeenCalledTimes(3);
    });
  });

  describe('event subscription', () => {
    it('should allow subscribing to events', () => {
      const callback = jest.fn();
      const unsubscribe = service.subscribe('exercise_update', callback);

      expect(service['eventListeners'].get('exercise_update')?.has(callback)).toBe(true);
      unsubscribe();
      expect(service['eventListeners'].get('exercise_update')?.has(callback)).toBe(false);
    });

    it('should handle multiple subscribers', () => {
      const callback1 = jest.fn();
      const callback2 = jest.fn();

      service.subscribe('metrics_update', callback1);
      service.subscribe('metrics_update', callback2);

      expect(service['eventListeners'].get('metrics_update')?.size).toBe(2);
    });
  });

  describe('message handling', () => {
    it('should send exercise updates', () => {
      const mockSend = jest.spyOn(service['ws'] as WebSocket, 'send');
      const exercise: Exercise = {
        id: '1',
        name: 'Test Exercise',
        neural_load: 0.5,
        physical_load: 0.6,
        duration: 300,
        type: 'strength'
      };

      service.updateExercise(exercise, 'user123');

      expect(mockSend).toHaveBeenCalledWith(
        expect.stringContaining('"type":"exercise_update"')
      );
    });

    it('should send metrics updates', () => {
      const mockSend = jest.spyOn(service['ws'] as WebSocket, 'send');
      const metrics: Partial<IntegratedMetrics> = {
        sync_score: 0.8,
        timestamp: new Date()
      };

      service.updateMetrics(metrics as IntegratedMetrics, 'user123');

      expect(mockSend).toHaveBeenCalledWith(
        expect.stringContaining('"type":"metrics_update"')
      );
    });

    it('should handle incoming messages', () => {
      const callback = jest.fn();
      service.subscribe('exercise_update', callback);

      const mockMessage = {
        type: 'exercise_update',
        data: { id: '1', name: 'Test' },
        timestamp: new Date().toISOString(),
        user_id: 'user123'
      };

      service['ws']?.onmessage?.({ data: JSON.stringify(mockMessage) } as MessageEvent);

      expect(callback).toHaveBeenCalledWith(mockMessage.data);
    });
  });

  describe('error handling', () => {
    it('should handle connection errors', () => {
      const mockError = new Error('Connection failed');
      const mockReconnect = jest.spyOn(service as any, 'handleReconnect');

      service['ws']?.onerror?.(mockError as Event);
      expect(mockReconnect).toHaveBeenCalled();
    });

    it('should handle message parsing errors', () => {
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
      service['ws']?.onmessage?.({ data: 'invalid json' } as MessageEvent);

      expect(consoleSpy).toHaveBeenCalledWith(
        'Error parsing WebSocket message:',
        expect.any(Error)
      );
    });
  });
});
