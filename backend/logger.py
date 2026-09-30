"""
Logging configuration for Thinx Backend
Provides consistent logging across all modules
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import datetime
import config

# ============================================================================
# LOGGER SETUP
# ============================================================================

def setup_logger(name='thinx', log_file=None, level=None):
    """
    Set up a logger with console and file handlers
    
    Args:
        name: Logger name
        log_file: Path to log file (optional)
        level: Logging level (default from config)
    
    Returns:
        logging.Logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    
    # Set level from config if not specified
    if level is None:
        level = getattr(logging, config.LOG_LEVEL, logging.INFO)
    logger.setLevel(level)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(simple_formatter if config.is_production() else detailed_formatter)
    logger.addHandler(console_handler)
    
    # File handler (if log file specified)
    if log_file or config.LOG_FILE:
        log_path = Path(log_file or config.LOG_FILE)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Rotating file handler (max 10MB per file, keep 5 backups)
        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    
    return logger


# ============================================================================
# REQUEST LOGGING
# ============================================================================

class RequestLogger:
    """Log HTTP requests with useful context"""
    
    def __init__(self, logger):
        self.logger = logger
    
    def log_request(self, request, response_status=None, duration_ms=None):
        """Log an HTTP request"""
        if not config.LOG_REQUESTS:
            return
        
        parts = [
            f"{request.method} {request.path}",
            f"from {request.remote_addr}"
        ]
        
        if response_status:
            parts.append(f"-> {response_status}")
        
        if duration_ms:
            parts.append(f"({duration_ms:.2f}ms)")
        
        # Log at appropriate level
        if response_status and response_status >= 500:
            self.logger.error(" ".join(parts))
        elif response_status and response_status >= 400:
            self.logger.warning(" ".join(parts))
        else:
            self.logger.info(" ".join(parts))
    
    def log_error(self, request, exception, include_traceback=True):
        """Log an error that occurred during request processing"""
        self.logger.error(
            f"Error processing {request.method} {request.path}: {str(exception)}",
            exc_info=include_traceback
        )


# ============================================================================
# SECURITY LOGGING
# ============================================================================

class SecurityLogger:
    """Log security-relevant events"""
    
    def __init__(self, logger):
        self.logger = logger
    
    def log_login_attempt(self, username, success, ip_address):
        """Log login attempt"""
        status = "successful" if success else "failed"
        self.logger.info(f"Login attempt for '{username}' from {ip_address}: {status}")
        
        if not success:
            self.logger.warning(f"Failed login for '{username}' from {ip_address}")
    
    def log_registration(self, username, ip_address):
        """Log user registration"""
        self.logger.info(f"New user registered: '{username}' from {ip_address}")
    
    def log_unauthorized_access(self, resource, ip_address):
        """Log unauthorized access attempt"""
        self.logger.warning(f"Unauthorized access attempt to {resource} from {ip_address}")
    
    def log_data_access(self, username, action, resource):
        """Log data access for audit trail"""
        self.logger.info(f"User '{username}' performed '{action}' on {resource}")


# ============================================================================
# PERFORMANCE LOGGING
# ============================================================================

class PerformanceLogger:
    """Log performance metrics"""
    
    def __init__(self, logger):
        self.logger = logger
    
    def log_slow_query(self, query, duration_seconds, threshold=5):
        """Log queries that take longer than threshold"""
        if duration_seconds > threshold:
            self.logger.warning(
                f"Slow query detected ({duration_seconds:.2f}s): {query[:100]}..."
            )
    
    def log_large_upload(self, filename, size_mb, threshold=10):
        """Log large file uploads"""
        if size_mb > threshold:
            self.logger.info(f"Large file upload: {filename} ({size_mb:.2f} MB)")
    
    def log_memory_usage(self, process_name, memory_mb):
        """Log memory usage"""
        if memory_mb > 1000:  # > 1GB
            self.logger.warning(f"{process_name} using {memory_mb:.2f} MB memory")


# ============================================================================
# APPLICATION LOGGING
# ============================================================================

class ApplicationLogger:
    """High-level application event logging"""
    
    def __init__(self, logger):
        self.logger = logger
    
    def log_startup(self, config_summary):
        """Log application startup"""
        self.logger.info("=" * 60)
        self.logger.info("Thinx Backend Starting")
        self.logger.info("=" * 60)
        for key, value in config_summary.items():
            self.logger.info(f"  {key}: {value}")
        self.logger.info("=" * 60)
    
    def log_shutdown(self):
        """Log application shutdown"""
        self.logger.info("Thinx Backend Shutting Down")
    
    def log_feature_usage(self, feature_name, user=None):
        """Log feature usage for analytics"""
        user_info = f"by {user}" if user else ""
        self.logger.info(f"Feature used: {feature_name} {user_info}")
    
    def log_database_operation(self, operation, success, details=""):
        """Log database operations"""
        status = "succeeded" if success else "failed"
        self.logger.info(f"Database operation '{operation}' {status}. {details}")


# ============================================================================
# GLOBAL LOGGER INSTANCES
# ============================================================================

# Main application logger
app_logger = setup_logger('thinx')

# Specialized loggers
request_logger = RequestLogger(app_logger)
security_logger = SecurityLogger(app_logger)
performance_logger = PerformanceLogger(app_logger)
application_logger = ApplicationLogger(app_logger)


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def log_info(message):
    """Quick info log"""
    app_logger.info(message)

def log_warning(message):
    """Quick warning log"""
    app_logger.warning(message)

def log_error(message, exc_info=False):
    """Quick error log"""
    app_logger.error(message, exc_info=exc_info)

def log_debug(message):
    """Quick debug log"""
    app_logger.debug(message)

def log_critical(message):
    """Quick critical log"""
    app_logger.critical(message)


# ============================================================================
# CONTEXT MANAGER FOR TIMED OPERATIONS
# ============================================================================

class TimedOperation:
    """Context manager to time and log operations"""
    
    def __init__(self, operation_name, logger=None):
        self.operation_name = operation_name
        self.logger = logger or app_logger
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.debug(f"Starting: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()
        
        if exc_type:
            self.logger.error(
                f"{self.operation_name} failed after {duration:.2f}s: {exc_val}"
            )
        else:
            self.logger.info(
                f"{self.operation_name} completed in {duration:.2f}s"
            )
        
        return False  # Don't suppress exceptions


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == '__main__':
    # Example usage
    log_info("This is an info message")
    log_warning("This is a warning")
    log_error("This is an error")
    
    # Timed operation example
    with TimedOperation("Sample Task"):
        import time
        time.sleep(1)
    
    # Security logging example
    security_logger.log_login_attempt("testuser", True, "192.168.1.1")
    
    print("\nLogging examples complete. Check log file at:", config.LOG_FILE)
