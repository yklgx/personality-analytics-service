"""
Personality Analytics Service - Main Application
Multi-service architecture for personality prediction
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key')
    app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Enable CORS
    CORS(app)
    
    # Basic health check endpoint
    @app.route('/health')
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'service': 'personality-analytics',
            'version': '1.0.0',
            'environment': 'codespace'
        })
    
    @app.route('/')
    def index():
        """Welcome endpoint"""
        return jsonify({
            'message': 'Personality Analytics Service',
            'description': 'AI-powered personality prediction API',
            'team_size': '3 developers',
            'development_mode': 'GitHub Codespaces',
            'endpoints': {
                'health': '/health',
                'predict': '/api/v1/predict (coming soon)',
                'batch_predict': '/api/v1/batch_predict (coming soon)',
                'docs': '/docs (coming soon)'
            }
        })
    
    return app

if __name__ == '__main__':
    app = create_app()
    # In Codespaces, use 0.0.0.0 to make it accessible
    app.run(host='0.0.0.0', port=5000, debug=True)
