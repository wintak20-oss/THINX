#!/usr/bin/env python3
"""
Federated Query Script for AllegroGraph
Queries multiple repositories and combines results using the AllegroGraph REST API
"""

import requests
from requests.auth import HTTPBasicAuth
import pandas as pd
from typing import List, Dict
import json

# Configuration
AGRAPH_HOST = "localhost"
AGRAPH_PORT = 10035

# Repositories to query with their credentials
# Note: Using admin credentials for now
REPOSITORIES = [
    {"name": "danieltesfa", "username": "admin", "password": "admin123"},
    {"name": "kaismits", "username": "admin", "password": "admin123"},
    {"name": "morganewirtz", "username": "admin", "password": "admin123"}
]

# Base URL
BASE_URL = f"http://{AGRAPH_HOST}:{AGRAPH_PORT}"


def execute_sparql_query(repo_config: Dict, query: str) -> List[Dict]:
    """
    Execute a SPARQL query against a specific repository
    
    Args:
        repo_config: Dictionary containing repository name, username, and password
        query: SPARQL query string
        
    Returns:
        List of result bindings
    """
    repo_name = repo_config["name"]
    username = repo_config["username"]
    password = repo_config["password"]
    
    # Use proper SPARQL endpoint URL
    url = f"{BASE_URL}/repositories/{repo_name}"
    
    print(f"  Attempting connection to: {url}")
    print(f"  Using credentials: {username} / {'*' * len(password)}")
    
    headers = {
        "Accept": "application/sparql-results+json"
    }
    
    # SPARQL queries should be sent as query parameter in GET or as form data in POST
    params = {"query": query}
    
    try:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            auth=HTTPBasicAuth(username, password)
        )
        response.raise_for_status()
        
        results = response.json()
        return results.get("results", {}).get("bindings", [])
    
    except requests.exceptions.RequestException as e:
        print(f"Error querying {repo_name}: {e}")
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            print(f"  Response: {e.response.text[:200]}")
        return []


def aggregate_statistics():
    """
    Query aggregate statistics from all repositories
    """
    query = """
    PREFIX hds: <http://example.org/hds#>
    
    SELECT (COUNT(DISTINCT ?victim) AS ?totalVictims)
           (AVG(?age) AS ?avgAge)
    WHERE {
      ?victim a hds:Victim .
      OPTIONAL { ?victim hds:age ?age }
    }
    """
    
    print("Aggregate Statistics Across All Datasets")
    print("=" * 60)
    
    all_results = []
    
    for repo_config in REPOSITORIES:
        repo_name = repo_config["name"]
        print(f"\nQuerying {repo_name}...")
        results = execute_sparql_query(repo_config, query)
        
        if results:
            binding = results[0]
            total_victims = binding.get("totalVictims", {}).get("value", "0")
            avg_age = binding.get("avgAge", {}).get("value", "N/A")
            
            # Map repository names back to readable format
            display_name = {
                "danieltesfa": "Daniel Tesfa",
                "kaismits": "Kai Smits", 
                "morganewirtz": "Morgane Wirtz"
            }.get(repo_name, repo_name)
            
            all_results.append({
                "Dataset": display_name,
                "Total Victims": total_victims,
                "Average Age": avg_age
            })
            
            print(f"  Total Victims: {total_victims}")
            print(f"  Average Age: {avg_age}")
    
    # Create DataFrame for easy viewing
    if all_results:
        df = pd.DataFrame(all_results)
        print("\n" + "=" * 60)
        print("Combined Results:")
        print(df.to_string(index=False))
        
        # Save to CSV
        df.to_csv("aggregate_stats_combined.csv", index=False)
        print("\nResults saved to: aggregate_stats_combined.csv")
    
    return all_results


def border_crossing_analysis():
    """
    Analyze nationality distribution across all repositories
    """
    query = """
    PREFIX hds: <http://example.org/hds#>
    
    SELECT ?nationality (COUNT(?victim) AS ?totalVictims)
    WHERE {
      ?victim a hds:Victim ;
              hds:nationality ?nationality .
    }
    GROUP BY ?nationality
    ORDER BY DESC(?totalVictims)
    """
    
    print("\n\nNationality Distribution Across All Datasets")
    print("=" * 60)
    
    all_nationalities = {}
    
    for repo_config in REPOSITORIES:
        repo_name = repo_config["name"]
        print(f"\nQuerying {repo_name}...")
        results = execute_sparql_query(repo_config, query)
        
        for binding in results:
            nationality = binding.get("nationality", {}).get("value", "Unknown")
            count = int(binding.get("totalVictims", {}).get("value", "0"))
            
            if nationality not in all_nationalities:
                all_nationalities[nationality] = {"total": 0, "datasets": []}
            
            all_nationalities[nationality]["total"] += count
            all_nationalities[nationality]["datasets"].append(f"{repo_name} ({count})")
    
    # Sort by total and display
    sorted_nationalities = sorted(all_nationalities.items(), key=lambda x: x[1]["total"], reverse=True)
    
    nationality_results = []
    for nationality, data in sorted_nationalities[:20]:  # Top 20
        nationality_results.append({
            "Nationality": nationality,
            "Total Victims": data["total"],
            "Datasets": ", ".join(data["datasets"])
        })
    
    if nationality_results:
        df = pd.DataFrame(nationality_results)
        print("\n" + "=" * 60)
        print("Combined Results (Top 20):")
        print(df.to_string(index=False))
        
        # Save to CSV
        df.to_csv("nationality_analysis_combined.csv", index=False)
        print("\nResults saved to: nationality_analysis_combined.csv")
    
    return nationality_results


def demographics_analysis():
    """
    Analyze victim demographics across all repositories
    """
    query = """
    PREFIX hds: <http://example.org/hds#>
    
    SELECT ?gender (COUNT(?victim) AS ?count)
    WHERE {
      ?victim a hds:Victim .
      OPTIONAL { ?victim hds:gender ?gender }
    }
    GROUP BY ?gender
    ORDER BY DESC(?count)
    """
    
    print("\n\nGender Distribution Across All Datasets")
    print("=" * 60)
    
    all_demographics = {}
    
    for repo_config in REPOSITORIES:
        repo_name = repo_config["name"]
        print(f"\nQuerying {repo_name}...")
        results = execute_sparql_query(repo_config, query)
        
        for binding in results:
            gender = binding.get("gender", {}).get("value", "Unknown")
            count = int(binding.get("count", {}).get("value", "0"))
            
            if gender not in all_demographics:
                all_demographics[gender] = {"total": 0, "datasets": []}
            
            all_demographics[gender]["total"] += count
            all_demographics[gender]["datasets"].append(f"{repo_name} ({count})")
    
    # Sort by total and display
    sorted_demographics = sorted(all_demographics.items(), key=lambda x: x[1]["total"], reverse=True)
    
    demo_results = []
    for gender, data in sorted_demographics:
        demo_results.append({
            "Gender": gender,
            "Total Count": data["total"],
            "Datasets": ", ".join(data["datasets"])
        })
    
    if demo_results:
        df = pd.DataFrame(demo_results)
        print("\n" + "=" * 60)
        print("Combined Results:")
        print(df.to_string(index=False))
        
        # Save to CSV
        df.to_csv("demographics_combined.csv", index=False)
        print("\nResults saved to: demographics_combined.csv")
    
    return demo_results


def main():
    """
    Main function to run all federated queries
    """
    print("AllegroGraph Federated Query Tool")
    print("Querying repositories:", ", ".join([r["name"] for r in REPOSITORIES]))
    print()
    
    # Run all analyses
    aggregate_statistics()
    border_crossing_analysis() 
    demographics_analysis()  
    
    print("\n" + "=" * 60)
    print("All queries completed!")
    print("Check the generated CSV files for detailed results.")


if __name__ == "__main__":
    main()
