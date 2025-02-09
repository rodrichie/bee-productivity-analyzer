from flask_socketio import emit, disconnect
from flask import request
import logging
import json
from typing import Dict, Any
import os

from app.models import bee_classifier, gemini_handler
from app.models.media_analyzer import MediaAnalyzer
from app.utils.auth import require_token
from app.utils.rate_limiter import rate_limiter

# Initialize logger
logger = logging.getLogger(__name__)

# Store user sessions and connections
user_sessions = {}
connection_to_user = {}

# Initialize media analyzer
media_analyzer = MediaAnalyzer()

def register_socket_events(socketio):
    @socketio.on('connect')
    @require_token
    def handle_connect():
        """Handle new client connections"""
        try:
            user_id = request.args.get('user_id')
            
            if not user_id:
                emit('error', {
                    'status': 400,
                    'message': 'User ID is required',
                    'type': 'ValidationError'
                })
                disconnect()
                return False

            connection_id = request.sid
            connection_to_user[connection_id] = user_id
            
            logger.info(f'User connected: {user_id} with connection ID: {connection_id}')

            # Initialize user session
            user_sessions[user_id] = {
                "history": [],
                "connection_id": connection_id,
                "current_context": {}
            }

            emit('connected', {
                'status': 200,
                'message': 'Connected to BeekeepingBot!',
                'user_id': user_id
            })
            
        except Exception as e:
            logger.error(f'Connection error: {str(e)}')
            emit('error', {
                'status': 500,
                'message': 'Internal server error during connection',
                'type': 'ServerError'
            })
            return False

    @socketio.on('message')
    @require_token
    def handle_message(data: Dict[str, Any]):
        """Handle incoming text messages and queries"""
        try:
            if isinstance(data, str):
                data = json.loads(data)

            message_user_id = data.get('user_id')
            user_input = data.get('message')
            connection_id = request.sid
            original_user_id = connection_to_user.get(connection_id)

            # Validate required fields
            if not all([message_user_id, user_input]):
                emit('error', {
                    'status': 400,
                    'message': 'Both user_id and message are required',
                    'type': 'ValidationError'
                })
                return

            # Verify user_id match
            if message_user_id != original_user_id:
                emit('error', {
                    'status': 403,
                    'message': 'User ID mismatch',
                    'type': 'AuthorizationError'
                })
                return

            # Check rate limit
            if not rate_limiter.is_allowed(message_user_id):
                emit('error', {
                    'status': 429,
                    'message': 'Rate limit exceeded. Please try again later.',
                    'type': 'RateLimitError'
                })
                return

            # Classify the query
            category, confidence = bee_classifier.classify_query(user_input)
            logger.info(f'Query classified as {category} with confidence {confidence}')

            # Get user context
            user_context = user_sessions[message_user_id].get('current_context', {})

            # Generate response based on category
            if category == 'analysis' and bee_classifier.is_image_analysis_required(user_input):
                emit('request_media', {
                    'status': 200,
                    'message': 'Please upload an image or video for analysis',
                    'type': 'media_request'
                })
                return

            # Generate response using Gemini
            response = gemini_handler.generate_response(user_input)

            # Update session history
            user_sessions[message_user_id]['history'].append({
                'query': user_input,
                'response': response,
                'category': category,
                'timestamp': str(datetime.now())
            })

            # Send response
            emit('response', {
                'status': 200,
                'user_id': message_user_id,
                'data': response,
                'category': category,
                'message_type': 'text_response'
            })

        except json.JSONDecodeError:
            emit('error', {
                'status': 400,
                'message': 'Invalid JSON format',
                'type': 'ValidationError'
            })
        except Exception as e:
            logger.error(f'Error processing message: {str(e)}', exc_info=True)
            emit('error', {
                'status': 500,
                'message': 'Internal server error',
                'type': 'ServerError'
            })

    @socketio.on('analyze_media')
    @require_token
    def handle_media_analysis(data: Dict[str, Any]):
        """Handle media analysis requests"""
        try:
            user_id = data.get('user_id')
            media_type = data.get('media_type')
            analysis_type = data.get('analysis_type', 'general')
            media_data = data.get('media_data')

            # Validate inputs
            if not all([user_id, media_type, media_data]):
                emit('error', {
                    'status': 400,
                    'message': 'Missing required parameters',
                    'type': 'ValidationError'
                })
                return

            # Check rate limit
            if not rate_limiter.is_allowed(user_id):
                emit('error', {
                    'status': 429,
                    'message': 'Rate limit exceeded',
                    'type': 'RateLimitError'
                })
                return

            # Process media
            if media_type == 'image':
                result = media_analyzer.analyze_image(media_data, analysis_type)
            elif media_type == 'video':
                result = media_analyzer.analyze_video(media_data, analysis_type)
            else:
                emit('error', {
                    'status': 400,
                    'message': 'Invalid media type',
                    'type': 'ValidationError'
                })
                return

            # Send analysis results
            emit('analysis_complete', {
                'status': 200,
                'user_id': user_id,
                'data': result,
                'message_type': f'{media_type}_analysis'
            })

        except Exception as e:
            logger.error(f'Media analysis error: {str(e)}', exc_info=True)
            emit('error', {
                'status': 500,
                'message': f'Error analyzing media: {str(e)}',
                'type': 'AnalysisError'
            })

    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnections"""
        connection_id = request.sid
        user_id = connection_to_user.get(connection_id)
        
        # Clean up session data
        if user_id:
            if user_id in user_sessions:
                del user_sessions[user_id]
            if connection_id in connection_to_user:
                del connection_to_user[connection_id]

        logger.info(f'User disconnected: {user_id}')
        
        emit('disconnected', {
            'status': 200,
            'message': 'Successfully disconnected from BeekeepingBot',
            'user_id': user_id
        })

    @socketio.on_error_default
    def default_error_handler(e):
        """Handle uncaught exceptions"""
        logger.error(f'Uncaught socket error: {str(e)}', exc_info=True)
        emit('error', {
            'status': 500,
            'message': 'An unexpected error occurred',
            'type': 'ServerError'
        })