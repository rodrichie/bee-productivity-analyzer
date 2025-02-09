import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';

const BeeAnalyticsVisualizer = ({ data, analysisType }) => {
  const [chartData, setChartData] = useState([]);
  const [metrics, setMetrics] = useState({});
  const [error, setError] = useState(null);

  useEffect(() => {
    try {
      formatDataForVisualization(data, analysisType);
    } catch (err) {
      setError('Error processing data for visualization');
    }
  }, [data, analysisType]);

  const formatDataForVisualization = (rawData, type) => {
    switch (type) {
      case 'activity':
        setChartData(formatActivityData(rawData));
        break;
      case 'productivity':
        setChartData(formatProductivityData(rawData));
        break;
      case 'environmental':
        setChartData(formatEnvironmentalData(rawData));
        break;
      default:
        setChartData([]);
    }
  };

  const renderMetricsSummary = () => {
    return (
      <div className="grid grid-cols-3 gap-4 mb-6">
        {Object.entries(metrics).map(([key, value]) => (
          <div key={key} className="p-4 bg-white rounded-lg shadow">
            <h3 className="text-lg font-semibold text-gray-700">{key}</h3>
            <p className="text-2xl font-bold text-blue-600">{value}</p>
          </div>
        ))}
      </div>
    );
  };

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertTitle>Error</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="w-full max-w-6xl mx-auto p-6">
      {Object.keys(metrics).length > 0 && renderMetricsSummary()}
      
      <div className="h-96 bg-white rounded-lg shadow p-4">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="timestamp" />
            <YAxis />
            <Tooltip />
            <Legend />
            {renderChartLines()}
          </LineChart>
        </ResponsiveContainer>
      </div>
      
      {renderAnalysisSummary()}
    </div>
  );

  function formatActivityData(rawData) {
    const formattedData = rawData.map(point => ({
      timestamp: new Date(point.timestamp).toLocaleDateString(),
      beeCount: point.bee_count,
      activityLevel: point.activity_level,
      foraging: point.foraging_rate
    }));

    setMetrics({
      'Average Bee Count': Math.round(
        formattedData.reduce((acc, curr) => acc + curr.beeCount, 0) / formattedData.length
      ),
      'Peak Activity': Math.max(...formattedData.map(d => d.beeCount)),
      'Activity Trend': calculateTrend(formattedData.map(d => d.beeCount))
    });

    return formattedData;
  }

  function formatProductivityData(rawData) {
    const formattedData = rawData.map(point => ({
      timestamp: new Date(point.timestamp).toLocaleDateString(),
      honeyYield: point.honey_yield,
      efficiency: point.efficiency_rate
    }));

    setMetrics({
      'Total Yield': formattedData.reduce((acc, curr) => acc + curr.honeyYield, 0).toFixed(2),
      'Average Efficiency': (
        formattedData.reduce((acc, curr) => acc + curr.efficiency, 0) / formattedData.length
      ).toFixed(2),
      'Yield Trend': calculateTrend(formattedData.map(d => d.honeyYield))
    });

    return formattedData;
  }

  function formatEnvironmentalData(rawData) {
    const formattedData = rawData.map(point => ({
      timestamp: new Date(point.timestamp).toLocaleDateString(),
      temperature: point.temperature,
      humidity: point.humidity,
      rainfall: point.rainfall
    }));

    setMetrics({
      'Avg Temperature': (
        formattedData.reduce((acc, curr) => acc + curr.temperature, 0) / formattedData.length
      ).toFixed(1),
      'Avg Humidity': (
        formattedData.reduce((acc, curr) => acc + curr.humidity, 0) / formattedData.length
      ).toFixed(1),
      'Total Rainfall': formattedData.reduce((acc, curr) => acc + curr.rainfall, 0).toFixed(1)
    });

    return formattedData;
  }

  function calculateTrend(values) {
    const n = values.length;
    if (n < 2) return 'Insufficient Data';
    
    const lastAvg = values.slice(-3).reduce((a, b) => a + b, 0) / 3;
    const firstAvg = values.slice(0, 3).reduce((a, b) => a + b, 0) / 3;
    
    const percentChange = ((lastAvg - firstAvg) / firstAvg) * 100;
    
    if (percentChange > 5) return 'Increasing';
    if (percentChange < -5) return 'Decreasing';
    return 'Stable';
  }

  function renderChartLines() {
    // Render appropriate lines based on analysis type
    switch (analysisType) {
      case 'activity':
        return [
          <Line type="monotone" dataKey="beeCount" stroke="#8884d8" name="Bee Count" />,
          <Line type="monotone" dataKey="activityLevel" stroke="#82ca9d" name="Activity Level" />,
          <Line type="monotone" dataKey="foraging" stroke="#ffc658" name="Foraging Rate" />
        ];
      case 'productivity':
        return [
          <Line type="monotone" dataKey="honeyYield" stroke="#8884d8" name="Honey Yield" />,
          <Line type="monotone" dataKey="efficiency" stroke="#82ca9d" name="Efficiency" />
        ];
      case 'environmental':
        return [
          <Line type="monotone" dataKey="temperature" stroke="#8884d8" name="Temperature" />,
          <Line type="monotone" dataKey="humidity" stroke="#82ca9d" name="Humidity" />,
          <Line type="monotone" dataKey="rainfall" stroke="#ffc658" name="Rainfall" />
        ];
      default:
        return null;
    }
  }

  function renderAnalysisSummary() {
    if (chartData.length === 0) return null;

    return (
      <div className="mt-6 p-4 bg-white rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-2">Analysis Summary</h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <h4 className="font-medium">Trends</h4>
            <ul className="list-disc list-inside">
              {Object.entries(metrics).map(([key, value]) => (
                <li key={key}>{`${key}: ${value}`}</li>
              ))}
            </ul>
          </div>
          <div>
            <h4 className="font-medium">Recommendations</h4>
            <ul className="list-disc list-inside">
              {generateRecommendations().map((rec, index) => (
                <li key={index}>{rec}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    );
  }

  function generateRecommendations() {
    // Generate recommendations based on metrics and trends
    const recommendations = [];
    
    if (analysisType === 'activity') {
      const avgBeeCount = metrics['Average Bee Count'];
      const trend = metrics['Activity Trend'];
      
      if (avgBeeCount < 20) {
        recommendations.push('Consider supplementary feeding to boost activity');
      }
      if (trend === 'Decreasing') {
        recommendations.push('Investigate potential causes of declining activity');
      }
    }
    
    // Add more recommendation logic for other analysis types
    
    return recommendations;
  }
};

export default BeeAnalyticsVisualizer;