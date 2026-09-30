"""
Configuration settings for Thinx Flask Backend
Supports both development and production environments
"""

import os
from pathlib import Path

# ============================================================================
# BASE CONFIGURATION
# ============================================================================

# Base directory
BASE_DIR = Path(__file__).parent

# Data storage
DATA_DIR = BASE_DIR / 'data'
DATA_DIR.mkdir(exist_ok=True)

CONNECTIONS_FILE = DATA_DIR / 'connections.json'
USERS_FILE = DATA_DIR / 'users.json'

# Uploads directory
UPLOAD_DIR = Path(os.getenv('UPLOAD_FOLDER', str(BASE_DIR / 'uploads')))
UPLOAD_DIR.mkdir(exist_ok=True)

# Logs directory
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)

# ============================================================================
# FLASK APPLICATION SETTINGS
# ============================================================================

# Environment: development, production, testing
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

# Secret key for sessions (MUST be set in production)
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
if FLASK_ENV == 'production' and SECRET_KEY == 'dev-key-change-in-production':
    import warnings
    warnings.warn("SECRET_KEY not set! Using default key is insecure in production!")

# Session settings
SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', 3600))  # 1 hour default
SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
SESSION_COOKIE_HTTPONLY = os.getenv('SESSION_COOKIE_HTTPONLY', 'True').lower() == 'true'
SESSION_COOKIE_SAMESITE = os.getenv('SESSION_COOKIE_SAMESITE', 'Lax')

# ============================================================================
# ALLEGROGRAPH DATABASE SETTINGS
# ============================================================================

# AllegroGraph connection settings
AGRAPH_HOST = os.getenv('AGRAPH_HOST', 'ag1jdz6nqkhfjj72.allegrograph.cloud')
AGRAPH_PORT = int(os.getenv('AGRAPH_PORT', 10035))
AGRAPH_REPOSITORY = os.getenv('AGRAPH_REPOSITORY', 'KS01')
AGRAPH_USER = os.getenv('AGRAPH_SUPER_USER', 'Admin')
AGRAPH_PASSWORD = os.getenv('AGRAPH_SUPER_PASSWORD', 'KbA8KuX3E7aZSOVwGCxiK4')

# Warn if using default credentials
if FLASK_ENV == 'production' and AGRAPH_PASSWORD == 'admin123':
    import warnings
    warnings.warn("Default AllegroGraph password detected! Change in production!")

# ============================================================================
# CORS CONFIGURATION
# ============================================================================

# CORS allowed origins
CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost,http://localhost:80').split(',')
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost,http://localhost:80').split(',')

# Merge both for backwards compatibility
ALL_ALLOWED_ORIGINS = list(set(CORS_ORIGINS + ALLOWED_ORIGINS))

# ============================================================================
# FILE UPLOAD SETTINGS
# ============================================================================

# Maximum file size (50MB default)
MAX_UPLOAD_SIZE = int(os.getenv('MAX_UPLOAD_SIZE', 52428800))

# Allowed file extensions
ALLOWED_EXTENSIONS = set(os.getenv('ALLOWED_EXTENSIONS', 'xlsx,xls,json,csv').split(','))

# Upload retention in days (0 = keep forever)
UPLOAD_RETENTION_DAYS = int(os.getenv('UPLOAD_RETENTION_DAYS', 30))

# ============================================================================
# API SETTINGS
# ============================================================================

# API request timeout in seconds
API_TIMEOUT = int(os.getenv('API_TIMEOUT', 30))

# Maximum query results to return
MAX_QUERY_RESULTS = int(os.getenv('MAX_QUERY_RESULTS', 1000))

# Rate limiting
RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'False').lower() == 'true'
RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', 60))
RATE_LIMIT_PER_HOUR = int(os.getenv('RATE_LIMIT_PER_HOUR', 1000))

# ============================================================================
# AI/OLLAMA SETTINGS
# ============================================================================

# Enable AI Smart Mapper features
OLLAMA_ENABLED = os.getenv('OLLAMA_ENABLED', 'True').lower() == 'true'

# Ollama server connection
OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'ollama')
OLLAMA_PORT = int(os.getenv('OLLAMA_PORT', 11434))
OLLAMA_BASE_URL = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}"

# Default AI model
OLLAMA_DEFAULT_MODEL = os.getenv('OLLAMA_DEFAULT_MODEL', 'llama3.2')

# AI request timeout (can be longer for complex operations)
OLLAMA_TIMEOUT = int(os.getenv('OLLAMA_TIMEOUT', 120))

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

# Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()

# Log file path
LOG_FILE = os.getenv('LOG_FILE', str(LOG_DIR / 'thinx.log'))

# Enable request logging
LOG_REQUESTS = os.getenv('LOG_REQUESTS', 'True').lower() == 'true'

# Log retention in days
LOG_RETENTION_DAYS = int(os.getenv('LOG_RETENTION_DAYS', 90))

# ============================================================================
# SECURITY SETTINGS
# ============================================================================

# Allow user registration
ALLOW_REGISTRATION = os.getenv('ALLOW_REGISTRATION', 'True').lower() == 'true'

# Password requirements
MIN_PASSWORD_LENGTH = int(os.getenv('MIN_PASSWORD_LENGTH', 6))
REQUIRE_STRONG_PASSWORDS = os.getenv('REQUIRE_STRONG_PASSWORDS', 'False').lower() == 'true'

# Admin key for protected operations (optional)
ADMIN_KEY = os.getenv('ADMIN_KEY', None)

# ============================================================================
# MONITORING & HEALTH CHECKS
# ============================================================================

# Enable health check endpoint
HEALTH_CHECK_ENABLED = os.getenv('HEALTH_CHECK_ENABLED', 'True').lower() == 'true'

# Enable metrics endpoint
METRICS_ENABLED = os.getenv('METRICS_ENABLED', 'False').lower() == 'true'
METRICS_TOKEN = os.getenv('METRICS_TOKEN', None)

# ============================================================================
# PRODUCTION SETTINGS
# ============================================================================

# Number of Gunicorn workers (production only)
WORKERS = int(os.getenv('WORKERS', 4))

# Worker timeout
WORKER_TIMEOUT = int(os.getenv('WORKER_TIMEOUT', 300))

# Enable Gzip compression
GZIP_ENABLED = os.getenv('GZIP_ENABLED', 'True').lower() == 'true'

# Cache timeout in seconds
CACHE_TIMEOUT = int(os.getenv('CACHE_TIMEOUT', 300))

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def is_production():
    """Check if running in production mode"""
    return FLASK_ENV == 'production'

def is_development():
    """Check if running in development mode"""
    return FLASK_ENV == 'development'

def get_config_summary():
    """Get a summary of current configuration (safe for logging)"""
    return {
        'environment': FLASK_ENV,
        'debug': FLASK_DEBUG,
        'agraph_host': AGRAPH_HOST,
        'agraph_port': AGRAPH_PORT,
        'ollama_enabled': OLLAMA_ENABLED,
        'cors_origins': ALL_ALLOWED_ORIGINS,
        'upload_max_size': MAX_UPLOAD_SIZE,
        'log_level': LOG_LEVEL
    }
