"""
Thinx - Flask Backend API
Human Trafficking Research Platform
Connection Manager

This backend provides a RESTful API for managing AllegroGraph connections,
executing SPARQL queries, and mapping CSV/Excel data to the Common Data Model (CDM)
using local AI. All data processing is GDPR-compliant and happens on-premises.

CDM is defined in hds_cdm.ttl and models.py
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from pathlib import Path
from datetime import datetime
from werkzeug.exceptions import HTTPException
from models import Connection, ConnectionManager, UserManager
from utils.allegrograph import AllegroGraphClient
from utils.ai_mapper import SmartMapper
from utils.fair_data_point import FairDataPointClient

app = Flask(__name__)

# Enable CORS for Vue.js frontend
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:8080", "http://localhost"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Configuration
DATA_DIR = Path(__file__).parent / 'data'
DATA_DIR.mkdir(exist_ok=True)
CONNECTIONS_FILE = DATA_DIR / 'connections.json'
USERS_FILE = DATA_DIR / 'users.json'

# Initialize managers
connection_manager = ConnectionManager(CONNECTIONS_FILE)
user_manager = UserManager(USERS_FILE)


# ============================================================================
# VALIDATION HELPERS
# ============================================================================

# Allowed file extensions for data uploads
ALLOWED_EXTENSIONS = {'.csv', '.xlsx', '.xls', '.json'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB


def validate_file_upload(file):
    """
    Validate uploaded file for security and compatibility.
    
    Performs comprehensive validation:
    - Checks file exists and has filename
    - Validates file extension against whitelist
    - Ensures file is not empty
    - Checks file size is within limits
    
    Args:
        file: werkzeug.datastructures.FileStorage object from request.files
        
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
        
    Example:
        >>> file = request.files['file']
        >>> valid, error = validate_file_upload(file)
        >>> if not valid:
        ...     return jsonify({'success': False, 'error': error}), 400
    """
    # Check if file exists
    if not file or file.filename == '':
        return False, 'No file selected'
    
    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        allowed = ', '.join(ALLOWED_EXTENSIONS)
        return False, f'Unsupported file type. Allowed: {allowed}'
    
    # Check if file is empty (read a bit and reset)
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)  # Reset to beginning
    
    if file_size == 0:
        return False, 'File is empty'
    
    # Check file size limit
    if file_size > MAX_FILE_SIZE:
        max_mb = MAX_FILE_SIZE / (1024 * 1024)
        return False, f'File too large. Maximum size: {max_mb}MB'
    
    return True, None


# ============================================================================
# GLOBAL ERROR HANDLERS
# ============================================================================

@app.errorhandler(Exception)
def handle_exception(error):
    """
    Global exception handler for all unhandled errors.
    
    Catches all exceptions including database failures, network errors,
    and unexpected runtime errors. Returns consistent JSON error response
    for client consumption.
    
    Args:
        error (Exception): The caught exception.
        
    Returns:
        tuple: (JSON response, HTTP status code)
        
    Note:
        This ensures production stability by preventing stack trace exposure
        and providing consistent error responses to the frontend.
    """
    # Handle HTTP exceptions (like 404, 405) separately
    if isinstance(error, HTTPException):
        return jsonify({
            'success': False,
            'error': error.description
        }), error.code
    
    # Log the error for debugging
    app.logger.error(f"Unhandled exception: {str(error)}", exc_info=True)
    
    # Return generic error response
    return jsonify({
        'success': False,
        'error': f'Internal server error: {str(error)}'
    }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 Not Found errors with consistent JSON response."""
    return jsonify({
        'success': False,
        'error': 'Resource not found'
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 Method Not Allowed errors with consistent JSON response."""
    return jsonify({
        'success': False,
        'error': 'Method not allowed for this endpoint'
    }), 405


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for Docker container monitoring.
    
    Returns:
        JSON response with service status and timestamp.
        
    Note:
        Used by Docker healthcheck to monitor container health.
    """
    return jsonify({
        'status': 'healthy',
        'service': 'flask_api',
        'timestamp': datetime.utcnow().isoformat()
    }), 200


# Authentication endpoints
@app.route('/api/register', methods=['POST'])
def register():
    """
    Register a new user account.
    
    Request JSON:
        {
            "username": str (min 3 characters),
            "password": str (min 6 characters)
        }
        
    Returns:
        JSON response:
        {
            "success": true,
            "user": {user object without password},
            "message": "User registered successfully"
        }
        
    Note:
        Passwords are hashed using SHA256. User data stored locally only.
    """
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({
                'success': False,
                'error': 'Username and password are required'
            }), 400
        
        if len(username) < 3:
            return jsonify({
                'success': False,
                'error': 'Username must be at least 3 characters'
            }), 400
        
        if len(password) < 6:
            return jsonify({
                'success': False,
                'error': 'Password must be at least 6 characters'
            }), 400
        
        user = user_manager.create_user(username, password)
        
        # Remove password hash from response
        user_data = {k: v for k, v in user.items() if k != 'password_hash'}
        
        return jsonify({
            'success': True,
            'user': user_data,
            'message': 'User registered successfully'
        }), 201
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Registration failed: {str(e)}'
        }), 500


@app.route('/api/login', methods=['POST'])
def login():
    """
    Authenticate user with username and password.
    
    Request JSON:
        {
            "username": str,
            "password": str
        }
        
    Returns:
        JSON response:
        {
            "success": true,
            "user": {user object without password},
            "message": "Login successful"
        }
        
    Note:
        All authentication is local. No external services involved.
        Session management handled client-side for stateless API.
    """
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({
                'success': False,
                'error': 'Username and password are required'
            }), 400
        
        user = user_manager.authenticate(username, password)
        
        if user:
            # Remove password hash from response
            user_data = {k: v for k, v in user.items() if k != 'password_hash'}
            return jsonify({
                'success': True,
                'user': user_data,
                'message': 'Login successful'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid username or password'
            }), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Login failed: {str(e)}'
        }), 500


@app.route('/api/logout', methods=['POST'])
def logout():
    """Logout user (client-side session management)"""
    return jsonify({
        'success': True,
        'message': 'Logout successful'
    }), 200


# Admin endpoints
@app.route('/api/admin/users', methods=['GET'])
def get_all_users():
    """Get all users (admin only)"""
    try:
        # In production, verify admin status from session/token
        users = user_manager.get_all_users()
        return jsonify({
            'success': True,
            'users': users
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to fetch users: {str(e)}'
        }), 500


@app.route('/api/admin/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    """Update user details (admin only)"""
    try:
        data = request.get_json()
        updated_user = user_manager.update_user(user_id, data)
        
        if updated_user:
            return jsonify({
                'success': True,
                'user': updated_user,
                'message': 'User updated successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Update failed: {str(e)}'
        }), 500


@app.route('/api/admin/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete user (admin only)"""
    try:
        if user_manager.delete_user(user_id):
            return jsonify({
                'success': True,
                'message': 'User deleted successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Delete failed: {str(e)}'
        }), 500


@app.route('/api/debug/types', methods=['POST'])
def debug_types():
    """Debug endpoint to check what types exist in the repository"""
    try:
        data = request.get_json()
        connection_id = data.get('connection_id')
        
        if not connection_id:
            return jsonify({
                'success': False,
                'error': 'Connection ID required'
            }), 400
        
        connection = connection_manager.get_connection(connection_id)
        if not connection:
            return jsonify({
                'success': False,
                'error': 'Connection not found'
            }), 404
        
        ag_client = AllegroGraphClient(
            connection['host'],
            connection['port'],
            connection['repository'],
            connection['username'],
            connection['password']
        )
        
        # Get all distinct types
        types_query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT DISTINCT ?type (COUNT(?s) as ?count)
        WHERE { ?s rdf:type ?type }
        GROUP BY ?type
        """
        types = ag_client.execute_query(types_query)
        
        # Get sample victim data
        sample_query = """
        PREFIX ex: <http://example.org/ontology#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT ?s ?p ?o
        WHERE { 
            ?s rdf:type ex:Victim .
            ?s ?p ?o 
        }
        LIMIT 20
        """
        samples = ag_client.execute_query(sample_query)
        
        return jsonify({
            'success': True,
            'types': types,
            'samples': samples
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/connections', methods=['GET'])
def get_connections():
    """
    Retrieve all AllegroGraph database connections for a user.
    
    Query Parameters:
        user_id (str, optional): Filter connections by user ID
        
    Returns:
        JSON response:
        {
            "success": true,
            "connections": [array of connection objects],
            "count": int
        }
        
    Note:
        Connection credentials stored locally in encrypted format.
    """
    try:
        user_id = request.args.get('user_id')
        connections = connection_manager.get_all_connections(user_id=user_id)
        return jsonify({
            'success': True,
            'connections': connections,
            'count': len(connections)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/connections', methods=['POST'])
def create_connection():
    """
    Create new AllegroGraph database connection.
    
    Request JSON:
        {
            "name": str (required),
            "type": "allegrograph" | "fair",
            "host": str (required for allegrograph),
            "port": int (required for allegrograph),
            "repository": str (required for allegrograph),
            "username": str (required for allegrograph),
            "password": str (required for allegrograph),
            "user_id": str (required),
            "test_connection": bool (optional, default false)
        }
        
    Returns:
        JSON response:
        {
            "success": true,
            "message": "Connection created successfully",
            "connection": {connection object}
        }
        
    Note:
        Set test_connection=true to validate credentials before saving.
        All connection data stored locally for GDPR compliance.
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        connection_type = data.get('type', '')
        user_id = data.get('user_id')  # Required for user ownership
        
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'user_id is required'
            }), 400
        
        # Validate required fields based on connection type
        if connection_type == 'fair':
            required_fields = ['name', 'fair_url']
        else:
            required_fields = ['name', 'host', 'port', 'repository', 'username', 'password']
        
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # Create connection object
        connection = Connection(
            name=data['name'],
            connection_type=connection_type,
            host=data.get('host', ''),
            port=data.get('port', 10035),
            repository=data.get('repository', ''),
            username=data.get('username', ''),
            password=data.get('password', ''),
            description=data.get('description', ''),
            user_id=user_id,
            # FAIR Data Point metadata
            catalog_id=data.get('catalog_id'),
            catalog_title=data.get('catalog_title'),
            catalog_publisher=data.get('catalog_publisher'),
            catalog_contact=data.get('catalog_contact'),
            catalog_license=data.get('catalog_license'),
            catalog_themes=data.get('catalog_themes', []),
            dataset_count=data.get('dataset_count', 0)
        )
        
        # Test AllegroGraph connection before saving (only if requested and type is allegrograph)
        # Set test_connection=false to skip validation and save anyway
        if connection_type == 'allegrograph':
            test_conn = data.get('test_connection', False)
            if test_conn:
                ag_client = AllegroGraphClient(
                    connection.host,
                    connection.port,
                    connection.repository,
                    connection.username,
                    connection.password
                )
                
                if not ag_client.test_connection():
                    return jsonify({
                        'success': False,
                        'error': 'Failed to connect to AllegroGraph with provided credentials'
                    }), 400
        
        # Save connection
        saved_connection = connection_manager.add_connection(connection)
        
        return jsonify({
            'success': True,
            'message': 'Connection created successfully',
            'connection': saved_connection
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/connections/<connection_id>', methods=['GET'])
def get_connection(connection_id):
    """Get a specific connection by ID"""
    try:
        connection = connection_manager.get_connection(connection_id)
        
        if not connection:
            return jsonify({
                'success': False,
                'error': 'Connection not found'
            }), 404
        
        return jsonify({
            'success': True,
            'connection': connection
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/connections/<connection_id>', methods=['PUT'])
def update_connection(connection_id):
    """Update an existing connection"""
    try:
        data = request.get_json()
        updated_connection = connection_manager.update_connection(connection_id, data)
        
        if not updated_connection:
            return jsonify({
                'success': False,
                'error': 'Connection not found'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Connection updated successfully',
            'connection': updated_connection
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/connections/<connection_id>', methods=['DELETE'])
def delete_connection(connection_id):
    """Delete a connection"""
    try:
        success = connection_manager.delete_connection(connection_id)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Connection not found'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Connection deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/connections/<connection_id>/activate', methods=['POST'])
def activate_connection(connection_id):
    """Set a connection as active"""
    try:
        success = connection_manager.set_active_connection(connection_id)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Connection not found'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Connection activated successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/connections/active', methods=['GET'])
def get_active_connection():
    """Get the currently active connection"""
    try:
        active_connection = connection_manager.get_active_connection()
        
        if not active_connection:
            return jsonify({
                'success': False,
                'error': 'No active connection'
            }), 404
        
        return jsonify({
            'success': True,
            'connection': active_connection
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/query', methods=['POST'])
def execute_query():
    """
    Execute SPARQL query on AllegroGraph database.
    
    Request JSON:
        {
            "query": str (SPARQL query),
            "connection_id": str (optional, uses active connection if not provided)
        }
        
    Returns:
        JSON response:
        {
            "success": true,
            "results": [array of query result objects]
        }
        
    Note:
        All queries execute within local network. No external data transmission.
        Supports full SPARQL 1.1 specification.
    """
    try:
        data = request.get_json()
        query = data.get('query')
        connection_id = data.get('connection_id')
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query is required'
            }), 400
        
        # Get connection (use specified or active)
        if connection_id:
            connection = connection_manager.get_connection(connection_id)
        else:
            connection = connection_manager.get_active_connection()
        
        if not connection:
            return jsonify({
                'success': False,
                'error': 'No connection specified or active'
            }), 400
        
        # Execute query
        ag_client = AllegroGraphClient(
            connection['host'],
            connection['port'],
            connection['repository'],
            connection['username'],
            connection['password']
        )
        
        results = ag_client.execute_query(query)
        
        return jsonify({
            'success': True,
            'results': results
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/data', methods=['GET'])
def get_data():
    """Get data from active connection with optional filters"""
    try:
        connection_id = request.args.get('connection_id')
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Get connection
        if connection_id:
            connection = connection_manager.get_connection(connection_id)
        else:
            connection = connection_manager.get_active_connection()
        
        if not connection:
            return jsonify({
                'success': False,
                'error': 'No connection specified or active'
            }), 400
        
        # Create AllegroGraph client
        ag_client = AllegroGraphClient(
            connection['host'],
            connection['port'],
            connection['repository'],
            connection['username'],
            connection['password']
        )
        
        # Query for victim data
        query = f"""
        PREFIX hds: <http://example.org/hds#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT DISTINCT ?victim ?age ?gender ?nationality
        WHERE {{
            ?victim a hds:Victim .
            OPTIONAL {{ ?victim hds:age ?age }}
            OPTIONAL {{ ?victim hds:gender ?gender }}
            OPTIONAL {{ ?victim hds:nationality ?nationality }}
        }}
        LIMIT {limit}
        OFFSET {offset}
        """
        
        results = ag_client.execute_query(query)
        
        print(f"[Data] Query returned {len(results)} results")
        if len(results) > 0:
            print(f"[Data] First result: {results[0]}")
        else:
            # Debug: Check what's actually in the repository
            try:
                # Get all types
                debug_query = "SELECT DISTINCT ?type WHERE { ?s a ?type } LIMIT 20"
                types = ag_client.execute_query(debug_query)
                print(f"[Data] Types found in repository: {types}")
                
                # Get sample triples
                sample_query = "SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 10"
                samples = ag_client.execute_query(sample_query)
                print(f"[Data] Sample triples: {samples}")
                
                # Check for any victims with any predicate
                victim_check = """
                PREFIX hds: <http://example.org/hds#>
                SELECT ?s ?p ?o WHERE { 
                    ?s a hds:Victim .
                    ?s ?p ?o 
                } LIMIT 5
                """
                victim_data = ag_client.execute_query(victim_check)
                print(f"[Data] Sample victim data: {victim_data}")
            except Exception as debug_error:
                print(f"[Data] Debug query failed: {debug_error}")
        
        return jsonify({
            'success': True,
            'data': results,
            'count': len(results),
            'limit': limit,
            'offset': offset
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get statistics from active connection"""
    try:
        connection_id = request.args.get('connection_id')
        
        # Get connection
        if connection_id:
            connection = connection_manager.get_connection(connection_id)
        else:
            connection = connection_manager.get_active_connection()
        
        if not connection:
            return jsonify({
                'success': False,
                'error': 'No connection specified or active'
            }), 400
        
        # Create AllegroGraph client
        ag_client = AllegroGraphClient(
            connection['host'],
            connection['port'],
            connection['repository'],
            connection['username'],
            connection['password']
        )
        
        # Get statistics
        stats = ag_client.get_statistics()
        
        return jsonify({
            'success': True,
            'statistics': stats
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/ontology', methods=['GET'])
def get_ontology():
    """Get CDM (Common Data Model) structure"""
    try:
        # Define CDM structure
        cdm = {
            'entities': [
                {
                    'name': 'Victim',
                    'description': 'Individual affected by human trafficking',
                    'fields': [
                        {'name': 'victim_id', 'type': 'string', 'required': True, 'sensitive': False},
                        {'name': 'age', 'type': 'integer', 'required': False, 'sensitive': True},
                        {'name': 'gender', 'type': 'string', 'required': False, 'sensitive': True},
                        {'name': 'nationality', 'type': 'string', 'required': False, 'sensitive': True}
                    ]
                },
                {
                    'name': 'Crime',
                    'description': 'Criminal acts and abuses experienced',
                    'fields': [
                        {'name': 'sexual_violence_experienced_binary', 'type': 'boolean', 'required': False, 'sensitive': True},
                        {'name': 'deaths_witnessed_binary', 'type': 'boolean', 'required': False, 'sensitive': True}
                    ]
                },
                {
                    'name': 'Trafficker',
                    'description': 'Individual or organization involved in trafficking',
                    'fields': [
                        {'name': 'trafficker_id', 'type': 'string', 'required': True, 'sensitive': False},
                        {'name': 'nationality', 'type': 'string', 'required': False, 'sensitive': False}
                    ]
                },
                {
                    'name': 'Border',
                    'description': 'Geographic crossing point or transit location',
                    'fields': [
                        {'name': 'border_name', 'type': 'string', 'required': True, 'sensitive': False},
                        {'name': 'country', 'type': 'string', 'required': False, 'sensitive': False}
                    ]
                },
                {
                    'name': 'Extortion',
                    'description': 'Financial exploitation and ransom demands',
                    'fields': [
                        {'name': 'amount', 'type': 'number', 'required': False, 'sensitive': False},
                        {'name': 'currency', 'type': 'string', 'required': False, 'sensitive': False}
                    ]
                }
            ]
        }
        
        return jsonify({
            'success': True,
            'ontology': cdm
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/schema', methods=['GET'])
def get_schema():
    """Get the CDM schema"""
    try:
        from models import get_cdm_schema
        schema = get_cdm_schema()
        
        return jsonify({
            'success': True,
            'schema': schema
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """
    Upload CSV, Excel, or JSON data file for processing.
    
    Accepts file uploads via multipart/form-data and performs validation:
    - File extension must be .csv, .xlsx, .xls, or .json
    - File must not be empty
    - File size must be under 100MB
    
    Request:
        - file: File object (multipart/form-data)
        
    Returns:
        JSON response:
        {
            "success": true,
            "message": "File uploaded successfully",
            "file_type": "excel|json",
            "filename": "data.xlsx",
            "record_count": 1234  (for JSON only)
        }
        
    Note:
        All uploaded data remains on-premises. No data leaves the system.
        Files are stored in /workspace for GDPR-compliant local processing.
    """
    from werkzeug.utils import secure_filename
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    file = request.files['file']
    
    # Validate file using our validation helper
    valid, error = validate_file_upload(file)
    if not valid:
        return jsonify({'success': False, 'error': error}), 400
    
    try:
        # Use /workspace which is mounted from root directory in docker-compose
        base_dir = Path('/workspace')
        
        if file.filename.endswith(('.xlsx', '.xls', '.csv')):
            # Save Excel/CSV file
            filename = 'data.xlsx'
            filepath = base_dir / filename
            file.save(filepath)
            
            return jsonify({
                'success': True,
                'message': f'File uploaded successfully: {filename}',
                'file_type': 'excel',
                'filename': filename
            })
        
        elif file.filename.endswith('.json'):
            # Save JSON file
            filename = secure_filename(file.filename)
            filepath = base_dir / 'uploads' / filename
            filepath.parent.mkdir(exist_ok=True)
            file.save(filepath)
            
            # Validate JSON structure
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                return jsonify({'success': False, 'error': 'JSON must be an array of records'}), 400
            
            return jsonify({
                'success': True,
                'message': f'File uploaded successfully: {filename}',
                'file_type': 'json',
                'filename': filename,
                'record_count': len(data)
            })
    
    except json.JSONDecodeError:
        return jsonify({'success': False, 'error': 'Invalid JSON file format'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/validate', methods=['POST'])
def validate_data():
    """
    Validate uploaded data file structure and content.
    
    Checks:
    - File exists and is readable
    - File contains data rows
    - Basic structure validation
    
    Returns:
        JSON response:
        {
            "success": true,
            "validation": {
                "passed": bool,
                "total_rows": int,
                "valid_rows": int,
                "errors": [array of error messages],
                "warnings": [array of warnings]
            }
        }
        
    Note:
        All validation happens locally. No data transmission.
    """
    try:
        import pandas as pd
        
        # Use /workspace which is mounted from root directory in docker-compose
        base_dir = Path('/workspace')
        data_file = base_dir / 'data.xlsx'
        
        if not data_file.exists():
            return jsonify({
                'success': False,
                'error': 'No data file found. Please upload a file first.'
            }), 400
        
        # Read the Excel file to get row count
        try:
            df = pd.read_excel(data_file)
            total_rows = len(df)
            
            # Basic validation - check if file has data
            if total_rows == 0:
                return jsonify({
                    'success': True,
                    'validation': {
                        'passed': False,
                        'total_rows': 0,
                        'valid_rows': 0,
                        'errors': ['File contains no data rows'],
                        'warnings': []
                    }
                }), 200
            
            return jsonify({
                'success': True,
                'validation': {
                    'passed': True,
                    'total_rows': total_rows,
                    'valid_rows': total_rows,
                    'errors': [],
                    'warnings': [],
                    'message': f'File validated successfully. Found {total_rows} data rows.'
                }
            }), 200
        except Exception as read_error:
            return jsonify({
                'success': False,
                'error': f'Failed to read Excel file: {str(read_error)}'
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/run-notebook', methods=['POST'])
def run_notebook():
    """Execute a Jupyter notebook"""
    import subprocess
    import sys
    
    try:
        data = request.get_json()
        notebook = data.get('notebook')
        
        if not notebook or not notebook.endswith('.ipynb'):
            return jsonify({'error': 'Invalid notebook name'}), 400
        
        # Use /workspace which is mounted from root directory in docker-compose
        base_dir = Path('/workspace')
        notebook_path = base_dir / notebook
        
        print(f"[Notebook] Looking for notebook at: {notebook_path}")
        print(f"[Notebook] Base directory: {base_dir}")
        print(f"[Notebook] Notebook exists: {notebook_path.exists()}")
        
        if not notebook_path.exists():
            # List files in base_dir for debugging
            try:
                files = list(base_dir.glob('*.ipynb'))
                print(f"[Notebook] Available .ipynb files: {[f.name for f in files]}")
            except:
                pass
            return jsonify({
                'error': f'Notebook not found: {notebook}',
                'path': str(notebook_path),
                'base_dir': str(base_dir)
            }), 404
        
        # Run the notebook using nbconvert
        result = subprocess.run(
            [sys.executable, '-m', 'jupyter', 'nbconvert', '--to', 'notebook', 
             '--execute', '--inplace', str(notebook_path)],
            capture_output=True,
            text=True,
            cwd=base_dir,
            timeout=300  # 5 minutes timeout
        )
        
        if result.returncode == 0:
            # Create meaningful output based on which notebook ran
            output_info = []
            if 'processing.ipynb' in notebook:
                output_info.append('✓ Data cleaning and standardization completed')
                if (base_dir / 'victims.json').exists():
                    output_info.append('✓ Created victims.json')
            elif 'json_creator.ipynb' in notebook:
                output_info.append('✓ Duplicate detection and merging completed')
                if (base_dir / 'cleaned_data.json').exists():
                    output_info.append('✓ Created cleaned_data.json')
            
            output_text = '\n'.join(output_info) if output_info else result.stdout
            
            return jsonify({
                'success': True,
                'message': f'Successfully executed {notebook}',
                'output': output_text
            })
        else:
            return jsonify({
                'success': False,
                'error': result.stderr or result.stdout or 'Unknown error occurred'
            }), 500
    
    except subprocess.TimeoutExpired:
        return jsonify({'success': False, 'error': 'Notebook execution timed out (5 min limit)'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/push-to-allegrograph', methods=['POST'])
def push_to_allegrograph():
    """Push generated RDF to AllegroGraph using selected connection"""
    import subprocess
    import sys
    from pathlib import Path
    
    try:
        data = request.get_json()
        connection_id = data.get('connection_id')
        
        if not connection_id:
            return jsonify({
                'success': False,
                'error': 'No connection specified'
            }), 400
        
        # Get the connection details
        connection = connection_manager.get_connection(connection_id)
        if not connection:
            return jsonify({
                'success': False,
                'error': 'Connection not found'
            }), 404
        
        # Use /workspace which is mounted from root directory in docker-compose
        base_dir = Path('/workspace')
        
        # Check if cleaned_data.json exists (required for RDF generation)
        cleaned_data = base_dir / 'cleaned_data.json'
        if not cleaned_data.exists():
            return jsonify({
                'success': False,
                'error': 'cleaned_data.json not found. Please run data processing first (Step 4).'
            }), 400
        
        # Run the push_to_allegrograph.py script (which generates RDF from cleaned_data.json and pushes it)
        python_executable = sys.executable
        push_script = base_dir / 'push_to_allegrograph.py'
        
        if not push_script.exists():
            return jsonify({
                'success': False,
                'error': 'push_to_allegrograph.py script not found'
            }), 500
        
        print(f"[Push] Running push_to_allegrograph.py from {base_dir}")
        print(f"[Push] Using connection: {connection['name']} at {connection['host']}:{connection['port']}")
        
        # Set environment variables for the script to use
        env = {
            **dict(os.environ),
            'AGRAPH_HOST': connection['host'],
            'AGRAPH_PORT': str(connection['port']),
            'AGRAPH_REPOSITORY': connection['repository'],
            'AGRAPH_USER': connection['username'],
            'AGRAPH_PASSWORD': connection['password']
        }
        
        result = subprocess.run(
            [python_executable, str(push_script)],
            capture_output=True,
            text=True,
            cwd=base_dir,
            timeout=120,
            env=env
        )
        
        print(f"[Push] Script return code: {result.returncode}")
        print(f"[Push] Script stdout: {result.stdout}")
        print(f"[Push] Script stderr: {result.stderr}")
        
        if result.returncode == 0:
            # Check if the output indicates actual success
            output = result.stdout + result.stderr
            
            # Check for actual success indicators first
            has_success = 'SUCCESS' in output or 'successfully' in output.lower() or 'Triples added:' in output
            
            # Ignore ontology parsing warnings - they don't affect data upload
            if 'Error loading ontology' in output and has_success:
                # Filter out the ontology error from output shown to user
                output_lines = output.split('\n')
                filtered_output = '\n'.join([
                    line for line in output_lines 
                    if not any(err in line for err in ['Error loading ontology', 'Bad syntax', 'Prefix', 'not bound'])
                ])
                output = filtered_output
            
            # Check for critical errors (not ontology warnings)
            critical_errors = ['MALFORMED DATA', 'Upload failed', 'Failed to create repository']
            if any(err in output for err in critical_errors):
                return jsonify({
                    'success': False,
                    'error': 'RDF generation or upload failed. Check logs.',
                    'output': output
                }), 500
            
            return jsonify({
                'success': True,
                'message': f'Data successfully pushed to AllegroGraph ({connection["name"]})!',
                'output': output
            })
        else:
            error_msg = result.stderr if result.stderr else result.stdout
            return jsonify({
                'success': False,
                'error': f'Error: {error_msg}'
            }), 500
    
    except subprocess.TimeoutExpired:
        return jsonify({'success': False, 'error': 'Operation timed out'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/ai-status', methods=['GET'])
def check_ai_status():
    """
    Check if local Ollama AI service is available and operational.
    
    Returns:
        JSON response:
        {
            "success": true,
            "available": bool,
            "model": "llama3" or null
        }
        
    Note:
        AI service runs locally in Docker container. No external API calls.
    """
    try:
        mapper = SmartMapper()
        available = mapper.is_available()
        return jsonify({
            'success': True,
            'available': available,
            'model': 'llama3' if available else None
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/file-columns', methods=['GET'])
def get_file_columns():
    """Get columns from the uploaded file"""
    import pandas as pd
    try:
        base_dir = Path('/workspace')
        excel_path = base_dir / 'data.xlsx'
        
        if excel_path.exists():
            df = pd.read_excel(excel_path, nrows=0)  # Read header only
            return jsonify({
                'success': True,
                'columns': df.columns.tolist()
            })
            
        # Check for JSON in uploads
        uploads_dir = base_dir / 'uploads'
        if uploads_dir.exists():
            json_files = list(uploads_dir.glob('*.json'))
            if json_files:
                with open(json_files[0], 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list) and len(data) > 0:
                        return jsonify({
                            'success': True,
                            'columns': list(data[0].keys())
                        })
        
        return jsonify({'success': False, 'error': 'No data file found'}), 404
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/ai-models', methods=['GET'])
def get_ai_models():
    """
    List all locally available LLM models from Ollama.
    
    Returns:
        JSON response:
        {
            "success": true,
            "models": [{"name": str, "size": int}, ...]
        }
        
    Note:
        Returns only models downloaded to local system.
        No external API calls - all models run on-premises.
    """
    try:
        mapper = SmartMapper()
        if not mapper.is_available():
            return jsonify({'success': False, 'error': 'AI service unavailable'}), 503
            
        models = mapper.list_models()
        return jsonify({
            'success': True,
            'models': models
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/pull-model', methods=['POST'])
def pull_model():
    """
    Pull (download) an AI model from Ollama.
    This endpoint triggers the model download in a background thread.
    The download may take several minutes depending on model size.
    Users should refresh the model list to check when the download is complete.
    """
    try:
        data = request.get_json()
        model_name = data.get('model', '').strip()
        
        if not model_name:
            return jsonify({
                'success': False, 
                'error': 'Model name is required. Visit https://ollama.com/library to find available models.'
            }), 400
        
        # Validate model name format (basic check)
        if not model_name or '/' in model_name[0] or model_name.startswith('.'):
            return jsonify({
                'success': False,
                'error': 'Invalid model name format. Use format like "llama3.2", "mistral", or "phi3".'
            }), 400
            
        mapper = SmartMapper()
        
        # Check if Ollama service is available
        if not mapper.is_available():
            return jsonify({
                'success': False,
                'error': 'Ollama service is not available. Please ensure Ollama is running.'
            }), 503
        
        # Check if model already exists
        existing_models = mapper.list_models()
        if any(m.get('name', '').startswith(model_name) for m in existing_models):
            return jsonify({
                'success': True,
                'message': f'Model "{model_name}" is already available.',
                'already_exists': True
            })
        
        # Start model download in background thread
        import threading
        def run_pull():
            try:
                print(f"Starting model pull: {model_name}")
                response = mapper.pull_model(model_name)
                if response:
                    # Consume the streaming response
                    for line in response.iter_lines():
                        if line:
                            print(f"Pull progress: {line.decode('utf-8')}")
                print(f"Model pull completed: {model_name}")
            except Exception as e:
                print(f"Model pull failed for {model_name}: {str(e)}")
                
        threading.Thread(target=run_pull, daemon=True).start()
        
        return jsonify({
            'success': True,
            'message': f'Started downloading model "{model_name}". This may take several minutes depending on model size. Refresh the model list to check when it\'s available.',
            'model_name': model_name
        })
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': f'Failed to start model download: {str(e)}'
        }), 500


@app.route('/api/apply-mapping', methods=['POST'])
def apply_mapping():
    """Apply column mapping to the uploaded file"""
    import pandas as pd
    try:
        data = request.get_json()
        mapping = data.get('mapping')
        
        if not mapping:
            return jsonify({'success': False, 'error': 'Mapping required'}), 400
            
        # Filter out nulls/empty mappings
        rename_dict = {k: v for k, v in mapping.items() if v}
        
        if not rename_dict:
            return jsonify({'success': True, 'message': 'No changes needed'})
            
        base_dir = Path('/workspace')
        excel_path = base_dir / 'data.xlsx'
        
        if excel_path.exists():
            df = pd.read_excel(excel_path)
            df.rename(columns=rename_dict, inplace=True)
            df.to_excel(excel_path, index=False)
            return jsonify({'success': True, 'message': 'Excel file updated'})
            
        # Check JSON
        uploads_dir = base_dir / 'uploads'
        if uploads_dir.exists():
            json_files = list(uploads_dir.glob('*.json'))
            if json_files:
                file_path = json_files[0]
                with open(file_path, 'r') as f:
                    json_data = json.load(f)
                
                # Update keys in all records
                new_data = []
                for record in json_data:
                    new_record = {}
                    for k, v in record.items():
                        new_key = rename_dict.get(k, k)
                        new_record[new_key] = v
                    new_data.append(new_record)
                    
                with open(file_path, 'w') as f:
                    json.dump(new_data, f, indent=2)
                    
                return jsonify({'success': True, 'message': 'JSON file updated'})
                
        return jsonify({'success': False, 'error': 'No file found to update'}), 404
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/data-preview', methods=['GET'])
def get_data_preview():
    """Get preview of uploaded data (first 10 rows with column info)"""
    import pandas as pd
    try:
        base_dir = Path('/workspace')
        excel_path = base_dir / 'data.xlsx'
        
        if excel_path.exists():
            df = pd.read_excel(excel_path, nrows=10)
            # Replace NaN with None (which becomes null in JSON)
            df = df.where(pd.notna(df), None)
            return jsonify({
                'success': True,
                'preview': df.to_dict('records'),
                'columns': df.columns.tolist(),
                'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
                'row_count': len(pd.read_excel(excel_path))
            })
            
        uploads_dir = base_dir / 'uploads'
        if uploads_dir.exists():
            json_files = list(uploads_dir.glob('*.json'))
            if json_files:
                with open(json_files[0], 'r') as f:
                    data = json.load(f)
                    preview = data[:10] if isinstance(data, list) else [data]
                    return jsonify({
                        'success': True,
                        'preview': preview,
                        'columns': list(preview[0].keys()) if preview else [],
                        'row_count': len(data) if isinstance(data, list) else 1
                    })
        
        return jsonify({'success': False, 'error': 'No data file found'}), 404
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/transform-column', methods=['POST'])
def transform_column():
    """Apply transformations to a specific column"""
    import pandas as pd
    import re
    from datetime import datetime as dt
    
    try:
        data = request.get_json()
        column_name = data.get('column')
        transform_type = data.get('transform_type')
        options = data.get('options', {})
        
        if not column_name or not transform_type:
            return jsonify({'success': False, 'error': 'Column name and transform type required'}), 400
        
        base_dir = Path('/workspace')
        excel_path = base_dir / 'data.xlsx'
        
        if excel_path.exists():
            df = pd.read_excel(excel_path)
        else:
            uploads_dir = base_dir / 'uploads'
            json_files = list(uploads_dir.glob('*.json'))
            if json_files:
                df = pd.read_json(json_files[0])
            else:
                return jsonify({'success': False, 'error': 'No data file found'}), 404
        
        if column_name not in df.columns:
            return jsonify({'success': False, 'error': f'Column "{column_name}" not found'}), 404
        
        # Apply transformation
        if transform_type == 'to_categorical':
            # Convert numerical ranges to categories
            # First check if column is actually numerical
            if pd.api.types.is_numeric_dtype(df[column_name]):
                bins = options.get('bins', [0, 18, 35, 60, 100])
                labels = options.get('labels', ['Child', 'Young Adult', 'Adult', 'Senior'])
                df[column_name] = pd.cut(df[column_name], bins=bins, labels=labels, include_lowest=True)
            else:
                return jsonify({
                    'success': False, 
                    'error': f'Column "{column_name}" is not numerical. It contains: {df[column_name].dtype}. Use this transformation only on numerical columns like age.'
                }), 400
            
        elif transform_type == 'to_numerical':
            # Convert categorical to numerical
            mapping = options.get('mapping', {})
            if mapping:
                df[column_name] = df[column_name].map(mapping)
            else:
                # Auto-detect common binary patterns
                unique_vals = df[column_name].dropna().unique()
                if len(unique_vals) <= 2:
                    # Binary column - use 1/0
                    # Check for Yes/No pattern
                    unique_lower = [str(v).lower() for v in unique_vals]
                    if 'yes' in unique_lower or 'no' in unique_lower:
                        df[column_name] = df[column_name].apply(
                            lambda x: 1 if str(x).lower() in ['yes', 'y', 'true', '1'] else 0 if str(x).lower() in ['no', 'n', 'false', '0'] else None
                        )
                    else:
                        # Generic binary: first unique = 0, second = 1
                        df[column_name] = df[column_name].map({unique_vals[0]: 0, unique_vals[1]: 1})
                else:
                    # Multi-category: auto-generate numeric codes
                    df[column_name] = pd.Categorical(df[column_name]).codes
                
        elif transform_type == 'normalize_case':
            # Convert text case
            case_type = options.get('case', 'title')  # title, upper, lower
            # Preserve NaN values
            mask = df[column_name].notna()
            if case_type == 'title':
                df.loc[mask, column_name] = df.loc[mask, column_name].astype(str).str.title()
            elif case_type == 'upper':
                df.loc[mask, column_name] = df.loc[mask, column_name].astype(str).str.upper()
            elif case_type == 'lower':
                df.loc[mask, column_name] = df.loc[mask, column_name].astype(str).str.lower()
                
        elif transform_type == 'format_date':
            # Standardize date format
            target_format = options.get('format', '%Y-%m-%d')
            df[column_name] = pd.to_datetime(df[column_name], errors='coerce').dt.strftime(target_format)
            
        elif transform_type == 'clean_text':
            # Remove special characters, extra spaces
            df[column_name] = df[column_name].fillna('').astype(str).apply(
                lambda x: re.sub(r'[^\w\s-]', '', x).strip() if x not in ['nan', 'None', ''] else ''
            )
            
        elif transform_type == 'fill_missing':
            # Fill missing values (NaN, None, empty strings)
            fill_value = options.get('value', 'Unknown')
            # Replace NaN with fill_value
            df[column_name] = df[column_name].fillna(fill_value)
            # Also replace empty strings if they exist
            df[column_name] = df[column_name].replace('', fill_value)
            df[column_name] = df[column_name].replace('nan', fill_value)
            df[column_name] = df[column_name].replace('None', fill_value)
            
        else:
            return jsonify({'success': False, 'error': f'Unknown transform type: {transform_type}'}), 400
        
        # Save back
        if excel_path.exists():
            df.to_excel(excel_path, index=False)
        else:
            df.to_json(json_files[0], orient='records', indent=2)
        
        # Get preview with proper null handling
        preview_data = df[column_name].head(5)
        preview_data = preview_data.where(pd.notna(preview_data), None)
        
        return jsonify({
            'success': True,
            'message': f'Transformation "{transform_type}" applied to column "{column_name}"',
            'preview': preview_data.tolist()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/suggest-mapping', methods=['POST'])
def suggest_mapping():
    """
    Use local AI to intelligently map source columns to CDM schema.
    
    This endpoint uses a local LLM to analyze source data column names
    and suggest appropriate mappings to the Common Data Model schema.
    The AI is strictly constrained to only suggest fields that actually
    exist in models.CDM_SCHEMA, preventing hallucination.
    
    Request JSON:
        {
            "columns": [array of source column names],
            "model": str (optional, default 'llama3'),
            "auto_transform": bool (optional, default true)
        }
        
    Returns:
        JSON response:
        {
            "success": true,
            "mapping": {source_col: "Entity.field" or null},
            "transformations_applied": [{"column": str, "transformation": str}]
        }
        
    Note:
        - All AI inference happens locally - GDPR compliant
        - Requires Ollama service running (docker-compose --profile ai up)
        - AI cannot suggest fields not defined in CDM schema
        - Auto-transformation applies recommended data cleaning
        - Processing time: 30s-5min depending on model size
    """
    import pandas as pd
    import re
    from datetime import datetime as dt
    
    try:
        data = request.get_json()
        source_columns = data.get('columns', [])
        model = data.get('model', 'llama3')
        auto_transform = data.get('auto_transform', True)
        
        # Get CDM schema from models
        from models import CDM_SCHEMA
        
        mapper = SmartMapper()
        if not mapper.is_available():
            return jsonify({
                'success': False,
                'error': 'Ollama AI service is not available. Please start it with: docker-compose --profile ai up'
            }), 503
            
        result = mapper.suggest_mapping(source_columns, CDM_SCHEMA, model=model)
        
        # Extract mapping and transformations from AI response
        if isinstance(result, dict) and 'mapping' in result:
            mapping = result.get('mapping', {})
            transformations = result.get('transformations', {})
        else:
            # Fallback for old format (just mapping)
            mapping = result
            transformations = {}
        
        # Apply transformations automatically if requested
        applied_transformations = []
        if auto_transform and transformations:
            base_dir = Path('/workspace')
            excel_path = base_dir / 'data.xlsx'
            
            if excel_path.exists():
                df = pd.read_excel(excel_path)
                
                for column_name, transform_type in transformations.items():
                    if column_name not in df.columns:
                        continue
                        
                    try:
                        # Apply the transformation (all 6 types)
                        if transform_type == 'fill_missing':
                            df[column_name] = df[column_name].fillna('Unknown')
                            df[column_name] = df[column_name].replace('', 'Unknown')
                            df[column_name] = df[column_name].replace('nan', 'Unknown')
                            df[column_name] = df[column_name].replace('None', 'Unknown')
                            
                        elif transform_type == 'normalize_case':
                            mask = df[column_name].notna()
                            df.loc[mask, column_name] = df.loc[mask, column_name].astype(str).str.title()
                            
                        elif transform_type == 'format_date':
                            df[column_name] = pd.to_datetime(df[column_name], errors='coerce').dt.strftime('%Y-%m-%d')
                            
                        elif transform_type == 'clean_text':
                            df[column_name] = df[column_name].fillna('').astype(str).apply(
                                lambda x: re.sub(r'[^\w\s-]', '', x).strip() if x not in ['nan', 'None', ''] else ''
                            )
                            
                        elif transform_type == 'to_numerical':
                            # Convert Yes/No and other categorical to numbers
                            unique_vals = df[column_name].dropna().unique()
                            if len(unique_vals) <= 2:
                                unique_lower = [str(v).lower() for v in unique_vals]
                                if 'yes' in unique_lower or 'no' in unique_lower:
                                    df[column_name] = df[column_name].apply(
                                        lambda x: 1 if str(x).lower() in ['yes', 'y', 'true', '1'] else 0 if str(x).lower() in ['no', 'n', 'false', '0'] else None
                                    )
                                else:
                                    df[column_name] = df[column_name].map({unique_vals[0]: 0, unique_vals[1]: 1})
                            else:
                                df[column_name] = pd.Categorical(df[column_name]).codes
                                
                        elif transform_type == 'to_categorical':
                            # Only apply to numerical columns
                            if pd.api.types.is_numeric_dtype(df[column_name]):
                                df[column_name] = pd.cut(df[column_name], bins=[0, 18, 35, 60, 100], 
                                                        labels=['Child', 'Young Adult', 'Adult', 'Senior'], 
                                                        include_lowest=True)
                        
                        applied_transformations.append({
                            'column': column_name,
                            'transformation': transform_type
                        })
                    except Exception as e:
                        # Log but don't fail the whole process
                        print(f"Warning: Failed to apply {transform_type} to {column_name}: {e}")
                
                # Save if any transformations were applied
                if applied_transformations:
                    df.to_excel(excel_path, index=False)
        
        return jsonify({
            'success': True,
            'mapping': mapping,
            'transformations_applied': applied_transformations
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# FAIR DATA POINT ENDPOINTS
# ============================================================================

@app.route('/api/fair/info', methods=['GET'])
def get_fair_data_point_info():
    """
    Get EEPA FAIR Data Point metadata and general information.
    
    Returns:
        JSON response:
        {
            "success": true,
            "info": {
                "title": str,
                "description": str,
                "contact": str (email),
                "publisher": str,
                "version": str,
                "catalogs": [array of catalog URLs]
            }
        }
        
    Note:
        This provides overview of the FAIR Data Point including contact
        information for requesting access to datasets.
    """
    try:
        # Use verify_ssl=False to handle expired/self-signed certificates
        fdp_client = FairDataPointClient(verify_ssl=False)
        fdp_info = fdp_client.get_fdp_metadata()
        
        if not fdp_info:
            return jsonify({
                'success': False,
                'error': 'Unable to fetch FAIR Data Point metadata'
            }), 500
        
        return jsonify({
            'success': True,
            'info': fdp_info
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/fair/catalogs', methods=['GET'])
def get_fair_catalogs():
    """
    Get all available data catalogs from EEPA FAIR Data Point.
    
    Returns:
        JSON response:
        {
            "success": true,
            "catalogs": [
                {
                    "id": str (URL),
                    "title": str,
                    "description": str,
                    "publisher": str,
                    "contact": str (from FDP info),
                    "license": str (URL),
                    "dataset_count": int,
                    "themes": [array of theme URLs],
                    "issued": str (ISO datetime),
                    "modified": str (ISO datetime)
                },
                ...
            ],
            "count": int
        }
        
    Note:
        Users can browse catalogs to understand available datasets before
        requesting access credentials from the data owner.
    """
    try:
        # Use verify_ssl=False to handle expired/self-signed certificates
        fdp_client = FairDataPointClient(verify_ssl=False)
        
        # Get FDP info for contact information
        fdp_info = fdp_client.get_fdp_metadata()
        contact_email = fdp_info.get('contact') if fdp_info else None
        
        # Get all catalogs
        catalogs = fdp_client.get_catalogs()
        
        # Enhance catalogs with contact info
        # (dataset_count is already calculated in get_catalogs)
        enhanced_catalogs = []
        for catalog in catalogs:
            catalog['contact'] = contact_email
            enhanced_catalogs.append(catalog)
        
        return jsonify({
            'success': True,
            'catalogs': enhanced_catalogs,
            'count': len(enhanced_catalogs)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/fair/catalogs/<path:catalog_id>', methods=['GET'])
def get_fair_catalog_details(catalog_id: str):
    """
    Get detailed information about a specific catalog including datasets.
    
    Args:
        catalog_id: URL-encoded catalog ID (URL)
        
    Returns:
        JSON response with catalog details and list of datasets.
        
    Note:
        This allows users to explore what data is available in a catalog
        before requesting access.
    """
    try:
        # Decode the catalog URL
        import urllib.parse
        catalog_url = urllib.parse.unquote(catalog_id)
        
        # Use verify_ssl=False to handle expired/self-signed certificates
        fdp_client = FairDataPointClient(verify_ssl=False)
        catalog = fdp_client.get_catalog_details(catalog_url)
        
        if not catalog:
            return jsonify({
                'success': False,
                'error': 'Catalog not found'
            }), 404
        
        # Get datasets in this catalog
        datasets = fdp_client.get_datasets(catalog_url)
        catalog['datasets_details'] = datasets
        
        return jsonify({
            'success': True,
            'catalog': catalog
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
