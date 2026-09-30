"""
Data Models for Connection Manager
Common Data Model (CDM) definitions
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import hashlib


class User:
    """Represents a user account"""
    
    def __init__(self, username: str, password_hash: str = None, user_id: str = None, 
                 is_admin: bool = False, email: str = None, full_name: str = None):
        self.id = user_id or str(uuid.uuid4())
        self.username = username
        self.password_hash = password_hash
        self.is_admin = is_admin
        self.email = email
        self.full_name = full_name
        self.created_at = datetime.utcnow().isoformat()
        self.last_login = None
    
    def to_dict(self) -> Dict:
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'password_hash': self.password_hash,
            'is_admin': self.is_admin,
            'email': self.email,
            'full_name': self.full_name,
            'created_at': self.created_at,
            'last_login': self.last_login
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'User':
        """Create user from dictionary"""
        user = User(
            user_id=data['id'],
            username=data['username'],
            password_hash=data['password_hash'],
            is_admin=data.get('is_admin', False),
            email=data.get('email'),
            full_name=data.get('full_name')
        )
        user.last_login = data.get('last_login')
        return user
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str) -> bool:
        """Verify password matches hash"""
        return self.password_hash == User.hash_password(password)


class Connection:
    """Represents an AllegroGraph connection with optional FAIR Data Point metadata"""
    
    def __init__(self, name: str, connection_type: str = 'allegrograph',
                 host: str = '', port: int = 10035, repository: str = '',
                 username: str = '', password: str = '',
                 description: str = '', connection_id: str = None, is_active: bool = False,
                 user_id: str = None,
                 # FAIR Data Point metadata fields
                 catalog_id: str = None, catalog_title: str = None,
                 catalog_publisher: str = None, catalog_contact: str = None,
                 catalog_license: str = None, catalog_themes: List[str] = None,
                 dataset_count: int = 0):
        self.id = connection_id or str(uuid.uuid4())
        self.name = name
        self.type = connection_type  # 'allegrograph'
        self.host = host
        self.port = port
        self.repository = repository
        self.username = username
        self.password = password
        self.description = description
        self.is_active = is_active
        self.user_id = user_id  # Owner of this connection
        # FAIR Data Point metadata
        self.catalog_id = catalog_id  # URL of the catalog in FDP
        self.catalog_title = catalog_title  # Human-readable catalog name
        self.catalog_publisher = catalog_publisher  # Data owner/publisher
        self.catalog_contact = catalog_contact  # Contact email for access
        self.catalog_license = catalog_license  # License URL
        self.catalog_themes = catalog_themes or []  # Theme URLs
        self.dataset_count = dataset_count  # Number of datasets in catalog
        self.created_at = datetime.utcnow().isoformat()
        self.updated_at = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict:
        """Convert connection to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'host': self.host,
            'port': self.port,
            'repository': self.repository,
            'username': self.username,
            'password': self.password,
            'description': self.description,
            'is_active': self.is_active,
            'user_id': self.user_id,
            'catalog_id': self.catalog_id,
            'catalog_title': self.catalog_title,
            'catalog_publisher': self.catalog_publisher,
            'catalog_contact': self.catalog_contact,
            'catalog_license': self.catalog_license,
            'catalog_themes': self.catalog_themes,
            'dataset_count': self.dataset_count,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Connection':
        """Create connection from dictionary"""
        return Connection(
            connection_id=data.get('id'),
            name=data['name'],
            connection_type=data.get('type', 'allegrograph'),
            host=data.get('host', ''),
            port=data.get('port', 10035),
            repository=data.get('repository', ''),
            username=data.get('username', ''),
            password=data.get('password', ''),
            description=data.get('description', ''),
            is_active=data.get('is_active', False),
            user_id=data.get('user_id'),
            catalog_id=data.get('catalog_id'),
            catalog_title=data.get('catalog_title'),
            catalog_publisher=data.get('catalog_publisher'),
            catalog_contact=data.get('catalog_contact'),
            catalog_license=data.get('catalog_license'),
            catalog_themes=data.get('catalog_themes', []),
            dataset_count=data.get('dataset_count', 0)
        )


class UserManager:
    """Manages user accounts and authentication"""
    
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self._ensure_storage()
    
    def _ensure_storage(self):
        """Create storage file if it doesn't exist"""
        if not self.storage_path.exists():
            # Create default admin user
            admin = User('admin', User.hash_password('admin'), is_admin=True)
            self.storage_path.write_text(json.dumps([admin.to_dict()], indent=2))
    
    def _load_users(self) -> List[Dict]:
        """Load users from storage"""
        try:
            return json.loads(self.storage_path.read_text())
        except Exception as e:
            print(f"Error loading users: {e}")
            return []
    
    def _save_users(self, users: List[Dict]):
        """Save users to storage"""
        self.storage_path.write_text(json.dumps(users, indent=2))
    
    def authenticate(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user and return user dict if valid"""
        users = self._load_users()
        for user_data in users:
            user = User.from_dict(user_data)
            if user.username == username and user.verify_password(password):
                # Update last login
                user_data['last_login'] = datetime.utcnow().isoformat()
                self._save_users(users)
                # Return user data without password hash
                user_dict = user.to_dict()
                return user_dict
        return None
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        users = self._load_users()
        for user in users:
            if user['id'] == user_id:
                return user
        return None
    
    def get_all_users(self) -> List[Dict]:
        """Get all users (admin only)"""
        users = self._load_users()
        # Return without password hashes
        return [{k: v for k, v in user.items() if k != 'password_hash'} for user in users]
    
    def create_user(self, username: str, password: str, is_admin: bool = False,
                   email: str = None, full_name: str = None) -> Dict:
        """Create new user"""
        users = self._load_users()
        
        # Check if username exists
        for user in users:
            if user['username'] == username:
                raise ValueError(f"Username '{username}' already exists")
        
        new_user = User(username, User.hash_password(password), 
                       is_admin=is_admin, email=email, full_name=full_name)
        users.append(new_user.to_dict())
        self._save_users(users)
        return new_user.to_dict()
    
    def update_user(self, user_id: str, updates: Dict) -> Optional[Dict]:
        """Update user details (admin only)"""
        users = self._load_users()
        for i, user in enumerate(users):
            if user['id'] == user_id:
                # Update allowed fields
                if 'email' in updates:
                    user['email'] = updates['email']
                if 'full_name' in updates:
                    user['full_name'] = updates['full_name']
                if 'is_admin' in updates:
                    user['is_admin'] = updates['is_admin']
                if 'password' in updates:
                    user['password_hash'] = User.hash_password(updates['password'])
                
                users[i] = user
                self._save_users(users)
                return {k: v for k, v in user.items() if k != 'password_hash'}
        return None
    
    def delete_user(self, user_id: str) -> bool:
        """Delete user (admin only, cannot delete last admin)"""
        users = self._load_users()
        
        # Count admins
        admin_count = sum(1 for u in users if u.get('is_admin', False))
        user_to_delete = next((u for u in users if u['id'] == user_id), None)
        
        if user_to_delete and user_to_delete.get('is_admin', False) and admin_count <= 1:
            raise ValueError("Cannot delete the last admin user")
        
        initial_count = len(users)
        users = [u for u in users if u['id'] != user_id]
        
        if len(users) < initial_count:
            self._save_users(users)
            return True
        return False


class ConnectionManager:
    """Manages connection persistence and operations"""
    
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self._ensure_storage()
    
    def _ensure_storage(self):
        """Create storage file if it doesn't exist"""
        if not self.storage_path.exists():
            self.storage_path.write_text('[]')
    
    def _load_connections(self) -> List[Dict]:
        """Load connections from storage"""
        try:
            return json.loads(self.storage_path.read_text())
        except Exception as e:
            print(f"Error loading connections: {e}")
            return []
    
    def _save_connections(self, connections: List[Dict]):
        """Save connections to storage"""
        self.storage_path.write_text(json.dumps(connections, indent=2))
    
    def get_all_connections(self, user_id: str = None) -> List[Dict]:
        """Get all connections, optionally filtered by user_id"""
        connections = self._load_connections()
        if user_id:
            return [conn for conn in connections if conn.get('user_id') == user_id]
        return connections
    
    def get_connection(self, connection_id: str) -> Optional[Dict]:
        """Get connection by ID"""
        connections = self._load_connections()
        for conn in connections:
            if conn['id'] == connection_id:
                return conn
        return None
    
    def add_connection(self, connection: Connection) -> Dict:
        """Add new connection"""
        connections = self._load_connections()
        
        # If this is the first connection, make it active
        if len(connections) == 0:
            connection.is_active = True
        
        connections.append(connection.to_dict())
        self._save_connections(connections)
        return connection.to_dict()
    
    def update_connection(self, connection_id: str, data: Dict) -> Optional[Dict]:
        """Update existing connection"""
        connections = self._load_connections()
        
        for i, conn in enumerate(connections):
            if conn['id'] == connection_id:
                # Update fields
                conn.update(data)
                conn['updated_at'] = datetime.utcnow().isoformat()
                connections[i] = conn
                self._save_connections(connections)
                return conn
        
        return None
    
    def delete_connection(self, connection_id: str) -> bool:
        """Delete connection"""
        connections = self._load_connections()
        initial_count = len(connections)
        
        connections = [conn for conn in connections if conn['id'] != connection_id]
        
        if len(connections) < initial_count:
            self._save_connections(connections)
            return True
        
        return False
    
    def set_active_connection(self, connection_id: str) -> bool:
        """Set a connection as active (deactivate others)"""
        connections = self._load_connections()
        found = False
        
        for conn in connections:
            if conn['id'] == connection_id:
                conn['is_active'] = True
                found = True
            else:
                conn['is_active'] = False
        
        if found:
            self._save_connections(connections)
        
        return found
    
    def get_active_connection(self) -> Optional[Dict]:
        """Get the currently active connection"""
        connections = self._load_connections()
        for conn in connections:
            if conn.get('is_active', False):
                return conn
        return None


# Common Data Model (CDM) Schema Definitions
# This defines the structure of human trafficking data based on hds_cdm.ttl

CDM_SCHEMA = {
    'Victim': {
        'description': 'Person harmed in an incident',
        'fields': [
            {
                'name': 'id',
                'type': 'string',
                'required': True,
                'sensitive': False,
                'gdpr_category': None,
                'description': 'Unique identifier for the victim'
            },
            {
                'name': 'age',
                'type': 'integer',
                'required': False,
                'sensitive': True,
                'gdpr_category': 'personal',
                'description': 'Age of the victim'
            },
            {
                'name': 'gender',
                'type': 'string',
                'required': False,
                'sensitive': True,
                'gdpr_category': 'personal',
                'description': 'Gender of the victim'
            },
            {
                'name': 'nationality',
                'type': 'string',
                'required': False,
                'sensitive': True,
                'gdpr_category': 'special_category',
                'description': 'Nationality of the victim'
            },
            {
                'name': 'maritalStatus',
                'type': 'string',
                'required': False,
                'sensitive': True,
                'gdpr_category': 'personal',
                'description': 'Marital status of the victim'
            },
            {
                'name': 'displacementStatus',
                'type': 'string',
                'required': False,
                'sensitive': True,
                'gdpr_category': 'personal',
                'description': 'Displacement status (Refugee/IDP)'
            }
        ]
    },
    'Incident': {
        'description': 'A security or humanitarian incident',
        'fields': [
            {
                'name': 'id',
                'type': 'string',
                'required': True,
                'sensitive': False,
                'gdpr_category': None,
                'description': 'Unique identifier for the incident'
            },
            {
                'name': 'date',
                'type': 'string',
                'required': False,
                'sensitive': False,
                'gdpr_category': None,
                'description': 'Date of the incident'
            },
            {
                'name': 'type',
                'type': 'string',
                'required': False,
                'sensitive': False,
                'gdpr_category': None,
                'description': 'Type of incident'
            },
            {
                'name': 'description',
                'type': 'string',
                'required': False,
                'sensitive': True,
                'gdpr_category': 'special_category',
                'description': 'Description of the incident'
            }
        ]
    },
    'Trafficker': {
        'description': 'A person engaged in illegal trade of people or goods',
        'fields': [
            {
                'name': 'id',
                'type': 'string',
                'required': True,
                'sensitive': False,
                'gdpr_category': None,
                'description': 'Unique identifier for the trafficker'
            },
            {
                'name': 'name',
                'type': 'string',
                'required': False,
                'sensitive': False,
                'gdpr_category': None,
                'description': 'Name of the trafficker'
            },
            {
                'name': 'nationality',
                'type': 'string',
                'required': False,
                'sensitive': False,
                'gdpr_category': None,
                'description': 'Nationality of the trafficker'
            }
        ]
    },
    'Location': {
        'description': 'A geospatial location',
        'fields': [
            {
                'name': 'id',
                'type': 'string',
                'required': True,
                'sensitive': False,
                'gdpr_category': None,
                'description': 'Unique identifier for the location'
            },
            {
                'name': 'description',
                'type': 'string',
                'required': False,
                'sensitive': False,
                'gdpr_category': None,
                'description': 'Description or name of the location'
            }
        ]
    }
}


def get_cdm_schema():
    """Return the Common Data Model schema"""
    return CDM_SCHEMA


def validate_data_against_cdm(entity_type: str, data: Dict) -> tuple[bool, List[str]]:
    """
    Validate data against CDM schema
    Returns (is_valid, list_of_errors)
    """
    if entity_type not in CDM_SCHEMA:
        return False, [f"Unknown entity type: {entity_type}"]
    
    errors = []
    schema = CDM_SCHEMA[entity_type]
    
    # Check required fields
    for field in schema['fields']:
        if field['required'] and field['name'] not in data:
            errors.append(f"Missing required field: {field['name']}")
    
    # Check data types
    for key, value in data.items():
        field_schema = next((f for f in schema['fields'] if f['name'] == key), None)
        if field_schema:
            expected_type = field_schema['type']
            if expected_type == 'integer' and not isinstance(value, int):
                errors.append(f"Field {key} should be integer, got {type(value).__name__}")
            elif expected_type == 'string' and not isinstance(value, str):
                errors.append(f"Field {key} should be string, got {type(value).__name__}")
            elif expected_type == 'boolean' and not isinstance(value, bool):
                errors.append(f"Field {key} should be boolean, got {type(value).__name__}")
    
    return len(errors) == 0, errors
