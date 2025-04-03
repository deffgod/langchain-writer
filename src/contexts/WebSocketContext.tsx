import React, { createContext, useContext, useEffect, useState } from 'react';
import { WebSocketService } from '../services/WebSocketService';
import { Exercise } from '../services/CognitiveLoadManager';
import { IntegratedMetrics } from '../types/metrics';

interface WebSocketContextType {
  isConnected: boolean;
  updateExercise: (exercise: Exercise, userId: string) => void;
  updateMetrics: (metrics: IntegratedMetrics, userId: string) => void;
  subscribeToExercises: (callback: (exercise: Exercise) => void) => () => void;
  subscribeToMetrics: (callback: (metrics: IntegratedMetrics) => void) => () => void;
}

const WebSocketContext = createContext<WebSocketContextType | null>(null);

interface WebSocketProviderProps {
  url: string;
  children: React.ReactNode;
}

export function WebSocketProvider({ url, children }: WebSocketProviderProps) {
  const [isConnected, setIsConnected] = useState(false);
  const [webSocket, setWebSocket] = useState<WebSocketService | null>(null);

  useEffect(() => {
    const ws = new WebSocketService({
      url,
      reconnectInterval: 5000,
      maxReconnectAttempts: 5
    });

    // Monitor connection status
    const unsubscribe = ws.subscribe('connection_status', (status: boolean) => {
      setIsConnected(status);
    });

    setWebSocket(ws);

    return () => {
      unsubscribe();
      ws.disconnect();
    };
  }, [url]);

  const updateExercise = (exercise: Exercise, userId: string) => {
    webSocket?.updateExercise(exercise, userId);
  };

  const updateMetrics = (metrics: IntegratedMetrics, userId: string) => {
    webSocket?.updateMetrics(metrics, userId);
  };

  const subscribeToExercises = (callback: (exercise: Exercise) => void) => {
    if (!webSocket) {
      return () => {};
    }
    return webSocket.subscribe('exercise_update', callback);
  };

  const subscribeToMetrics = (callback: (metrics: IntegratedMetrics) => void) => {
    if (!webSocket) {
      return () => {};
    }
    return webSocket.subscribe('metrics_update', callback);
  };

  const value: WebSocketContextType = {
    isConnected,
    updateExercise,
    updateMetrics,
    subscribeToExercises,
    subscribeToMetrics
  };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
}

export function useWebSocket() {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  return context;
}

// Custom hooks for specific subscriptions
export function useExerciseUpdates(callback: (exercise: Exercise) => void) {
  const { subscribeToExercises } = useWebSocket();

  useEffect(() => {
    const unsubscribe = subscribeToExercises(callback);
    return () => unsubscribe();
  }, [callback, subscribeToExercises]);
}

export function useMetricsUpdates(callback: (metrics: IntegratedMetrics) => void) {
  const { subscribeToMetrics } = useWebSocket();

  useEffect(() => {
    const unsubscribe = subscribeToMetrics(callback);
    return () => unsubscribe();
  }, [callback, subscribeToMetrics]);
}
