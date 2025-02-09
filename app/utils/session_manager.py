from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import json

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.session_timeout = timedelta(hours=1)

    def create_session(self, user_id: str, connection_id: str) -> Dict[str, Any]:
        """Create a new session for a user"""
        session = {
            'user_id': user_id,
            'connection_id': connection_id,
            'created_at': datetime.now(),
            'last_activity': datetime.now(),
            'history': [],
            'context': {},
            'media_uploads': [],
            'analysis_results': []
        }
        self.sessions[user_id] = session
        return session

    def get_session(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get an existing session"""
        session = self.sessions.get(user_id)
        if session:
            if self._is_session_valid(session):
                session['last_activity'] = datetime.now()
                return session
            else:
                self.end_session(user_id)
        return None

    def update_session(self, user_id: str, data: Dict[str, Any]) -> None:
        """Update session data"""
        if session := self.get_session(user_id):
            session.update(data)
            session['last_activity'] = datetime.now()

    def add_to_history(self, user_id: str, interaction: Dict[str, Any]) -> None:
        """Add an interaction to session history"""
        if session := self.get_session(user_id):
            interaction['timestamp'] = datetime.now().isoformat()
            session['history'].append(interaction)

    def add_media_result(self, user_id: str, result: Dict[str, Any]) -> None:
        """Add media analysis result to session"""
        if session := self.get_session(user_id):
            result['timestamp'] = datetime.now().isoformat()
            session['analysis_results'].append(result)

    def get_session_context(self, user_id: str) -> Dict[str, Any]:
        """Get current session context"""
        if session := self.get_session(user_id):
            return session.get('context', {})
        return {}

    def update_context(self, user_id: str, context: Dict[str, Any]) -> None:
        """Update session context"""
        if session := self.get_session(user_id):
            session['context'].update(context)

    def end_session(self, user_id: str) -> None:
        """End a user session"""
        if user_id in self.sessions:
            del self.sessions[user_id]

    def _is_session_valid(self, session: Dict[str, Any]) -> bool:
        """Check if session is still valid"""
        last_activity = session['last_activity']
        return datetime.now() - last_activity < self.session_timeout

    def cleanup_expired_sessions(self) -> None:
        """Remove expired sessions"""
        expired = [
            user_id for user_id, session in self.sessions.items()
            if not self._is_session_valid(session)
        ]
        for user_id in expired:
            self.end_session(user_id)

    def get_session_summary(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get summary of session activity"""
        if session := self.get_session(user_id):
            return {
                'session_duration': str(datetime.now() - session['created_at']),
                'interaction_count': len(session['history']),
                'media_analyses': len(session['analysis_results']),
                'last_activity': session['last_activity'].isoformat()
            }
        return None

# Create global session manager instance
session_manager = SessionManager()