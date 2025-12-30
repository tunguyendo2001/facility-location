import os


class Config:
    """Base configuration"""
    
    # Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Database configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_NAME = os.getenv('DB_NAME', 'retail_dss')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'your_password')
    DB_CHARSET = 'utf8mb4'
    
    # Supported algorithms
    SUPPORTED_ALGORITHMS = ['topsis', 'ahp', 'electre', 'promethee']
    DEFAULT_ALGORITHM = 'topsis'
    
    # Analysis configuration
    MAX_SITES = 1000  # Maximum number of sites to analyze
    TOP_RESULTS_LIMIT = 50  # Maximum number of top results to return


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
