import { NextApiRequest, NextApiResponse } from 'next';
import { RecoveryOptimizer } from '../../../services/RecoveryOptimizer';
import { IntegratedMetrics } from '../../../types/metrics';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  try {
    const metrics: IntegratedMetrics = req.body;

    // Validate the incoming metrics
    if (!validateMetrics(metrics)) {
      return res.status(400).json({ message: 'Invalid metrics data' });
    }

    // Create recovery optimizer instance
    const optimizer = new RecoveryOptimizer(metrics);

    // Calculate optimal recovery plan
    const recoveryPlan = optimizer.calculateOptimalRecovery();

    // Return the recovery plan
    return res.status(200).json(recoveryPlan);
  } catch (error) {
    console.error('Error in recovery optimization:', error);
    return res.status(500).json({ message: 'Internal server error' });
  }
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

  // Check timestamp
  if (!(metrics.timestamp instanceof Date) && !Date.parse(metrics.timestamp)) {
    return false;
  }

  return true;
}
