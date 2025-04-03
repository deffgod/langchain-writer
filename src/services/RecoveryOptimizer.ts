import { IntegratedMetrics } from '../types/metrics';

interface RecoveryRecommendation {
  recovery_duration: number; // in hours
  recommended_activities: string[];
  intensity_adjustments: {
    neural: number;
    physical: number;
  };
  focus_areas: string[];
}

export class RecoveryOptimizer {
  private readonly MIN_RECOVERY_HOURS = 8;
  private readonly MAX_RECOVERY_HOURS = 72;
  private readonly RECOVERY_THRESHOLD = 0.7;

  constructor(private readonly metrics: IntegratedMetrics) {}

  public calculateOptimalRecovery(): RecoveryRecommendation {
    const neuralLoad = this.calculateNeuralLoad();
    const physicalLoad = this.calculatePhysicalLoad();
    const recoveryDuration = this.calculateRecoveryDuration(neuralLoad, physicalLoad);

    return {
      recovery_duration: recoveryDuration,
      recommended_activities: this.getRecoveryActivities(neuralLoad, physicalLoad),
      intensity_adjustments: this.calculateIntensityAdjustments(neuralLoad, physicalLoad),
      focus_areas: this.determineFocusAreas()
    };
  }

  private calculateNeuralLoad(): number {
    const { vision, balance, coordination } = this.metrics.neural;

    // Calculate weighted average of neural metrics
    const weights = {
      vision: 0.35,
      balance: 0.35,
      coordination: 0.3
    };

    return (
      (weights.vision * this.calculateVisionLoad(vision)) +
      (weights.balance * this.calculateBalanceLoad(balance)) +
      (weights.coordination * this.calculateCoordinationLoad(coordination))
    );
  }

  private calculatePhysicalLoad(): number {
    const { performance, recovery } = this.metrics.physical;

    // Calculate weighted average of physical metrics
    return (
      (0.4 * (1 - performance.endurance / 100)) +
      (0.3 * recovery.fatigue_level / 100) +
      (0.3 * recovery.muscle_soreness / 100)
    );
  }

  private calculateRecoveryDuration(neuralLoad: number, physicalLoad: number): number {
    const baseRecovery = this.MIN_RECOVERY_HOURS;
    const loadFactor = Math.max(neuralLoad, physicalLoad);

    const additionalHours = Math.round(
      (this.MAX_RECOVERY_HOURS - this.MIN_RECOVERY_HOURS) * loadFactor
    );

    return Math.min(baseRecovery + additionalHours, this.MAX_RECOVERY_HOURS);
  }

  private getRecoveryActivities(neuralLoad: number, physicalLoad: number): string[] {
    const activities: string[] = [];

    if (neuralLoad > this.RECOVERY_THRESHOLD) {
      activities.push(
        'Meditation',
        'Deep breathing exercises',
        'Light stretching',
        'Nature walk'
      );
    }

    if (physicalLoad > this.RECOVERY_THRESHOLD) {
      activities.push(
        'Light mobility work',
        'Gentle yoga',
        'Swimming',
        'Progressive muscle relaxation'
      );
    }

    return activities;
  }

  private calculateIntensityAdjustments(neuralLoad: number, physicalLoad: number) {
    return {
      neural: Math.max(0, 1 - neuralLoad),
      physical: Math.max(0, 1 - physicalLoad)
    };
  }

  private determineFocusAreas(): string[] {
    const focusAreas: string[] = [];
    const { neural, physical } = this.metrics;

    // Check neural metrics
    if (neural.vision.focus_score < 70) focusAreas.push('Vision training');
    if (neural.balance.vestibular_score < 70) focusAreas.push('Balance work');
    if (neural.coordination.reaction_time < 70) focusAreas.push('Coordination drills');

    // Check physical metrics
    if (physical.performance.flexibility < 70) focusAreas.push('Mobility work');
    if (physical.recovery.sleep_quality < 70) focusAreas.push('Sleep optimization');
    if (physical.recovery.stress_level > 70) focusAreas.push('Stress management');

    return focusAreas;
  }

  private calculateVisionLoad(vision: IntegratedMetrics['neural']['vision']): number {
    return (100 - vision.focus_score) / 100;
  }

  private calculateBalanceLoad(balance: IntegratedMetrics['neural']['balance']): number {
    return (100 - balance.vestibular_score) / 100;
  }

  private calculateCoordinationLoad(coordination: IntegratedMetrics['neural']['coordination']): number {
    return (coordination.reaction_time) / 100;
  }
}
