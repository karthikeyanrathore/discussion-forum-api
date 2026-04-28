from flask import Flask, jsonify
import logging

from apps.settings import Setting
from apps.views import ingest_bp
import sys


def create_app():
    app = Flask(__name__)
    app.config.from_object(Setting)

    # Logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    
    # Register blueprints
    app.register_blueprint(ingest_bp)
    
    # Error handlers — always use jsonify for JSON responses
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found"}), 404
    
    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "Method not allowed"}), 405
    
    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"error": "Internal server error"}), 500
    
    @app.errorhandler(413)
    def payload_too_large(e):
        return jsonify({"error": "Payload too large"}), 413
    
    return app