from typing import Dict, Any, List
from datetime import datetime
import json
from pathlib import Path
import threading

class FeedbackSystem:
    def __init__(self):
        self.feedback_dir = Path('feedback')
        self.feedback_dir.mkdir(exist_ok=True)
        self._lock = threading.Lock()

    def save_feedback(self, user_id: str, analysis_id: str, feedback: Dict[str, Any]) -> None:
        """Save user feedback for an analysis"""
        with self._lock:
            feedback_data = {
                'user_id': user_id,
                'analysis_id': analysis_id,
                'feedback': feedback,
                'timestamp': datetime.now().isoformat()
            }
            
            # Save to user-specific feedback file
            user_feedback_file = self.feedback_dir / f'user_{user_id}_feedback.jsonl'
            
            with open(user_feedback_file, 'a') as f:
                f.write(json.dumps(feedback_data) + '\n')

    def get_user_feedback(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all feedback from a specific user"""
        feedback_file = self.feedback_dir / f'user_{user_id}_feedback.jsonl'
        feedback_list = []
        
        if feedback_file.exists():
            with open(feedback_file, 'r') as f:
                for line in f:
                    feedback_list.append(json.loads(line))
        
        return feedback_list

    def get_analysis_feedback(self, analysis_id: str) -> List[Dict[str, Any]]:
        """Get all feedback for a specific analysis"""
        feedback_list = []
        
        for feedback_file in self.feedback_dir.glob('*_feedback.jsonl'):
            with open(feedback_file, 'r') as f:
                for line in f:
                    feedback_data = json.loads(line)
                    if feedback_data['analysis_id'] == analysis_id:
                        feedback_list.append(feedback_data)
        
        return feedback_list

# Create feedback system instance
feedback_system = FeedbackSystem()