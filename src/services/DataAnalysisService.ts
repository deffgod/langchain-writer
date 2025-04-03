import { IntegratedMetrics } from '../types/metrics';
import { Exercise } from './CognitiveLoadManager';

interface MetricsAggregation {
  average_neural_load: number;
  average_physical_load: number;
  total_duration: number;
  exercise_type_distribution: Record<string, number>;
  improvement_trends: {
    neural: number;
    physical: number;
  };
}

interface TrendAnalysis {
  short_term: {
    neural: number;
    physical: number;
  };
  long_term: {
    neural: number;
    physical: number;
  };
  predictions: {
    next_week: {
      neural: number;
      physical: number;
    };
  };
}

export class DataAnalysisService {
  private readonly TREND_WINDOW_SHORT = 7; // 7 days
  private readonly TREND_WINDOW_LONG = 30; // 30 days
  private readonly IMPROVEMENT_THRESHOLD = 0.05; // 5% improvement threshold

  constructor(private readonly metricsHistory: IntegratedMetrics[]) {}

  public analyzeMetrics(
    currentMetrics: IntegratedMetrics,
    exercises: Exercise[]
  ): MetricsAggregation {
    return {
      average_neural_load: this.calculateAverageNeuralLoad(exercises),
      average_physical_load: this.calculateAveragePhysicalLoad(exercises),
      total_duration: this.calculateTotalDuration(exercises),
      exercise_type_distribution: this.calculateTypeDistribution(exercises),
      improvement_trends: this.calculateImprovementTrends(currentMetrics)
    };
  }

  public analyzeTrends(): TrendAnalysis {
    return {
      short_term: this.calculateShortTermTrends(),
      long_term: this.calculateLongTermTrends(),
      predictions: {
        next_week: this.predictNextWeek()
      }
    };
  }

  private calculateAverageNeuralLoad(exercises: Exercise[]): number {
    if (exercises.length === 0) return 0;
    return exercises.reduce((sum, ex) => sum + ex.neural_load, 0) / exercises.length;
  }

  private calculateAveragePhysicalLoad(exercises: Exercise[]): number {
    if (exercises.length === 0) return 0;
    return exercises.reduce((sum, ex) => sum + ex.physical_load, 0) / exercises.length;
  }

  private calculateTotalDuration(exercises: Exercise[]): number {
    return exercises.reduce((sum, ex) => sum + ex.duration, 0);
  }

  private calculateTypeDistribution(exercises: Exercise[]): Record<string, number> {
    const distribution: Record<string, number> = {};
    exercises.forEach(ex => {
      distribution[ex.type] = (distribution[ex.type] || 0) + 1;
    });
    return distribution;
  }

  private calculateImprovementTrends(
    currentMetrics: IntegratedMetrics
  ): { neural: number; physical: number } {
    if (this.metricsHistory.length < 2) {
      return { neural: 0, physical: 0 };
    }

    const previousMetrics = this.metricsHistory[this.metricsHistory.length - 2];

    return {
      neural: this.calculateNeuralImprovement(currentMetrics, previousMetrics),
      physical: this.calculatePhysicalImprovement(currentMetrics, previousMetrics)
    };
  }

  private calculateShortTermTrends(): { neural: number; physical: number } {
    const recentMetrics = this.metricsHistory.slice(-this.TREND_WINDOW_SHORT);
    return this.calculateTrendSlope(recentMetrics);
  }

  private calculateLongTermTrends(): { neural: number; physical: number } {
    const longTermMetrics = this.metricsHistory.slice(-this.TREND_WINDOW_LONG);
    return this.calculateTrendSlope(longTermMetrics);
  }

  private predictNextWeek(): { neural: number; physical: number } {
    const recentTrends = this.calculateShortTermTrends();
    const currentMetrics = this.metricsHistory[this.metricsHistory.length - 1];

    return {
      neural: this.predictMetric(currentMetrics.neural, recentTrends.neural),
      physical: this.predictMetric(currentMetrics.physical, recentTrends.physical)
    };
  }

  private calculateTrendSlope(
    metrics: IntegratedMetrics[]
  ): { neural: number; physical: number } {
    if (metrics.length < 2) {
      return { neural: 0, physical: 0 };
    }

    const neuralValues = metrics.map(m => this.aggregateNeuralMetrics(m));
    const physicalValues = metrics.map(m => this.aggregatePhysicalMetrics(m));

    return {
      neural: this.calculateSlope(neuralValues),
      physical: this.calculateSlope(physicalValues)
    };
  }

  private calculateSlope(values: number[]): number {
    if (values.length < 2) return 0;

    const xMean = (values.length - 1) / 2;
    const yMean = values.reduce((a, b) => a + b) / values.length;

    const numerator = values.reduce((sum, y, x) => {
      return sum + (x - xMean) * (y - yMean);
    }, 0);

    const denominator = values.reduce((sum, _, x) => {
      return sum + Math.pow(x - xMean, 2);
    }, 0);

    return denominator === 0 ? 0 : numerator / denominator;
  }

  private predictMetric(currentValue: number, trend: number): number {
    return Math.max(0, Math.min(1, currentValue + trend * 7)); // 7 days projection
  }

  private aggregateNeuralMetrics(metrics: IntegratedMetrics): number {
    const { vision, balance, coordination } = metrics.neural;
    return (
      (vision.focus_score / 100) * 0.4 +
      (balance.vestibular_score / 100) * 0.3 +
      ((100 - coordination.reaction_time) / 100) * 0.3
    );
  }

  private aggregatePhysicalMetrics(metrics: IntegratedMetrics): number {
    const { performance, recovery } = metrics.physical;
    return (
      (performance.endurance / 100) * 0.4 +
      ((100 - recovery.fatigue_level) / 100) * 0.3 +
      ((100 - recovery.muscle_soreness) / 100) * 0.3
    );
  }

  private calculateNeuralImprovement(
    current: IntegratedMetrics,
    previous: IntegratedMetrics
  ): number {
    const currentScore = this.aggregateNeuralMetrics(current);
    const previousScore = this.aggregateNeuralMetrics(previous);
    return this.calculateImprovement(currentScore, previousScore);
  }

  private calculatePhysicalImprovement(
    current: IntegratedMetrics,
    previous: IntegratedMetrics
  ): number {
    const currentScore = this.aggregatePhysicalMetrics(current);
    const previousScore = this.aggregatePhysicalMetrics(previous);
    return this.calculateImprovement(currentScore, previousScore);
  }

  private calculateImprovement(current: number, previous: number): number {
    const improvement = (current - previous) / previous;
    return improvement > this.IMPROVEMENT_THRESHOLD ? improvement : 0;
  }
}
