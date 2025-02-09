import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const DataVisualizer = ({ data = [] }) => {
  const [chartData, setChartData] = useState([]);
  const [metrics, setMetrics] = useState({});

  useEffect(() => {
    if (data.length > 0) {
      formatDataForVisualization(data);
    }
  }, [data]);

  const formatDataForVisualization = (rawData) => {
    const formatted = rawData.map(point => ({
      timestamp: new Date(point.timestamp).toLocaleDateString(),
      beeCount: point.bee_count || 0,
      activity: point.activity_level || 0,
      productivity: point.productivity || 0
    }));

    setChartData(formatted);

    // Calculate metrics
    setMetrics({
      averageBeeCount: calculateAverage(formatted, 'beeCount'),
      averageActivity: calculateAverage(formatted, 'activity'),
      productivityTrend: calculateTrend(formatted, 'productivity')
    });
  };

  const calculateAverage = (data, key) => {
    return (data.reduce((sum, item) => sum + item[key], 0) / data.length).toFixed(2);
  };

  const calculateTrend = (data, key) => {
    if (data.length < 2) return 'Insufficient data';
    
    const firstValue = data[0][key];
    const lastValue = data[data.length - 1][key];
    const change = ((lastValue - firstValue) / firstValue) * 100;
    
    if (change > 5) return 'Increasing';
    if (change < -5) return 'Decreasing';
    return 'Stable';
  };

  return (
    <div className="space-y-6">
      {/* Metrics Summary */}
      <div className="grid grid-cols-3 gap-4">
        {Object.entries(metrics).map(([key, value]) => (
          <div key={key} className="p-4 bg-gray-50 rounded-lg">
            <h3 className="text-sm font-medium text-gray-500">
              {key.replace(/([A-Z])/g, ' $1').trim()}
            </h3>
            <p className="text-2xl font-bold text-gray-900">{value}</p>
          </div>
        ))}
      </div>

      {/* Chart */}
      <div className="h-96 bg-white rounded-lg p-4">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="timestamp" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="beeCount" 
              stroke="#8884d8" 
              name="Bee Count" 
            />
            <Line 
              type="monotone" 
              dataKey="activity" 
              stroke="#82ca9d" 
              name="Activity Level" 
            />
            <Line 
              type="monotone" 
              dataKey="productivity" 
              stroke="#ffc658" 
              name="Productivity" 
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default DataVisualizer;