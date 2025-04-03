import { IntegratedMetrics } from '../types/metrics';
import { Exercise } from './CognitiveLoadManager';

interface UserPreferences {
  preferred_exercise_types: string[];
  avoided_exercise_types: string[];
  optimal_session_duration: number;
  preferred_time_of_day: string;
  recovery_needs: {
    neural: number;
    physical: number;
  };
}

interface LearningPattern {
  exercise_type: string;
  improvement_rate: number;
  consistency: number;
  optimal_frequency: number;
  optimal_intensity: number;
}

interface PersonalizationProfile {
  user_id: string;
  preferences: UserPreferences;
  learning_patterns: LearningPattern[];
  adaptation_history: {
    timestamp: Date;
    metrics: IntegratedMetrics;
    adjustments: any;
  }[];
}

export class PersonalizationEngine {
  private readonly MIN_DATA_POINTS = 5;
  private readonly LEARNING_RATE = 0.1;
  private readonly ADAPTATION_THRESHOLD = 0.15;

  constructor(
    private readonly profile: PersonalizationProfile,
    private readonly currentMetrics: IntegratedMetrics
  ) {}

  public generatePersonalizedPlan(exercises: Exercise[]): Exercise[] {
    const adaptedExercises = this.adaptExercisesToPreferences(exercises);
    const sequencedExercises = this.optimizeSequence(adaptedExercises);
    const finalizedExercises = this.applyLearningPatterns(sequencedExercises);

    return finalizedExercises;
  }

  public updateLearningPatterns(
    exerciseResults: Array<{ exercise_id: string; performance: number }>
  ): void {
    exerciseResults.forEach(result => {
      const exercise = this.findExerciseById(result.exercise_id);
      if (exercise) {
        this.updatePatternForExercise(exercise.type, result.performance);
      }
    });
  }

  private adaptExercisesToPreferences(exercises: Exercise[]): Exercise[] {
    const { preferences } = this.profile;

    return exercises.map(exercise => {
      const adapted = { ...exercise };

      // Adjust intensity based on preferences
      if (preferences.preferred_exercise_types.includes(exercise.type)) {
        adapted.neural_load *= 1.1;
        adapted.physical_load *= 1.1;
      }

      if (preferences.avoided_exercise_types.includes(exercise.type)) {
        adapted.neural_load *= 0.9;
        adapted.physical_load *= 0.9;
      }

      // Adjust duration based on optimal session length
      const durationFactor = preferences.optimal_session_duration /
        exercises.reduce((sum, ex) => sum + ex.duration, 0);
      adapted.duration = Math.round(adapted.duration * durationFactor);

      return adapted;
    });
  }

  private optimizeSequence(exercises: Exercise[]): Exercise[] {
    const { learning_patterns } = this.profile;

    return exercises.sort((a, b) => {
      const patternA = this.findLearningPattern(a.type);
      const patternB = this.findLearningPattern(b.type);

      // Sort based on optimal timing and effectiveness
      const scoreA = this.calculateExerciseScore(a, patternA);
      const scoreB = this.calculateExerciseScore(b, patternB);

      return scoreB - scoreA;
    });
  }

  private applyLearningPatterns(exercises: Exercise[]): Exercise[] {
    return exercises.map(exercise => {
      const pattern = this.findLearningPattern(exercise.type);
      if (!pattern) return exercise;

      const adapted = { ...exercise };

      // Adjust intensity based on learning pattern
      const intensityFactor = pattern.optimal_intensity /
        ((adapted.neural_load + adapted.physical_load) / 2);

      adapted.neural_load *= intensityFactor;
      adapted.physical_load *= intensityFactor;

      // Adjust duration based on improvement rate
      if (pattern.improvement_rate > 0.7) {
        adapted.duration *= 1.2; // Increase duration for exercises showing good progress
      } else if (pattern.improvement_rate < 0.3) {
        adapted.duration *= 0.8; // Decrease duration for challenging exercises
      }

      return adapted;
    });
  }

  private findLearningPattern(exerciseType: string): LearningPattern | null {
    return this.profile.learning_patterns.find(
      pattern => pattern.exercise_type === exerciseType
    ) || null;
  }

  private calculateExerciseScore(
    exercise: Exercise,
    pattern: LearningPattern | null
  ): number {
    if (!pattern) return 0;

    return (
      pattern.improvement_rate * 0.4 +
      pattern.consistency * 0.3 +
      (1 - Math.abs(pattern.optimal_intensity -
        ((exercise.neural_load + exercise.physical_load) / 2))) * 0.3
    );
  }

  private findExerciseById(id: string): Exercise | null {
    // Implementation would depend on exercise storage/retrieval mechanism
    return null;
  }

  private updatePatternForExercise(
    exerciseType: string,
    performance: number
  ): void {
    const pattern = this.findLearningPattern(exerciseType);
    if (!pattern) return;

    // Update improvement rate with exponential moving average
    pattern.improvement_rate =
      (1 - this.LEARNING_RATE) * pattern.improvement_rate +
      this.LEARNING_RATE * performance;

    // Update consistency based on performance variance
    const recentPerformances = this.profile.adaptation_history
      .slice(-this.MIN_DATA_POINTS)
      .map(h => h.adjustments[exerciseType] || 0);

    pattern.consistency = this.calculateConsistency(recentPerformances);
  }

  private calculateConsistency(performances: number[]): number {
    if (performances.length < this.MIN_DATA_POINTS) return 0.5;

    const mean = performances.reduce((sum, p) => sum + p, 0) / performances.length;
    const variance = performances.reduce(
      (sum, p) => sum + Math.pow(p - mean, 2),
      0
    ) / performances.length;

    return Math.max(0, 1 - Math.sqrt(variance));
  }
}
