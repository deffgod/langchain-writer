import React from 'react';
import { Card } from '../ui/card';
import { Progress } from '../ui/progress';
import { Exercise } from '../../services/CognitiveLoadManager';

interface CognitiveLoadDisplayProps {
  totalLoad: number;
  optimizedSequence: Exercise[];
  adjustments: {
    exercise_id: string;
    intensity_factor: number;
    duration_factor: number;
    rest_period: number;
  }[];
}

export function CognitiveLoadDisplay({
  totalLoad,
  optimizedSequence,
  adjustments
}: CognitiveLoadDisplayProps) {
  return (
    <div className="space-y-6">
      <Card className="p-6">
        <h2 className="text-2xl font-bold mb-4">Cognitive Load Analysis</h2>

        {/* Total Load */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-2">Total Training Load</h3>
          <div className="relative pt-1">
            <div className="flex items-center justify-between mb-2">
              <span>{Math.round(totalLoad * 100)}%</span>
              <span className="text-sm text-textSecondary">
                {getLoadLevel(totalLoad)}
              </span>
            </div>
            <Progress
              value={totalLoad * 100}
              className="h-2 bg-surface"
              indicatorClassName={getLoadColor(totalLoad)}
            />
          </div>
        </div>

        {/* Optimized Sequence */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-2">Optimized Exercise Sequence</h3>
          <div className="space-y-3">
            {optimizedSequence.map((exercise, index) => (
              <div
                key={`${exercise.id}-${index}`}
                className="p-4 bg-surface rounded-lg"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium">{exercise.name}</span>
                  <span className="text-sm text-textSecondary">
                    {exercise.duration}s
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className="text-sm text-textSecondary mb-1">
                      Neural Load
                    </div>
                    <Progress
                      value={exercise.neural_load * 100}
                      className="h-1.5 bg-surfaceLight"
                    />
                  </div>
                  <div>
                    <div className="text-sm text-textSecondary mb-1">
                      Physical Load
                    </div>
                    <Progress
                      value={exercise.physical_load * 100}
                      className="h-1.5 bg-surfaceLight"
                    />
                  </div>
                </div>
                <div className="mt-2 flex items-center">
                  <span className="text-xs px-2 py-1 bg-surfaceLight rounded-full">
                    {exercise.type}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Load Adjustments */}
        <div>
          <h3 className="text-lg font-semibold mb-2">Load Adjustments</h3>
          <div className="space-y-3">
            {adjustments.map((adjustment, index) => (
              <div
                key={`${adjustment.exercise_id}-${index}`}
                className="p-4 bg-surface rounded-lg"
              >
                <div className="grid grid-cols-2 gap-4 mb-2">
                  <div>
                    <span className="text-sm text-textSecondary">Intensity</span>
                    <div className="font-medium">
                      {formatFactor(adjustment.intensity_factor)}
                    </div>
                  </div>
                  <div>
                    <span className="text-sm text-textSecondary">Duration</span>
                    <div className="font-medium">
                      {formatFactor(adjustment.duration_factor)}
                    </div>
                  </div>
                </div>
                <div className="text-sm text-textSecondary">
                  Rest Period: {adjustment.rest_period}s
                </div>
              </div>
            ))}
          </div>
        </div>
      </Card>
    </div>
  );
}

function getLoadLevel(load: number): string {
  if (load < 0.3) return 'Low';
  if (load < 0.6) return 'Moderate';
  if (load < 0.8) return 'High';
  return 'Very High';
}

function getLoadColor(load: number): string {
  if (load < 0.3) return 'bg-success';
  if (load < 0.6) return 'bg-primary';
  if (load < 0.8) return 'bg-warning';
  return 'bg-error';
}

function formatFactor(factor: number): string {
  const percent = Math.round((factor - 1) * 100);
  return percent >= 0 ? `+${percent}%` : `${percent}%`;
}
