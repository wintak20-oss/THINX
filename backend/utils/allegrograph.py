"""
AllegroGraph Client for SPARQL queries and RDF operations
"""

from franz.openrdf.connect import ag_connect
from franz.openrdf.sail.allegrographserver import AllegroGraphServer
from franz.openrdf.query.query import QueryLanguage
import traceback
import os


class AllegroGraphClient:
    """Client for connecting to and querying AllegroGraph"""
    
    _repository_checked = {}  # Class variable to track which repos have been verified
    
    def __init__(self, host: str, port: int, repository: str,
                 username: str, password: str):
        # If user enters 'localhost', convert to 'allegrograph' for Docker networking
        # The backend is inside Docker and needs to use container names
        if host == 'localhost' or host == '127.0.0.1':
            self.host = os.getenv('AGRAPH_HOST', 'ag1jdz6nqkhfjj72.allegrograph.cloud')
            print(f"[AllegroGraph] Converting localhost to '{self.host}' for Docker networking")
        else:
            self.host = host
        self.port = port
        self.repository = repository
        self.username = username
        self.password = password
        self.connection = None
        self._repo_key = f"{self.host}:{self.port}/{self.repository}"
    
    def connect(self):
        """Establish connection to AllegroGraph, creating repository if needed"""
        try:
            print(f"[AllegroGraph] Connecting to host='{self.host}', port={self.port}, repo='{self.repository}'")
            print(f"[AllegroGraph] Username: '{self.username}'")
            
            # First, ensure the repository exists (create if not) - only check once per repo
            if self._repo_key not in AllegroGraphClient._repository_checked:
                try:
                    server = AllegroGraphServer(
                        host=self.host,
                        port=self.port,
                        user=self.username,
                        password=self.password
                    )
                    
                    catalog = server.openCatalog()
                    
                    # Try to list repositories to check if ours exists
                    try:
                        repos = catalog.listRepositories()
                        repo_names = [r.getName() for r in repos]
                        
                        if self.repository not in repo_names:
                            print(f"[AllegroGraph] Repository '{self.repository}' does not exist. Creating...")
                            # Create repository without clearing existing data
                            catalog.createRepository(self.repository)
                            print(f"[AllegroGraph] Repository '{self.repository}' created successfully")
                        else:
                            print(f"[AllegroGraph] Repository '{self.repository}' already exists (preserving existing data)")
                    except AttributeError:
                        # Older API version - skip creation to avoid clearing data
                        print(f"[AllegroGraph] Cannot verify repository existence, assuming it exists (preserving data)")
                    
                    # Mark this repository as checked
                    AllegroGraphClient._repository_checked[self._repo_key] = True
                except Exception as repo_error:
                    print(f"[AllegroGraph] Warning during repository check/creation: {repo_error}")
                    # Continue anyway - repository might exist
            else:
                print(f"[AllegroGraph] Repository '{self.repository}' already verified, skipping check")
            
            # Now connect to the repository
            self.connection = ag_connect(
                self.repository,
                host=self.host,
                port=self.port,
                user=self.username,
                password=self.password
            )
            print(f"[AllegroGraph] Successfully connected to '{self.repository}'")
            return True
        except Exception as e:
            print(f"Failed to connect to AllegroGraph: {e}")
            traceback.print_exc()
            return False
    
    def test_connection(self) -> bool:
        """Test if connection is valid"""
        try:
            if self.connect():
                # Try a simple query
                result = self.connection.size()
                self.close()
                return True
            return False
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
    
    def execute_query(self, query: str, close_after: bool = True) -> list:
        """Execute SPARQL query and return results
        
        Args:
            query: SPARQL query string
            close_after: Whether to close connection after query (default True)
        """
        results = []
        
        try:
            if not self.connection:
                if not self.connect():
                    raise Exception("Failed to connect to AllegroGraph")
            
            # Execute query
            tuple_query = self.connection.prepareTupleQuery(QueryLanguage.SPARQL, query)
            result = tuple_query.evaluate()
            
            # Process results
            binding_names = result.getBindingNames()
            
            for binding_set in result:
                row = {}
                for name in binding_names:
                    value = binding_set.getValue(name)
                    if value:
                        row[name] = str(value)
                    else:
                        row[name] = None
                results.append(row)
            
            result.close()
            
        except Exception as e:
            print(f"Query execution failed: {e}")
            traceback.print_exc()
            raise
        finally:
            if close_after and self.connection:
                self.close()
        
        return results
    
    def get_statistics(self) -> dict:
        """Get repository statistics"""
        stats = {
            'total_triples': 0,
            'total_victims': 0,
            'total_incidents': 0,
            'total_locations': 0
        }
        
        try:
            if not self.connection:
                if not self.connect():
                    raise Exception("Failed to connect to AllegroGraph")
            
            # Get total triples
            stats['total_triples'] = self.connection.size()
            print(f"[Statistics] Repository has {stats['total_triples']} total triples")
            
            # Count victims - use rdf:type explicitly and check both forms
            victim_query = """
            PREFIX hds: <http://example.org/hds#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            SELECT (COUNT(DISTINCT ?victim) as ?count)
            WHERE {
                ?victim rdf:type hds:Victim .
            }
            """
            result = self.execute_query(victim_query, close_after=False)
            if result and len(result) > 0:
                count_val = result[0].get('count', '0')
                # Strip RDF type annotations like "100"^^<http://www.w3.org/2001/XMLSchema#integer>
                count_str = str(count_val).split('^^')[0].strip('"')
                stats['total_victims'] = int(count_str) if count_str and count_str != '0' else 0
                print(f"[Statistics] Found {stats['total_victims']} victims (raw: {count_val})")
            
            # Count crimes - check if Incident entities exist
            crime_query = """
            PREFIX hds: <http://example.org/hds#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            SELECT (COUNT(DISTINCT ?incident) as ?count)
            WHERE {
                ?incident rdf:type hds:Incident .
            }
            """
            result = self.execute_query(crime_query, close_after=False)
            if result and len(result) > 0:
                count_val = result[0].get('count', '0')
                # Strip RDF type annotations
                count_str = str(count_val).split('^^')[0].strip('"')
                stats['total_incidents'] = int(count_str) if count_str and count_str != '0' else 0
                print(f"[Statistics] Found {stats['total_incidents']} incidents (raw: {count_val})")
            
            # Count borders - check if Location entities exist
            border_query = """
            PREFIX hds: <http://example.org/hds#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            SELECT (COUNT(DISTINCT ?location) as ?count)
            WHERE {
                ?location rdf:type hds:Location .
            }
            """
            result = self.execute_query(border_query, close_after=False)
            if result and len(result) > 0:
                count_val = result[0].get('count', '0')
                # Strip RDF type annotations
                count_str = str(count_val).split('^^')[0].strip('"')
                stats['total_locations'] = int(count_str) if count_str and count_str != '0' else 0
                print(f"[Statistics] Found {stats['total_locations']} locations (raw: {count_val})")
            
        except Exception as e:
            print(f"Failed to get statistics: {e}")
            traceback.print_exc()
        finally:
            if self.connection:
                self.close()
        
        return stats
    
    def close(self):
        """Close connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
