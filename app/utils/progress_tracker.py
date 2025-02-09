from typing import Dict, Any, Optional
from datetime import datetime
from flask_socketio import emit
import threading
import time

class AnalysisProgressTracker:
    def __init__(self):
        self.progress_data: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def start_tracking(self, analysis_id: str, total_steps: int) -> None:
        """Initialize progress tracking for an analysis"""
        with self._lock:
            self.progress_data[analysis_id] = {
                'started_at': datetime.now(),
                'current_step': 0,
                'total_steps': total_steps,
                'status': 'in_progress',
                'messages': [],
                'completed_at': None
            }

    def update_progress(self, analysis_id: str, step: int, message: str) -> None:
        """Update progress for an analysis"""
        with self._lock:
            if analysis_id in self.progress_data:
                data = self.progress_data[analysis_id]
                data['current_step'] = step
                data['messages'].append({
                    'step': step,
                    'message': message,
                    'timestamp': datetime.now().isoformat()
                })
                
                # Calculate progress percentage
                progress = (step / data['total_steps']) * 100
                
                # Emit progress update
                emit('analysis_progress', {
                    'analysis_id': analysis_id,
                    'progress': progress,
                    'step': step,
                    'message': message,
                    'total_steps': data['total_steps']
                })

    def complete_analysis(self, analysis_id: str, results: Dict[str, Any]) -> None:
        """Mark analysis as complete"""
        with self._lock:
            if analysis_id in self.progress_data:
                self.progress_data[analysis_id].update({
                    'status': 'completed',
                    'completed_at': datetime.now(),
                    'results': results
                })
                
                emit('analysis_complete', {
                    'analysis_id': analysis_id,
                    'results': results,
                    'duration': str(datetime.now() - self.progress_data[analysis_id]['started_at'])
                })

    def fail_analysis(self, analysis_id: str, error: str) -> None:
        """Mark analysis as failed"""
        with self._lock:
            if analysis_id in self.progress_data:
                self.progress_data[analysis_id].update({
                    'status': 'failed',
                    'completed_at': datetime.now(),
                    'error': error
                })
                
                emit('analysis_failed', {
                    'analysis_id': analysis_id,
                    'error': error
                })

    def get_progress(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Get current progress for an analysis"""
        with self._lock:
            return self.progress_data.get(analysis_id)

# Create global progress tracker instance
progress_tracker = AnalysisProgressTracker()