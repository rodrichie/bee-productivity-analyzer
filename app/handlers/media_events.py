from flask_socketio import emit
from app.models.media_analyzer import MediaAnalyzer
from app.utils.auth import require_token
import base64
from datetime import datetime
import os

media_analyzer = MediaAnalyzer()

def register_media_events(socketio):
    @socketio.on('analyze_media')
    @require_token
    def handle_media_analysis(data):
        """Handle incoming media analysis requests"""
        try:
            user_id = data.get('user_id')
            media_type = data.get('media_type')  # 'image' or 'video'
            analysis_type = data.get('analysis_type', 'general')
            media_data = data.get('media_data')  # base64 encoded media
            
            if not all([user_id, media_type, media_data]):
                emit('error', {
                    'status': 400,
                    'message': 'Missing required parameters',
                    'type': 'ValidationError'
                })
                return
            
            # Decode media data
            try:
                media_bytes = base64.b64decode(media_data.split(',')[1])
            except:
                emit('error', {
                    'status': 400,
                    'message': 'Invalid media data format',
                    'type': 'ValidationError'
                })
                return
            
            # Process based on media type
            if media_type == 'image':
                result = media_analyzer.analyze_image(media_bytes, analysis_type)
            elif media_type == 'video':
                result = media_analyzer.analyze_video(media_bytes, analysis_type)
            else:
                emit('error', {
                    'status': 400,
                    'message': 'Invalid media type',
                    'type': 'ValidationError'
                })
                return
            
            if result['success']:
                emit('analysis_complete', {
                    'status': 200,
                    'user_id': user_id,
                    'data': result,
                    'message_type': f'{media_type}_analysis'
                })
            else:
                emit('error', {
                    'status': 500,
                    'message': f'Analysis failed: {result.get("error", "Unknown error")}',
                    'type': 'AnalysisError'
                })
                
        except Exception as e:
            emit('error', {
                'status': 500,
                'message': f'Error processing media: {str(e)}',
                'type': 'ServerError'
            })

    @socketio.on('media_upload_start')
    @require_token
    def handle_upload_start(data):
        """Handle the start of a media upload session"""
        try:
            user_id = data.get('user_id')
            media_type = data.get('media_type')
            file_size = data.get('file_size')
            
            # Validate file size (e.g., 50MB limit)
            if file_size > 50 * 1024 * 1024:
                emit('error', {
                    'status': 400,
                    'message': 'File too large. Maximum size is 50MB',
                    'type': 'ValidationError'
                })
                return
            
            # Generate upload session ID
            session_id = f"{user_id}_{datetime.now().timestamp()}"
            
            emit('upload_ready', {
                'status': 200,
                'session_id': session_id,
                'max_chunk_size': 1024 * 1024  # 1MB chunks
            })
            
        except Exception as e:
            emit('error', {
                'status': 500,
                'message': f'Error initiating upload: {str(e)}',
                'type': 'ServerError'
            })

    @socketio.on('media_upload_chunk')
    @require_token
    def handle_upload_chunk(data):
        """Handle incoming media chunks for large files"""
        try:
            session_id = data.get('session_id')
            chunk_number = data.get('chunk_number')
            total_chunks = data.get('total_chunks')
            chunk_data = data.get('chunk_data')
            
            # Process chunk
            # ... (implement chunk processing logic)
            
            # If last chunk, trigger analysis
            if chunk_number == total_chunks - 1:
                # Combine chunks and analyze
                # ... (implement chunk combination and analysis)
                pass
            
            emit('chunk_received', {
                'status': 200,
                'session_id': session_id,
                'chunk_number': chunk_number
            })
            
        except Exception as e:
            emit('error', {
                'status': 500,
                'message': f'Error processing chunk: {str(e)}',
                'type': 'ServerError'
            })