from flask import Flask, render_template
from flask_socketio import SocketIO
import os
from dotenv import load_dotenv
from .handlers.socket_events import register_socket_events
from .controllers.analysis_controller import AnalysisController


import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", ping_timeout=120, ping_interval=30)

# Initialize controller
analysis_controller = AnalysisController()

# Register socket events
register_socket_events(socketio)

@app.route('/')
def index():
    """Serve the main application page"""
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return {'status': 'healthy', 'version': '1.0.0'}

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Run the application
    socketio.run(app, host='0.0.0.0', port=port, debug=debug)