import React from 'react';
import { Card } from '../ui/card';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface ProgressData {
  labels: string[];
  neural: number[];
  physical: number[];
  predictions?: {
    neural: number[];
    physical: number[];
  };
}

interface ProgressChartProps {
  data: ProgressData;
  title: string;
  showPredictions?: boolean;
}

export function ProgressChart({
  data,
  title,
  showPredictions = false
}: ProgressChartProps) {
  const chartData = {
    labels: data.labels,
    datasets: [
      {
        label: 'Neural Progress',
        data: data.neural,
        borderColor: 'rgb(183, 245, 1)',
        backgroundColor: 'rgba(183, 245, 1, 0.1)',
        fill: true,
        tension: 0.4
      },
      {
        label: 'Physical Progress',
        data: data.physical,
        borderColor: 'rgb(0, 209, 255)',
        backgroundColor: 'rgba(0, 209, 255, 0.1)',
        fill: true,
        tension: 0.4
      },
      ...(showPredictions && data.predictions
        ? [
            {
              label: 'Neural Prediction',
              data: [...Array(data.neural.length - 1).fill(null),
                     data.neural[data.neural.length - 1],
                     ...data.predictions.neural],
              borderColor: 'rgba(183, 245, 1, 0.5)',
              borderDash: [5, 5],
              fill: false,
              tension: 0.4
            },
            {
              label: 'Physical Prediction',
              data: [...Array(data.physical.length - 1).fill(null),
                     data.physical[data.physical.length - 1],
                     ...data.predictions.physical],
              borderColor: 'rgba(0, 209, 255, 0.5)',
              borderDash: [5, 5],
              fill: false,
              tension: 0.4
            }
          ]
        : [])
    ]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          color: 'rgb(255, 255, 255)',
          font: {
            family: 'system-ui'
          }
        }
      },
      title: {
        display: true,
        text: title,
        color: 'rgb(255, 255, 255)',
        font: {
          size: 16,
          family: 'system-ui'
        }
      },
      tooltip: {
        mode: 'index',
        intersect: false,
        backgroundColor: 'rgba(26, 26, 26, 0.9)',
        titleColor: 'rgb(255, 255, 255)',
        bodyColor: 'rgb(255, 255, 255)',
        borderColor: 'rgb(42, 42, 42)',
        borderWidth: 1
      }
    },
    scales: {
      x: {
        grid: {
          color: 'rgba(255, 255, 255, 0.1)'
        },
        ticks: {
          color: 'rgb(160, 160, 160)'
        }
      },
      y: {
        grid: {
          color: 'rgba(255, 255, 255, 0.1)'
        },
        ticks: {
          color: 'rgb(160, 160, 160)'
        },
        min: 0,
        max: 100
      }
    },
    interaction: {
      mode: 'nearest',
      axis: 'x',
      intersect: false
    }
  };

  return (
    <Card className="p-6">
      <div className="h-[400px]">
        <Line data={chartData} options={options} />
      </div>
    </Card>
  );
}
