# Media Analysis API Documentation

## Overview

The Media Analysis API allows farmers to submit images or videos of their beehives for automated analysis using advanced AI techniques.

## Endpoints

### 1. Analyze Media

**Event:** `analyze_media`

**Request Format:**

```json
{
    "user_id": "user123",
    "media_type": "image|video",
    "analysis_type": "general|foraging|health|productivity",
    "media_data": "base64_encoded_media_data"
}
```

**Response Format:**

```json
{
    "status": 200,
    "user_id": "user123",
    "data": {
        "success": true,
        "analysis": "Detailed analysis text",
        "timestamp": "2024-02-08T12:00:00Z",
        "type": "analysis_type"
    },
    "message_type": "image_analysis|video_analysis"
}
```

### 2. Start Media Upload

**Event:** `media_upload_start`

**Request Format:**

```json
{
    "user_id": "user123",
    "media_type": "image|video",
    "file_size": 1048576
}
```

**Response Format:**

```json
{
    "status": 200,
    "session_id": "unique_session_id",
    "max_chunk_size": 1048576
}
```

### 3. Upload Media Chunk

**Event:** `media_upload_chunk`

**Request Format:**

```json
{
    "session_id": "unique_session_id",
    "chunk_number": 0,
    "total_chunks": 10,
    "chunk_data": "base64_encoded_chunk_data"
}
```

**Response Format:**

```json
{
    "status": 200,
    "session_id": "unique_session_id",
    "chunk_number": 0
}
```

## Analysis Types

1. **General Analysis**
   - Overall assessment of visible conditions
   - Identification of issues
   - General recommendations

2. **Foraging Analysis**
   - Assessment of foraging patterns
   - Evaluation of food sources
   - Foraging efficiency recommendations

3. **Health Analysis**
   - Disease and pest detection
   - Hive condition assessment
   - Health management recommendations

4. **Productivity Analysis**
   - Hive strength evaluation
   - Honey production indicators
   - Productivity improvement suggestions

## Media Guidelines

### Images

- Supported formats: JPG, PNG
- Maximum file size: 10MB
- Recommended resolution: 1920x1080 or higher
- Best practices:
  - Ensure good lighting
  - Capture multiple angles of the hive
  - Include surrounding environment
  - Avoid motion blur

### Videos

- Supported formats: MP4, MOV
- Maximum file size: 50MB
- Maximum duration: 2 minutes
- Recommended resolution: 1080p
- Best practices:
  - Hold camera steady
  - Pan slowly around hive
  - Include close-ups of important details
  - Capture bee activity patterns
  - Record during peak foraging hours

## Error Handling

Error responses follow this format:

```json
{
    "status": error_code,
    "message": "Error description",
    "type": "ErrorType"
}
```

Common error types:

- ValidationError: Invalid input parameters
- AnalysisError: Problems during media analysis
- ServerError: Internal server issues
- AuthorizationError: Authentication problems

## Rate Limiting

- Maximum 10 media analyses per hour per user
- Maximum 100MB total upload per day
- Larger uploads require special authorization
