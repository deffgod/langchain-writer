import { NextApiRequest, NextApiResponse } from 'next';
import { PersonalizationEngine } from '../../../services/PersonalizationEngine';
import { Exercise } from '../../../services/CognitiveLoadManager';
import { IntegratedMetrics } from '../../../types/metrics';

interface PersonalizationRequest {
  user_id: string;
  profile: {
    preferences: {
      preferred_exercise_types: string[];
      avoided_exercise_types: string[];
      optimal_session_duration: number;
      preferred_time_of_day: string;
      recovery_needs: {
        neural: number;
        physical: number;
      };
    };
    learning_patterns: Array<{
      exercise_type: string;
      improvement_rate: number;
      consistency: number;
      optimal_frequency: number;
      optimal_intensity: number;
    }>;
    adaptation_history: Array<{
      timestamp: Date;
      metrics: IntegratedMetrics;
      adjustments: any;
    }>;
  };
  current_metrics: IntegratedMetrics;
  exercises: Exercise[];
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  try {
    const {
      user_id,
      profile,
      current_metrics,
      exercises
    } = req.body as PersonalizationRequest;

    // Validate request data
    if (!validateRequest(req.body)) {
      return res.status(400).json({ message: 'Invalid request data' });
    }

    // Create personalization engine
    const engine = new PersonalizationEngine(
      { user_id, ...profile },
      current_metrics
    );

    // Generate personalized plan
    const personalizedExercises = engine.generatePersonalizedPlan(exercises);

    // Return personalized plan
    return res.status(200).json({
      personalized_exercises: personalizedExercises,
      user_id,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('Error in personalization:', error);
    return res.status(500).json({ message: 'Internal server error' });
  }
}

function validateRequest(data: any): data is PersonalizationRequest {
  if (!data || typeof data !== 'object') return false;

  // Check required top-level properties
  if (
    !data.user_id ||
    !data.profile ||
    !data.current_metrics ||
    !Array.isArray(data.exercises)
  ) {
    return false;
  }

  // Validate profile structure
  const { profile } = data;
  if (
    !profile.preferences ||
    !Array.isArray(profile.learning_patterns) ||
    !Array.isArray(profile.adaptation_history)
  ) {
    return false;
  }

  // Validate preferences
  const { preferences } = profile;
  if (
    !Array.isArray(preferences.preferred_exercise_types) ||
    !Array.isArray(preferences.avoided_exercise_types) ||
    typeof preferences.optimal_session_duration !== 'number' ||
    typeof preferences.preferred_time_of_day !== 'string' ||
    !preferences.recovery_needs ||
    typeof preferences.recovery_needs.neural !== 'number' ||
    typeof preferences.recovery_needs.physical !== 'number'
  ) {
    return false;
  }

  // Validate learning patterns
  if (!profile.learning_patterns.every(validateLearningPattern)) {
    return false;
  }

  // Validate exercises
  if (!data.exercises.every(validateExercise)) {
    return false;
  }

  return true;
}

function validateLearningPattern(pattern: any): boolean {
  return (
    typeof pattern === 'object' &&
    typeof pattern.exercise_type === 'string' &&
    typeof pattern.improvement_rate === 'number' &&
    typeof pattern.consistency === 'number' &&
    typeof pattern.optimal_frequency === 'number' &&
    typeof pattern.optimal_intensity === 'number'
  );
}

function validateExercise(exercise: any): boolean {
  return (
    typeof exercise === 'object' &&
    typeof exercise.id === 'string' &&
    typeof exercise.name === 'string' &&
    typeof exercise.neural_load === 'number' &&
    typeof exercise.physical_load === 'number' &&
    typeof exercise.duration === 'number' &&
    ['vision', 'balance', 'coordination', 'strength', 'endurance', 'flexibility'].includes(exercise.type)
  );
}
