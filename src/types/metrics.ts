export interface VisionMetrics {
  right_eye: string;
  left_eye_mobility: string;
  binocular: string;
  focus_score: number;
  tracking_score: number;
}

export interface BalanceMetrics {
  static_balance: number;
  dynamic_balance: number;
  vestibular_score: number;
}

export interface CoordinationMetrics {
  hand_eye: number;
  spatial_awareness: number;
  reaction_time: number;
}

export interface PerformanceMetrics {
  strength: number;
  endurance: number;
  flexibility: number;
  power: number;
}

export interface RecoveryMetrics {
  fatigue_level: number;
  sleep_quality: number;
  muscle_soreness: number;
  stress_level: number;
}

export interface ProgressionMetrics {
  neural_adaptation: number;
  physical_adaptation: number;
  skill_acquisition: number;
}

export interface IntegratedMetrics {
  neural: {
    vision: VisionMetrics;
    balance: BalanceMetrics;
    coordination: CoordinationMetrics;
  };
  physical: {
    performance: PerformanceMetrics;
    recovery: RecoveryMetrics;
    progression: ProgressionMetrics;
  };
  sync_score: number;
  timestamp: Date;
}
