import React, { useState, useCallback } from 'react';
import { Camera, Upload, Video, AlertCircle } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';

const MediaUploadAnalysis = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [mediaType, setMediaType] = useState('image');
  const [analysisType, setAnalysisType] = useState('general');
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileSelect = useCallback((event) => {
    const file = event.target.files[0];
    if (file) {
      // Validate file size and type
      const isValid = validateFile(file, mediaType);
      if (isValid) {
        setSelectedFile(file);
        setError(null);
      }
    }
  }, [mediaType]);

  const validateFile = (file, type) => {
    const maxSize = type === 'image' ? 10 * 1024 * 1024 : 50 * 1024 * 1024;
    const validTypes = type === 'image' 
      ? ['image/jpeg', 'image/png']
      : ['video/mp4', 'video/quicktime'];

    if (file.size > maxSize) {
      setError(`File too large. Maximum size for ${type} is ${maxSize / (1024 * 1024)}MB`);
      return false;
    }

    if (!validTypes.includes(file.type)) {
      setError(`Invalid file type. Supported formats for ${type}: ${validTypes.join(', ')}`);
      return false;
    }

    return true;
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setLoading(true);
    setError(null);

    try {
      // Convert file to base64
      const base64Data = await fileToBase64(selectedFile);

      // Emit socket event for analysis
      window.socket.emit('analyze_media', {
        user_id: window.userId,
        media_type: mediaType,
        analysis_type: analysisType,
        media_data: base64Data
      });

      // Listen for response
      window.socket.once('analysis_complete', (response) => {
        setAnalysis(response.data);
        setLoading(false);
      });

      window.socket.once('error', (error) => {
        setError(error.message);
        setLoading(false);
      });

    } catch (err) {
      setError('Error processing file: ' + err.message);
      setLoading(false);
    }
  };

  const fileToBase64 = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result);
      reader.onerror = (error) => reject(error);
    });
  };

  return (
    <div className="w-full max-w-4xl mx-auto p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold mb-4">Hive Analysis</h2>
        
        {/* Media Type Selection */}
        <div className="flex gap-4 mb-4">
          <button
            onClick={() => setMediaType('image')}
            className={`flex items-center px-4 py-2 rounded ${
              mediaType === 'image' ? 'bg-blue-500 text-white' : 'bg-gray-200'
            }`}
          >
            <Camera className="mr-2 h-5 w-5" />
            Image
          </button>
          <button
            onClick={() => setMediaType('video')}
            className={`flex items-center px-4 py-2 rounded ${
              mediaType === 'video' ? 'bg-blue-500 text-white' : 'bg-gray-200'
            }`}
          >
            <Video className="mr-2 h-5 w-5" />
            Video
          </button>
        </div>

        {/* Analysis Type Selection */}
        <select
          value={analysisType}
          onChange={(e) => setAnalysisType(e.target.value)}
          className="w-full p-2 border rounded mb-4"
        >
          <option value="general">General Analysis</option>
          <option value="foraging">Foraging Analysis</option>
          <option value="health">Health Analysis</option>
          <option value="productivity">Productivity Analysis</option>
        </select>

        {/* File Upload */}
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
          <input
            type="file"
            accept={mediaType === 'image' ? 'image/*' : 'video/*'}
            onChange={handleFileSelect}
            className="hidden"
            id="media-upload"
          />
          <label
            htmlFor="media-upload"
            className="cursor-pointer flex flex-col items-center"
          >
            <Upload className="h-12 w-12 text-gray-400 mb-2" />
            <span className="text-sm text-gray-600">
              Click to upload {mediaType}
              {selectedFile && ` - ${selectedFile.name}`}
            </span>
          </label>
        </div>

        {/* Error Display */}
        {error && (
          <Alert variant="destructive" className="mt-4">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Upload Button */}
        <button
          onClick={handleUpload}
          disabled={!selectedFile || loading}
          className={`w-full mt-4 px-4 py-2 rounded ${
            !selectedFile || loading
              ? 'bg-gray-300 cursor-not-allowed'
              : 'bg-blue-500 text-white hover:bg-blue-600'
          }`}
        >
          {loading ? 'Analyzing...' : 'Analyze'}
        </button>
      </div>

      {/* Analysis Results */}
      {analysis && (
        <div className="mt-6 p-4 border rounded">
          <h3 className="text-xl font-semibold mb-2">Analysis Results</h3>
          <div className="whitespace-pre-wrap">{analysis.analysis}</div>
          <div className="mt-2 text-sm text-gray-500">
            Analyzed at: {new Date(analysis.timestamp).toLocaleString()}
          </div>
        </div>
      )}
    </div>
  );
};

export default MediaUploadAnalysis;