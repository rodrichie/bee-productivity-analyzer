import React, { useState, useCallback } from 'react';
import { Upload, Camera, Video } from 'lucide-react';

const MediaAnalyzer = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState(null);

  // Socket event listeners
  React.useEffect(() => {
    window.socket.on('analysis_complete', (response) => {
      setAnalysis(response.data);
      setAnalyzing(false);
    });

    window.socket.on('error', (error) => {
      setError(error.message);
      setAnalyzing(false);
    });

    return () => {
      window.socket.off('analysis_complete');
      window.socket.off('error');
    };
  }, []);

  const handleFileSelect = useCallback((event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      setError(null);
    }
  }, []);

  const handleUpload = async () => {
    if (!selectedFile) return;
    setAnalyzing(true);
    setError(null);

    try {
      // Convert file to base64
      const reader = new FileReader();
      reader.onloadend = () => {
        // Emit socket event for analysis
        window.socket.emit('analyze_media', {
          user_id: window.userId,
          media_type: selectedFile.type.startsWith('image/') ? 'image' : 'video',
          media_data: reader.result
        });
      };
      reader.readAsDataURL(selectedFile);
    } catch (error) {
      setError('Error processing file');
      setAnalyzing(false);
    }
  };

  const renderAnalysisResults = () => {
    if (!analysis) return null;

    return (
      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Analysis Results</h3>
        
        {/* Bee Activity Section */}
        <div className="bg-white p-4 rounded-lg shadow">
          <h4 className="font-medium mb-2">Bee Activity</h4>
          <dl className="grid grid-cols-2 gap-4">
            <div>
              <dt className="text-sm text-gray-500">Bee Count</dt>
              <dd className="text-lg font-medium">{analysis.bee_count || 'N/A'}</dd>
            </div>
            <div>
              <dt className="text-sm text-gray-500">Activity Level</dt>
              <dd className="text-lg font-medium">{analysis.activity_level || 'N/A'}</dd>
            </div>
          </dl>
        </div>

        {/* Foraging Analysis */}
        <div className="bg-white p-4 rounded-lg shadow">
          <h4 className="font-medium mb-2">Foraging Analysis</h4>
          <div className="space-y-2">
            {analysis.foraging_patterns?.map((pattern, index) => (
              <div key={index} className="text-sm">
                {pattern}
              </div>
            ))}
          </div>
        </div>

        {/* Recommendations */}
        <div className="bg-white p-4 rounded-lg shadow">
          <h4 className="font-medium mb-2">Recommendations</h4>
          <ul className="list-disc list-inside space-y-1">
            {analysis.recommendations?.map((rec, index) => (
              <li key={index} className="text-sm">
                {rec}
              </li>
            ))}
          </ul>
        </div>

        {/* Environmental Conditions */}
        {analysis.environmental_conditions && (
          <div className="bg-white p-4 rounded-lg shadow">
            <h4 className="font-medium mb-2">Environmental Conditions</h4>
            <dl className="grid grid-cols-2 gap-4">
              <div>
                <dt className="text-sm text-gray-500">Temperature</dt>
                <dd className="text-lg font-medium">
                  {analysis.environmental_conditions.temperature}°C
                </dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500">Humidity</dt>
                <dd className="text-lg font-medium">
                  {analysis.environmental_conditions.humidity}%
                </dd>
              </div>
            </dl>
          </div>
        )}

        {/* Alerts */}
        {analysis.alerts && analysis.alerts.length > 0 && (
          <div className="bg-yellow-50 p-4 rounded-lg">
            <h4 className="font-medium mb-2 text-yellow-800">Alerts</h4>
            <ul className="list-disc list-inside space-y-1">
              {analysis.alerts.map((alert, index) => (
                <li key={index} className="text-sm text-yellow-700">
                  {alert}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* File Upload Section */}
      <div className="border-2 border-dashed border-gray-300 rounded-lg p-6">
        <div className="flex justify-center mb-4">
          <div className="space-x-4">
            <label className="inline-flex items-center px-4 py-2 bg-white border rounded-md cursor-pointer hover:bg-gray-50">
              <Camera className="w-5 h-5 mr-2" />
              <span>Take Photo</span>
              <input
                type="file"
                accept="image/*"
                capture="environment"
                className="hidden"
                onChange={handleFileSelect}
              />
            </label>
            <label className="inline-flex items-center px-4 py-2 bg-white border rounded-md cursor-pointer hover:bg-gray-50">
              <Video className="w-5 h-5 mr-2" />
              <span>Record Video</span>
              <input
                type="file"
                accept="video/*"
                capture="environment"
                className="hidden"
                onChange={handleFileSelect}
              />
            </label>
            <label className="inline-flex items-center px-4 py-2 bg-white border rounded-md cursor-pointer hover:bg-gray-50">
              <Upload className="w-5 h-5 mr-2" />
              <span>Upload File</span>
              <input
                type="file"
                accept="image/*,video/*"
                className="hidden"
                onChange={handleFileSelect}
              />
            </label>
          </div>
        </div>
        
        {selectedFile && (
          <div className="text-center text-sm text-gray-600">
            Selected: {selectedFile.name}
          </div>
        )}
      </div>

      {/* Analysis Button */}
      <button
        onClick={handleUpload}
        disabled={!selectedFile || analyzing}
        className={`w-full px-4 py-2 rounded ${
          !selectedFile || analyzing
            ? 'bg-gray-300 cursor-not-allowed'
            : 'bg-blue-500 text-white hover:bg-blue-600'
        }`}
      >
        {analyzing ? 'Analyzing...' : 'Analyze'}
      </button>

      {/* Error Display */}
      {error && (
        <div className="p-4 bg-red-50 text-red-700 rounded-md">
          {error}
        </div>
      )}

      {/* Analysis Results */}
      {renderAnalysisResults()}
    </div>
  );
};

export default MediaAnalyzer;