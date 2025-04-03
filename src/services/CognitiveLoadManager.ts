import { IntegratedMetrics } from '../types/metrics';

export interface Exercise {
  id: string;
  name: string;
  neural_load: number;
  physical_load: number;
  duration: number;
  type: 'vision' | 'balance' | 'coordination' | 'strength' | 'endurance' | 'flexibility';
}

export interface Adjustment {
  exercise_id: string;
  intensity_factor: number;
  duration_factor: number;
  rest_period: number;
}

export class CognitiveLoadManager {
  private readonly MAX_NEURAL_LOAD = 0.8;
  private readonly MAX_PHYSICAL_LOAD = 0.9;
  private readonly OPTIMAL_LOAD_RATIO = 0.7;

  constructor(private readonly metrics: IntegratedMetrics) {}

  public calculateTotalLoad(neuralLoad: number, physicalLoad: number): number {
    // Apply weighted combination based on user's current metrics
    const neuralWeight = this.calculateNeuralWeight();
    const physicalWeight = 1 - neuralWeight;

    return (neuralLoad * neuralWeight) + (physicalLoad * physicalWeight);
  }

  public optimizeExerciseSequence(exercises: Exercise[]): Exercise[] {
    let currentNeuralLoad = 0;
    let currentPhysicalLoad = 0;
    const optimizedSequence: Exercise[] = [];
    const remainingExercises = [...exercises];

    while (remainingExercises.length > 0) {
      const nextExercise = this.selectNextExercise(
        remainingExercises,
        currentNeuralLoad,
        currentPhysicalLoad
      );

      if (nextExercise) {
        optimizedSequence.push(nextExercise);
        remainingExercises.splice(remainingExercises.indexOf(nextExercise), 1);

        // Update current loads
        currentNeuralLoad = this.updateLoad(currentNeuralLoad, nextExercise.neural_load);
        currentPhysicalLoad = this.updateLoad(currentPhysicalLoad, nextExercise.physical_load);
      } else {
        // If no suitable exercise found, add rest period
        optimizedSequence.push(this.createRestExercise());
        currentNeuralLoad *= 0.7; // Reduce loads during rest
        currentPhysicalLoad *= 0.7;
      }
    }

    return optimizedSequence;
  }

  public adjustIntensity(currentLoad: number, targetLoad: number): Adjustment[] {
    const adjustments: Adjustment[] = [];
    const loadDiff = targetLoad - currentLoad;

    // Calculate adjustment factors
    const intensityFactor = 1 + (loadDiff * 0.5);
    const durationFactor = 1 + (loadDiff * 0.3);
    const restPeriod = this.calculateRestPeriod(currentLoad);

    // Apply adjustments to each exercise
    return adjustments;
  }

  private calculateNeuralWeight(): number {
    const { neural, physical } = this.metrics;
    const neuralFatigue = this.calculateNeuralFatigue(neural);
    const physicalFatigue = this.calculatePhysicalFatigue(physical);

    // Adjust weight based on fatigue levels
    return 0.5 + (physicalFatigue - neuralFatigue) * 0.2;
  }

  private calculateNeuralFatigue(neural: IntegratedMetrics['neural']): number {
    return (
      (1 - neural.vision.focus_score / 100) * 0.4 +
      (1 - neural.balance.vestibular_score / 100) * 0.3 +
      (neural.coordination.reaction_time / 100) * 0.3
    );
  }

  private calculatePhysicalFatigue(physical: IntegratedMetrics['physical']): number {
    return (
      (physical.recovery.fatigue_level / 100) * 0.4 +
      (physical.recovery.muscle_soreness / 100) * 0.3 +
      (1 - physical.performance.endurance / 100) * 0.3
    );
  }

  private selectNextExercise(
    exercises: Exercise[],
    currentNeuralLoad: number,
    currentPhysicalLoad: number
  ): Exercise | null {
    return exercises.find(exercise => {
      const projectedNeuralLoad = this.updateLoad(currentNeuralLoad, exercise.neural_load);
      const projectedPhysicalLoad = this.updateLoad(currentPhysicalLoad, exercise.physical_load);

      return (
        projectedNeuralLoad <= this.MAX_NEURAL_LOAD &&
        projectedPhysicalLoad <= this.MAX_PHYSICAL_LOAD
      );
    }) || null;
  }

  private updateLoad(currentLoad: number, exerciseLoad: number): number {
    return Math.min(1, currentLoad + (exerciseLoad * (1 - currentLoad)));
  }

  private calculateRestPeriod(currentLoad: number): number {
    const baseRest = 60; // Base rest period in seconds
    return Math.round(baseRest * (1 + currentLoad));
  }

  private createRestExercise(): Exercise {
    return {
      id: 'rest',
      name: 'Active Recovery',
      neural_load: -0.1,
      physical_load: -0.1,
      duration: 60,
      type: 'flexibility'
    };
  }
}
