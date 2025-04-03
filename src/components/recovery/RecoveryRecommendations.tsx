import React from 'react';
import { Card } from '../ui/card';
import { Progress } from '../ui/progress';

interface RecoveryRecommendationsProps {
  recoveryPlan: {
    recovery_duration: number;
    recommended_activities: string[];
    intensity_adjustments: {
      neural: number;
      physical: number;
    };
    focus_areas: string[];
  };
}

export function RecoveryRecommendations({ recoveryPlan }: RecoveryRecommendationsProps) {
  const {
    recovery_duration,
    recommended_activities,
    intensity_adjustments,
    focus_areas
  } = recoveryPlan;

  return (
    <div className="space-y-6">
      <Card className="p-6">
        <h2 className="text-2xl font-bold mb-4">Recovery Recommendations</h2>

        {/* Recovery Duration */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-2">Recommended Recovery Time</h3>
          <div className="text-3xl font-bold text-primary">
            {recovery_duration} hours
          </div>
        </div>

        {/* Intensity Adjustments */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-2">Training Intensity Adjustments</h3>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between mb-2">
                <span>Neural Load</span>
                <span>{Math.round(intensity_adjustments.neural * 100)}%</span>
              </div>
              <Progress
                value={intensity_adjustments.neural * 100}
                className="h-2 bg-surface"
              />
            </div>
            <div>
              <div className="flex justify-between mb-2">
                <span>Physical Load</span>
                <span>{Math.round(intensity_adjustments.physical * 100)}%</span>
              </div>
              <Progress
                value={intensity_adjustments.physical * 100}
                className="h-2 bg-surface"
              />
            </div>
          </div>
        </div>

        {/* Recommended Activities */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-2">Recommended Activities</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {recommended_activities.map((activity, index) => (
              <div
                key={index}
                className="p-3 bg-surface rounded-lg flex items-center"
              >
                <div className="w-2 h-2 bg-primary rounded-full mr-3" />
                <span>{activity}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Focus Areas */}
        <div>
          <h3 className="text-lg font-semibold mb-2">Focus Areas</h3>
          <div className="flex flex-wrap gap-2">
            {focus_areas.map((area, index) => (
              <span
                key={index}
                className="px-3 py-1 bg-surfaceLight rounded-full text-sm"
              >
                {area}
              </span>
            ))}
          </div>
        </div>
      </Card>
    </div>
  );
}
