import React, { useEffect, useState } from 'react';
import { Card } from '../ui/card';
import { Progress } from '../ui/progress';
import { useWebSocket, useMetricsUpdates } from '../../contexts/WebSocketContext';
import { IntegratedMetrics } from '../../types/metrics';

interface LearningPattern {
  exercise_type: string;
  improvement_rate: number;
  consistency: number;
  optimal_frequency: number;
  optimal_intensity: number;
}

interface PersonalizationInsightsProps {
  initialPatterns: LearningPattern[];
  initialPreferences: {
    preferred_exercise_types: string[];
    avoided_exercise_types: string[];
    optimal_session_duration: number;
    preferred_time_of_day: string;
    recovery_needs: {
      neural: number;
      physical: number;
    };
  };
  userId: string;
}

export function PersonalizationInsights({
  initialPatterns,
  initialPreferences,
  userId
}: PersonalizationInsightsProps) {
  const [patterns, setPatterns] = useState(initialPatterns);
  const [preferences, setPreferences] = useState(initialPreferences);
  const { isConnected } = useWebSocket();

  // Subscribe to metrics updates
  useMetricsUpdates((metrics: IntegratedMetrics) => {
    // Update patterns based on new metrics
    setPatterns(currentPatterns =>
      currentPatterns.map(pattern => ({
        ...pattern,
        improvement_rate: calculateImprovementRate(pattern, metrics),
        consistency: calculateConsistency(pattern, metrics)
      }))
    );
  });

  // Update connection status indicator
  useEffect(() => {
    console.log('WebSocket connection status:', isConnected);
  }, [isConnected]);

  return (
    <div className="space-y-6">
      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold">Personalization Insights</h2>
          <div className="flex items-center gap-2">
            <div
              className={`w-2 h-2 rounded-full ${
                isConnected ? 'bg-success' : 'bg-error'
              }`}
            />
            <span className="text-sm text-textSecondary">
              {isConnected ? 'Live' : 'Offline'}
            </span>
          </div>
        </div>

        {/* Learning Patterns */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-2">Learning Patterns</h3>
          <div className="grid gap-4 md:grid-cols-2">
            {patterns.map((pattern, index) => (
              <div
                key={index}
                className="p-4 bg-surface rounded-lg"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium capitalize">
                    {pattern.exercise_type}
                  </span>
                  <span className="text-xs px-2 py-1 bg-surfaceLight rounded-full">
                    {getProgressLevel(pattern.improvement_rate)}
                  </span>
                </div>

                <div className="space-y-3">
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-textSecondary">Improvement</span>
                      <span>{Math.round(pattern.improvement_rate * 100)}%</span>
                    </div>
                    <Progress
                      value={pattern.improvement_rate * 100}
                      className="h-1.5 bg-surfaceLight"
                      indicatorClassName={getProgressColor(pattern.improvement_rate)}
                    />
                  </div>

                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-textSecondary">Consistency</span>
                      <span>{Math.round(pattern.consistency * 100)}%</span>
                    </div>
                    <Progress
                      value={pattern.consistency * 100}
                      className="h-1.5 bg-surfaceLight"
                      indicatorClassName={getProgressColor(pattern.consistency)}
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4 mt-2">
                    <div>
                      <span className="text-sm text-textSecondary">
                        Optimal Frequency
                      </span>
                      <div className="font-medium">
                        {formatFrequency(pattern.optimal_frequency)}
                      </div>
                    </div>
                    <div>
                      <span className="text-sm text-textSecondary">
                        Optimal Intensity
                      </span>
                      <div className="font-medium">
                        {Math.round(pattern.optimal_intensity * 100)}%
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Preferences */}
        <div>
          <h3 className="text-lg font-semibold mb-2">Training Preferences</h3>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="p-4 bg-surface rounded-lg">
              <h4 className="font-medium mb-2">Exercise Types</h4>
              <div className="space-y-2">
                <div>
                  <span className="text-sm text-textSecondary">Preferred</span>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {preferences.preferred_exercise_types.map((type, index) => (
                      <span
                        key={index}
                        className="text-xs px-2 py-1 bg-primary/20 text-primary rounded-full"
                      >
                        {type}
                      </span>
                    ))}
                  </div>
                </div>
                <div>
                  <span className="text-sm text-textSecondary">Avoided</span>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {preferences.avoided_exercise_types.map((type, index) => (
                      <span
                        key={index}
                        className="text-xs px-2 py-1 bg-error/20 text-error rounded-full"
                      >
                        {type}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            <div className="p-4 bg-surface rounded-lg">
              <h4 className="font-medium mb-2">Session Details</h4>
              <div className="space-y-4">
                <div>
                  <span className="text-sm text-textSecondary">
                    Optimal Duration
                  </span>
                  <div className="font-medium">
                    {preferences.optimal_session_duration} minutes
                  </div>
                </div>
                <div>
                  <span className="text-sm text-textSecondary">
                    Preferred Time
                  </span>
                  <div className="font-medium capitalize">
                    {preferences.preferred_time_of_day}
                  </div>
                </div>
                <div>
                  <span className="text-sm text-textSecondary">
                    Recovery Needs
                  </span>
                  <div className="grid grid-cols-2 gap-4 mt-1">
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>Neural</span>
                        <span>{preferences.recovery_needs.neural}%</span>
                      </div>
                      <Progress
                        value={preferences.recovery_needs.neural}
                        className="h-1.5 bg-surfaceLight"
                      />
                    </div>
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>Physical</span>
                        <span>{preferences.recovery_needs.physical}%</span>
                      </div>
                      <Progress
                        value={preferences.recovery_needs.physical}
                        className="h-1.5 bg-surfaceLight"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}

function getProgressLevel(rate: number): string {
  if (rate < 0.3) return 'Needs Work';
  if (rate < 0.6) return 'Improving';
  if (rate < 0.8) return 'Good';
  return 'Excellent';
}

function getProgressColor(rate: number): string {
  if (rate < 0.3) return 'bg-error';
  if (rate < 0.6) return 'bg-warning';
  if (rate < 0.8) return 'bg-primary';
  return 'bg-success';
}

function formatFrequency(frequency: number): string {
  if (frequency <= 1) return 'Daily';
  if (frequency <= 2) return 'Every 2 days';
  if (frequency <= 7) return `${frequency} times/week`;
  return `Every ${frequency} days`;
}

// New helper functions for real-time updates
function calculateImprovementRate(
  pattern: LearningPattern,
  metrics: IntegratedMetrics
): number {
  // Implementation would depend on your specific metrics calculation logic
  return pattern.improvement_rate;
}

function calculateConsistency(
  pattern: LearningPattern,
  metrics: IntegratedMetrics
): number {
  // Implementation would depend on your specific consistency calculation logic
  return pattern.consistency;
}
