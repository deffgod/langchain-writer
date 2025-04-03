import { NextApiRequest, NextApiResponse } from 'next';
import { CognitiveLoadManager, Exercise } from '../../../services/CognitiveLoadManager';
import { IntegratedMetrics } from '../../../types/metrics';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  try {
    const { metrics, exercises, currentLoad, targetLoad } = req.body;

    // Validate request data
    if (!validateRequest(metrics, exercises, currentLoad, targetLoad)) {
      return res.status(400).json({ message: 'Invalid request data' });
    }

    // Create cognitive load manager
    const loadManager = new CognitiveLoadManager(metrics);

    // Process optimization based on request type
    const result = processOptimization(loadManager, exercises, currentLoad, targetLoad);

    return res.status(200).json(result);
  } catch (error) {
    console.error('Error in cognitive load optimization:', error);
    return res.status(500).json({ message: 'Internal server error' });
  }
}

function validateRequest(
  metrics: any,
  exercises: any,
  currentLoad: any,
  targetLoad: any
): boolean {
  // Validate metrics
  if (!metrics || !validateMetrics(metrics)) {
    return false;
  }

  // Validate exercises array
  if (!Array.isArray(exercises) || !exercises.every(validateExercise)) {
    return false;
  }

  // Validate load values
  if (
    typeof currentLoad !== 'number' ||
    typeof targetLoad !== 'number' ||
    currentLoad < 0 ||
    currentLoad > 1 ||
    targetLoad < 0 ||
    targetLoad > 1
  ) {
    return false;
  }

  return true;
}

function validateMetrics(metrics: any): metrics is IntegratedMetrics {
  if (!metrics) return false;

  // Check for required top-level properties
  if (!metrics.neural || !metrics.physical || typeof metrics.sync_score !== 'number') {
    return false;
  }

  // Check neural metrics
  const { neural } = metrics;
  if (!neural.vision || !neural.balance || !neural.coordination) {
    return false;
  }

  // Check physical metrics
  const { physical } = metrics;
  if (!physical.performance || !physical.recovery || !physical.progression) {
    return false;
  }

  return true;
}

function validateExercise(exercise: any): exercise is Exercise {
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

function processOptimization(
  loadManager: CognitiveLoadManager,
  exercises: Exercise[],
  currentLoad: number,
  targetLoad: number
) {
  // Calculate total load
  const totalLoad = loadManager.calculateTotalLoad(
    exercises.reduce((sum, ex) => sum + ex.neural_load, 0),
    exercises.reduce((sum, ex) => sum + ex.physical_load, 0)
  );

  // Optimize exercise sequence
  const optimizedSequence = loadManager.optimizeExerciseSequence(exercises);

  // Calculate intensity adjustments
  const adjustments = loadManager.adjustIntensity(currentLoad, targetLoad);

  return {
    total_load: totalLoad,
    optimized_sequence: optimizedSequence,
    adjustments: adjustments
  };
}
