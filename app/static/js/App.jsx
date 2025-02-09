import React from 'react';
import BeekeepingAnalyzer from './components/BeekeepingAnalyzer';

const App = () => {
  return (
    <div className="min-h-screen bg-gray-100 py-6">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Bee Productivity Analyzer
          </h1>
          <p className="mt-2 text-sm text-gray-600">
            Analyze bee foraging patterns and hive productivity
          </p>
        </div>
        <BeekeepingAnalyzer />
      </div>
    </div>
  );
};

export default App;