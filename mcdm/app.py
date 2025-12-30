from flask import Flask
from flask_cors import CORS
from config import Config
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def create_app(config_class=Config):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Register blueprints
    from api.health_routes import health_bp
    from api.analysis_routes import analysis_bp
    
    app.register_blueprint(health_bp, url_prefix='/api')
    app.register_blueprint(analysis_bp, url_prefix='/api')
    
    logger.info("Flask MCDM Service initialized successfully")
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
