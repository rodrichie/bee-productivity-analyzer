from flask_socketio import emit
from app.utils.error_middleware import handle_errors, BeeAnalysisError
from app.utils.progress_tracker import progress_tracker
from app.utils.feedback_system import feedback_system
from app.utils.session_manager import session_manager
from app.models.media_analyzer import MediaAnalyzer
from typing import Dict, Any
import uuid
import logging

logger = logging.getLogger(__name__)
media_analyzer = MediaAnalyzer()

@handle_errors
def process_media_analysis(data: Dict[str, Any]) -> Dict[str, Any]:
    """Process media analysis request with progress tracking and feedback"""
    user_id = data.get('user_id')
    media_type = data.get('media_type')
    analysis_type = data.get('analysis_type', 'general')
    
    # Generate unique analysis ID
    analysis_id = str(uuid.uuid4())
    
    # Start progress tracking
    total_steps = 5 if media_type == 'video' else 3
    progress_tracker.start_tracking(analysis_id, total_steps)
    
    try:
        # Step 1: Validate and prepare media
        progress_tracker.update_progress(analysis_id, 1, "Preparing media for analysis...")
        
        # Step 2: Initial analysis
        progress_tracker.update_progress(analysis_id, 2, "Performing initial analysis...")
        if media_type == 'image':
            result = media_analyzer.analyze_image(data['media_data'], analysis_type)
        else:
            result = media_analyzer.analyze_video(data['media_data'], analysis_type)
        
        # Additional steps for video
        if media_type == 'video':
            progress_tracker.update_progress(analysis_id, 3, "Processing video frames...")
            progress_tracker.update_progress(analysis_id, 4, "Generating temporal analysis...")
        
        # Final step: Generating recommendations
        progress_tracker.update_progress(
            analysis_id,
            total_steps,
            "Generating recommendations..."
        )
        
        # Complete analysis
        progress_tracker.complete_analysis(analysis_id, result)
        
        # Save to session history
        session_manager.add_media_result(user_id, {
            'analysis_id': analysis_id,
            'type': media_type,
            'result': result
        })
        
        return {
            'status': 'success',
            'analysis_id': analysis_id,
            'result': result
        }
        
    except Exception as e:
        progress_tracker.fail_analysis(analysis_id, str(e))
        raise BeeAnalysisError(str(e), "AnalysisError", {
            'analysis_id': analysis_id,
            'media_type': media_type
        })

def register_integrated_handlers(socketio):
    @socketio.on('submit_feedback')
    def handle_feedback(data: Dict[str, Any]):
        """Handle user feedback for analysis"""
        try:
            user_id = data.get('user_id')
            analysis_id = data.get('analysis_id')
            feedback = data.get('feedback')
            
            if not all([user_id, analysis_id, feedback]):
                raise ValueError("Missing required feedback parameters")
            
            feedback_system.save_feedback(user_id, analysis_id, feedback)
            
            emit('feedback_received', {
                'status': 'success',
                'message': 'Feedback received successfully'
            })
            
        except Exception as e:
            logger.error(f"Error processing feedback: {str(e)}")
            emit('error', {
                'status': 'error',
                'message': 'Error processing feedback',
                'details': str(e)
            })

    @socketio.on('get_analysis_status')
    def handle_status_request(data: Dict[str, Any]):
        """Handle analysis status requests"""
        analysis_id = data.get('analysis_id')
        if not analysis_id:
            emit('error', {
                'status': 'error',
                'message': 'Analysis ID required'
            })
            return
            
        progress = progress_tracker.get_progress(analysis_id)
        if progress:
            emit('analysis_status', {
                'status': 'success',
                'progress': progress
            })
        else:
            emit('error', {
                'status': 'error',
                'message': 'Analysis not found'
            })