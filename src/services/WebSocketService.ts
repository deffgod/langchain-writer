import { Exercise } from './CognitiveLoadManager';
import { IntegratedMetrics } from '../types/metrics';

type WebSocketEventType =
  | 'exercise_update'
  | 'metrics_update'
  | 'pattern_update'
  | 'preference_update'
  | 'batch_update'
  | 'heartbeat'
  | 'connection_status';

interface WebSocketMessage<T = any> {
  type: WebSocketEventType;
  data: T;
  timestamp: string;
  user_id: string;
  batch_id?: string;
}

interface WebSocketOptions {
  url: string;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  heartbeatInterval?: number;
  batchDelay?: number;
}

interface BatchUpdate {
  exercises: Exercise[];
  metrics: IntegratedMetrics;
}

export class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private heartbeatInterval: number;
  private heartbeatTimer: NodeJS.Timeout | null = null;
  private batchTimer: NodeJS.Timeout | null = null;
  private batchQueue: Map<string, BatchUpdate> = new Map();
  private readonly eventListeners = new Map<string, Set<(data: any) => void>>();

  constructor(private readonly options: WebSocketOptions) {
    this.heartbeatInterval = options.heartbeatInterval ?? 30000; // 30 seconds default
    this.connect();
  }

  public connect(): void {
    try {
      this.ws = new WebSocket(this.options.url);
      this.setupEventHandlers();
      this.startHeartbeat();
    } catch (error) {
      console.error('WebSocket connection error:', error);
      this.handleReconnect();
    }
  }

  public subscribe<T>(
    eventType: WebSocketEventType,
    callback: (data: T) => void
  ): () => void {
    if (!this.eventListeners.has(eventType)) {
      this.eventListeners.set(eventType, new Set());
    }

    const listeners = this.eventListeners.get(eventType)!;
    listeners.add(callback);

    return () => {
      listeners.delete(callback);
      if (listeners.size === 0) {
        this.eventListeners.delete(eventType);
      }
    };
  }

  public sendMessage<T>(message: WebSocketMessage<T>): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected. Message not sent:', message);
      this.handleMessageQueue(message);
    }
  }

  public updateExercise(exercise: Exercise, userId: string): void {
    const batchId = `batch_${userId}_${Date.now()}`;
    this.queueBatchUpdate(batchId, 'exercise', exercise, userId);
  }

  public updateMetrics(metrics: IntegratedMetrics, userId: string): void {
    const batchId = `batch_${userId}_${Date.now()}`;
    this.queueBatchUpdate(batchId, 'metrics', metrics, userId);
  }

  public disconnect(): void {
    this.stopHeartbeat();
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  private setupEventHandlers(): void {
    if (!this.ws) return;

    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
      this.notifyConnectionStatus(true);
      this.processPendingMessages();
    };

    this.ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        if (message.type === 'heartbeat') {
          this.handleHeartbeat();
        } else {
          this.handleMessage(message);
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    this.ws.onclose = () => {
      console.log('WebSocket disconnected');
      this.notifyConnectionStatus(false);
      this.handleReconnect();
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  private handleMessage(message: WebSocketMessage): void {
    const listeners = this.eventListeners.get(message.type);
    if (listeners) {
      listeners.forEach(callback => {
        try {
          callback(message.data);
        } catch (error) {
          console.error('Error in WebSocket event listener:', error);
        }
      });
    }
  }

  private handleReconnect(): void {
    this.stopHeartbeat();
    const maxAttempts = this.options.maxReconnectAttempts ?? 5;
    const interval = this.options.reconnectInterval ?? 5000;

    if (this.reconnectAttempts < maxAttempts) {
      this.reconnectAttempts++;
      console.log(`Reconnecting... Attempt ${this.reconnectAttempts}/${maxAttempts}`);

      setTimeout(() => {
        this.connect();
      }, interval);
    } else {
      console.error('Max reconnection attempts reached');
    }
  }

  private startHeartbeat(): void {
    this.heartbeatTimer = setInterval(() => {
      this.sendMessage({
        type: 'heartbeat',
        data: { timestamp: Date.now() },
        timestamp: new Date().toISOString(),
        user_id: 'system'
      });
    }, this.heartbeatInterval);
  }

  private stopHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  private handleHeartbeat(): void {
    // Reset connection monitoring
    this.reconnectAttempts = 0;
  }

  private queueBatchUpdate(
    batchId: string,
    type: 'exercise' | 'metrics',
    data: Exercise | IntegratedMetrics,
    userId: string
  ): void {
    let batch = this.batchQueue.get(batchId) ?? { exercises: [], metrics: {} as IntegratedMetrics };

    if (type === 'exercise') {
      batch.exercises.push(data as Exercise);
    } else {
      batch.metrics = data as IntegratedMetrics;
    }

    this.batchQueue.set(batchId, batch);

    // Set up batch processing timer
    if (!this.batchTimer) {
      this.batchTimer = setTimeout(() => {
        this.processBatchQueue();
      }, this.options.batchDelay ?? 1000);
    }
  }

  private processBatchQueue(): void {
    this.batchTimer = null;

    for (const [batchId, batch] of this.batchQueue.entries()) {
      this.sendMessage({
        type: 'batch_update',
        data: batch,
        timestamp: new Date().toISOString(),
        user_id: batchId.split('_')[1],
        batch_id: batchId
      });
    }

    this.batchQueue.clear();
  }

  private notifyConnectionStatus(isConnected: boolean): void {
    const listeners = this.eventListeners.get('connection_status');
    if (listeners) {
      listeners.forEach(callback => {
        try {
          callback(isConnected);
        } catch (error) {
          console.error('Error in connection status listener:', error);
        }
      });
    }
  }

  private handleMessageQueue(message: WebSocketMessage): void {
    // Implement message queueing for offline support
    // This could be enhanced with IndexedDB or other storage mechanisms
    console.log('Message queued for later delivery:', message);
  }
}
