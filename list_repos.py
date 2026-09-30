#!/usr/bin/env python3
"""
List all repositories in AllegroGraph
"""

import requests
from requests.auth import HTTPBasicAuth

AGRAPH_HOST = "https://ag1s5fv23e82hv78.allegrograph.cloud"
AGRAPH_PORT = 10035
AGRAPH_USER = "Admin"
AGRAPH_PASSWORD = "moVzCHbrYZ9XdRipk18Pg1"

BASE_URL = f"http://{AGRAPH_HOST}:{AGRAPH_PORT}"

def list_repositories():
    """List all repositories in all catalogs"""
    
    # Get root catalog repositories
    url = f"{BASE_URL}/repositories"
    
    try:
        response = requests.get(
            url,
            auth=HTTPBasicAuth(AGRAPH_USER, AGRAPH_PASSWORD),
            headers={"Accept": "application/json"}
        )
        response.raise_for_status()
        
        data = response.json()
        print("Repositories found in AllegroGraph:")
        print("=" * 60)
        
        if isinstance(data, list):
            for repo in data:
                repo_id = repo.get("id", "Unknown")
                repo_title = repo.get("title", "No title")
                print(f"  - {repo_id} ({repo_title})")
        else:
            print(data)
            
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"Error listing repositories: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")
        return []

if __name__ == "__main__":
    list_repositories()
