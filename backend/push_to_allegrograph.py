import json
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, SKOS, XSD, RDFS
import urllib.parse
import requests
import os

# Load your ontology into the RDF graph
ontology_file = "hds_cdm.ttl"
g = Graph()
try:
    g.parse(ontology_file, format="turtle")
    print(f"Loaded ontology from {ontology_file}")
except Exception as e:
    print(f"Error loading ontology: {e}")

# Namespaces
HDS = Namespace("http://example.org/hds#")
g.bind("hds", HDS)

# Load new JSON data
data_file = "cleaned_data.json"
try:
    with open(data_file, "r") as f:
        victims_data = json.load(f)
    print(f"Loaded data from {data_file}")
except FileNotFoundError:
    print(f"Error: {data_file} not found.")
    victims_data = []

# Helper functions
def sanitize_uri(value):
    if not value:
        return "Unknown"
    return urllib.parse.quote(str(value).replace(" ", "_"))

def safe_add(graph, subject, predicate, obj):
    if subject and predicate and obj is not None:
        graph.add((subject, predicate, obj))

def as_literal(value, datatype=XSD.string):
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    if isinstance(value, list):
        if len(value) == 0:
            return None
        value = ", ".join([str(v) for v in value])
    
    # Special handling for integer datatype
    if datatype == XSD.integer:
        # Check if value is a valid integer or numeric string
        try:
            # Try to convert to int
            int_val = int(value)
            return Literal(int_val, datatype=datatype)
        except (ValueError, TypeError):
            # If conversion fails (e.g., "not specified", "Unknown"), return None
            # This will cause safe_add to skip adding the triple
            return None
    
    return Literal(value, datatype=datatype)

# Process victims data
print("Processing victim data...")
for victim in victims_data:
    victim_id = victim.get("victim_id", "Unknown")
    victim_uri = URIRef(f"http://example.org/resource/Victim/{sanitize_uri(victim_id)}")
    safe_add(g, victim_uri, RDF.type, HDS.Victim)
    safe_add(g, victim_uri, HDS.id, as_literal(victim_id))

    # Add victim attributes
    safe_add(g, victim_uri, HDS.age, as_literal(victim.get("age"), XSD.integer))
    safe_add(g, victim_uri, HDS.gender, as_literal(victim.get("gender")))
    safe_add(g, victim_uri, HDS.nationality, as_literal(victim.get("nationality")))
    
    # Trafficker(s)
    for trafficker_name in victim.get("trafficker_name", []):
        trafficker_uri = URIRef(f"http://example.org/resource/Trafficker/{sanitize_uri(trafficker_name)}")
        safe_add(g, trafficker_uri, RDF.type, HDS.Trafficker)
        safe_add(g, trafficker_uri, HDS.name, as_literal(trafficker_name))
        
        # Create an Incident "Trafficking" to link Victim and Trafficker
        incident_uri = URIRef(f"http://example.org/resource/Incident/Trafficking_{sanitize_uri(victim_id)}_{sanitize_uri(trafficker_name)}")
        safe_add(g, incident_uri, RDF.type, HDS.Incident)
        safe_add(g, incident_uri, HDS.type, as_literal("Trafficking"))
        safe_add(g, incident_uri, HDS.affected, victim_uri)
        safe_add(g, incident_uri, HDS.involved, trafficker_uri)

    # Crimes
    for crime in victim.get("crimes", []):
        # Sexual Violence
        if crime.get("sexual_violence_experienced_binary"):
            sv_uri = URIRef(f"http://example.org/resource/Incident/SV_{sanitize_uri(victim_id)}")
            safe_add(g, sv_uri, RDF.type, HDS.Incident)
            safe_add(g, sv_uri, HDS.type, as_literal("Sexual Violence"))
            safe_add(g, sv_uri, HDS.description, as_literal(crime.get("sexual_violence_experienced_type")))
            safe_add(g, sv_uri, HDS.affected, victim_uri)

        # Abuse
        if "abuse_type_experienced" in crime:
             abuse_uri = URIRef(f"http://example.org/resource/Incident/Abuse_{sanitize_uri(victim_id)}")
             safe_add(g, abuse_uri, RDF.type, HDS.Incident)
             safe_add(g, abuse_uri, HDS.type, as_literal("Abuse"))
             safe_add(g, abuse_uri, HDS.description, as_literal(crime.get("abuse_labels_experienced")))
             safe_add(g, abuse_uri, HDS.affected, victim_uri)

    # Borders and Extortion
    for border_crossing in victim.get("borders_crossed", []):
        if isinstance(border_crossing, dict):
            border_name = border_crossing.get("border", "no data")
            money_amount = border_crossing.get("money_extorted_amount", "no data")
        else:
            continue

        # Location
        location_uri = URIRef(f"http://example.org/resource/Location/{sanitize_uri(border_name)}")
        safe_add(g, location_uri, RDF.type, HDS.Location)
        safe_add(g, location_uri, HDS.description, as_literal(border_name))

        # Event (Crossing)
        event_uri = URIRef(f"http://example.org/resource/Event/Crossing_{sanitize_uri(victim_id)}_{sanitize_uri(border_name)}")
        safe_add(g, event_uri, RDF.type, HDS.Event)
        safe_add(g, event_uri, HDS.type, as_literal("Border Crossing"))
        safe_add(g, event_uri, HDS.location, location_uri)
        safe_add(g, event_uri, HDS.involved, victim_uri)

        # Extortion
        if money_amount != "no data":
            extortion_uri = URIRef(f"http://example.org/resource/Incident/Extortion_{sanitize_uri(victim_id)}_{sanitize_uri(border_name)}")
            safe_add(g, extortion_uri, RDF.type, HDS.Incident)
            safe_add(g, extortion_uri, HDS.type, as_literal("Extortion"))
            safe_add(g, extortion_uri, HDS.location, location_uri)
            safe_add(g, extortion_uri, HDS.affected, victim_uri)
            safe_add(g, extortion_uri, HDS.description, as_literal(f"Extorted amount: {money_amount}"))

# Save the RDF graph
output_file = "Human_trafficking_output.ttl"
g.serialize(destination=output_file, format="turtle")
print(f"RDF data has been successfully generated and saved to {output_file}")

# AllegroGraph Connection Details (from environment variables or defaults)
repo_name = os.getenv("AGRAPH_REPOSITORY", "KS01")
host = os.getenv("AGRAPH_HOST", "ag1jdz6nqkhfjj72.allegrograph.cloud")
port = int(os.getenv("AGRAPH_PORT", "10035"))
username = os.getenv("AGRAPH_USER", "Admin")
password = os.getenv("AGRAPH_PASSWORD", "KbA8KuX3E7aZSOVwGCxiK4")

# Convert ag1jdz6nqkhfjj72.allegrograph.cloud to allegrograph for Docker networking
if host == "ag1jdz6nqkhfjj72.allegrograph.cloud" or host == "127.0.0.1":
    host = "allegrograph"
    print(f"Converted ag1jdz6nqkhfjj72.allegrograph.cloud to allegrograph for Docker networking")

print(f"Connection details: host={host}, port={port}, repo={repo_name}, user={username}")

# Load RDF data from the generated file
rdf_file = "Human_trafficking_output.ttl"  # Path to the RDF file

# Upload RDF Data to AllegroGraph using REST API (Python 3.11+ compatible)
try:
    print(f"Connecting to AllegroGraph repository: {repo_name} at {host}:{port}")
    
    # Read the RDF file
    with open(rdf_file, "rb") as f:
        rdf_content = f.read()
    
    print(f"Read {len(rdf_content)} bytes from {rdf_file}")
    
    # Check if repository exists, create if not
    catalog_url = f"http://{host}:{port}/catalogs"
    repositories_url = f"{catalog_url}/repositories"
    repo_check_url = f"{repositories_url}/{repo_name}"
    
    check_response = requests.get(repo_check_url, auth=(username, password))
    
    if check_response.status_code == 404:
        print(f"Repository {repo_name} does not exist. Creating it...")
        
        # Create the repository
        create_url = f"{catalog_url}/root/repositories"
        create_data = {
            "id": repo_name,
            "title": "Human Trafficking Research Data",
            "description": "RDF knowledge graph for human trafficking research"
        }
        
        create_response = requests.put(
            f"{create_url}/{repo_name}",
            auth=(username, password),
            headers={"Content-Type": "application/json"},
            json=create_data
        )
        
        if create_response.status_code in [200, 201, 204]:
            print(f"SUCCESS: Repository {repo_name} created successfully!")
        else:
            print(f"ERROR: Failed to create repository. Status: {create_response.status_code}")
            print(f"Response: {create_response.text}")
            raise Exception(f"Failed to create repository: {create_response.text}")
    else:
        print(f"Repository {repo_name} exists.")
    
    # Get current triple count before upload
    size_url = f"http://{host}:{port}/repositories/{repo_name}/size"
    size_response = requests.get(size_url, auth=(username, password))
    
    if size_response.status_code == 200:
        initial_count = int(size_response.text.strip())
        print(f"Current triple count in repository: {initial_count}")
    else:
        print(f"Warning: Could not get initial size. Status: {size_response.status_code}")
        initial_count = 0
    
    # Upload the RDF data
    statements_url = f"http://{host}:{port}/repositories/{repo_name}/statements"
    headers = {
        "Content-Type": "application/x-turtle"  # Turtle format
    }
    
    print("Uploading RDF data to AllegroGraph...")
    upload_response = requests.post(
        statements_url,
        auth=(username, password),
        headers=headers,
        data=rdf_content
    )
    
    if upload_response.status_code in [200, 201, 204]:
        print("RDF data upload completed!")
        
        # Get final triple count after upload
        size_response = requests.get(size_url, auth=(username, password))
        if size_response.status_code == 200:
            final_count = int(size_response.text.strip())
            print(f"Final triple count in repository: {final_count}")
            print(f"Triples added: {final_count - initial_count}")
            
            if final_count > initial_count:
                print("SUCCESS: Data was actually uploaded to AllegroGraph!")
            else:
                print("WARNING: No new triples were added. Data might already exist or be duplicates.")
        else:
            print("SUCCESS: Upload completed but could not verify final count.")
    else:
        print(f"ERROR: Upload failed with status code: {upload_response.status_code}")
        print(f"Response: {upload_response.text}")
        raise Exception(f"Upload failed: {upload_response.text}")
            
except FileNotFoundError:
    print(f"ERROR: RDF file not found: {rdf_file}")
    print("Please make sure you have generated the RDF file first (Step 3).")
except requests.exceptions.ConnectionError:
    print("ERROR: Could not connect to AllegroGraph.")
    print("Please make sure AllegroGraph is running at http://ag1jdz6nqkhfjj72.allegrograph.cloud:10035")
    print("You can start it with: docker start allegrograph")
except Exception as e:
    print(f"An error occurred: {e}")
    import traceback
    traceback.print_exc()
