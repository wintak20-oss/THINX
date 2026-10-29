import json
import os
import urllib.parse
import traceback

import requests
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, XSD


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
ONTOLOGY_FILE = "hds_cdm.ttl"
DATA_FILE = "cleaned_data.json"
OUTPUT_FILE = "Human_trafficking_output.ttl"

HDS = Namespace("http://example.org/hds#")
RESOURCE_BASE = "http://example.org/resource/"


def sanitize_uri(value):
    """Return a URL-safe identifier component."""
    if value is None or str(value).strip() == "":
        return "Unknown"
    return urllib.parse.quote(str(value).strip().replace(" ", "_"), safe="_-.")


def safe_add(graph, subject, predicate, obj):
    if subject is not None and predicate is not None and obj is not None:
        graph.add((subject, predicate, obj))


def as_literal(value, datatype=XSD.string):
    """Convert non-empty values to RDF literals; skip missing/invalid values."""
    if value is None or (isinstance(value, str) and not value.strip()):
        return None

    if isinstance(value, list):
        if not value:
            return None
        value = ", ".join(str(item) for item in value)

    if datatype == XSD.integer:
        try:
            # Avoid accepting values such as 3.5 or "unknown" as integers.
            int_value = int(value)
            return Literal(int_value, datatype=datatype)
        except (ValueError, TypeError, OverflowError):
            return None

    return Literal(value, datatype=datatype)


def load_graph():
    graph = Graph()
    graph.bind("hds", HDS)

    # Load the ontology when available. Stop rather than silently continuing
    # if an ontology file exists but cannot be parsed.
    if os.path.exists(ONTOLOGY_FILE):
        graph.parse(ONTOLOGY_FILE, format="turtle")
        print(f"Loaded ontology from {ONTOLOGY_FILE}")
    else:
        print(
            f"WARNING: {ONTOLOGY_FILE} was not found. "
            "Continuing without ontology triples."
        )

    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError(
            f"{DATA_FILE} was not found. No RDF output or upload was performed."
        )

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        victims_data = json.load(file)

    if not isinstance(victims_data, list):
        raise ValueError(f"{DATA_FILE} must contain a JSON list of records.")

    print(f"Loaded {len(victims_data)} records from {DATA_FILE}")

    for victim in victims_data:
        if not isinstance(victim, dict):
            continue

        victim_id = victim.get("victim_id")
        if victim_id is None or str(victim_id).strip() == "":
            print("WARNING: Skipping a record with no victim_id.")
            continue

        victim_uri = URIRef(
            f"{RESOURCE_BASE}Victim/{sanitize_uri(victim_id)}"
        )
        safe_add(graph, victim_uri, RDF.type, HDS.Victim)
        safe_add(graph, victim_uri, HDS.id, as_literal(victim_id))
        safe_add(graph, victim_uri, HDS.age, as_literal(victim.get("age"), XSD.integer))
        safe_add(graph, victim_uri, HDS.gender, as_literal(victim.get("gender")))
        safe_add(graph, victim_uri, HDS.nationality, as_literal(victim.get("nationality")))

        # Trafficker(s)
        trafficker_value = victim.get("trafficker_name")
        if isinstance(trafficker_value, str):
            trafficker_names = [trafficker_value]
        elif isinstance(trafficker_value, list):
            trafficker_names = trafficker_value
        else:
            trafficker_names = []

        for trafficker_name in trafficker_names:
            if not isinstance(trafficker_name, str):
                continue

            trafficker_name = trafficker_name.strip()
            if trafficker_name.lower() in {
                "", "no data", "unknown", "none", "null", "not specified"
            }:
                continue

            trafficker_uri = URIRef(
                f"{RESOURCE_BASE}Trafficker/{sanitize_uri(trafficker_name)}"
            )
            safe_add(graph, trafficker_uri, RDF.type, HDS.Trafficker)
            safe_add(graph, trafficker_uri, HDS.name, as_literal(trafficker_name))

            incident_uri = URIRef(
                f"{RESOURCE_BASE}Incident/Trafficking_"
                f"{sanitize_uri(victim_id)}_{sanitize_uri(trafficker_name)}"
            )
            safe_add(graph, incident_uri, RDF.type, HDS.Incident)
            safe_add(graph, incident_uri, HDS.type, as_literal("Trafficking"))
            safe_add(graph, incident_uri, HDS.affected, victim_uri)
            safe_add(graph, incident_uri, HDS.involved, trafficker_uri)

        # Crimes
        crimes = victim.get("crimes", [])
        if isinstance(crimes, list):
            for crime in crimes:
                if not isinstance(crime, dict):
                    continue

                if crime.get("sexual_violence_experienced_binary"):
                    sv_uri = URIRef(
                        f"{RESOURCE_BASE}Incident/SV_{sanitize_uri(victim_id)}"
                    )
                    safe_add(graph, sv_uri, RDF.type, HDS.Incident)
                    safe_add(graph, sv_uri, HDS.type, as_literal("Sexual Violence"))
                    safe_add(
                        graph,
                        sv_uri,
                        HDS.description,
                        as_literal(crime.get("sexual_violence_experienced_type")),
                    )
                    safe_add(graph, sv_uri, HDS.affected, victim_uri)

                if crime.get("abuse_type_experienced"):
                    abuse_uri = URIRef(
                        f"{RESOURCE_BASE}Incident/Abuse_{sanitize_uri(victim_id)}"
                    )
                    safe_add(graph, abuse_uri, RDF.type, HDS.Incident)
                    safe_add(graph, abuse_uri, HDS.type, as_literal("Abuse"))
                    safe_add(
                        graph,
                        abuse_uri,
                        HDS.description,
                        as_literal(crime.get("abuse_labels_experienced")),
                    )
                    safe_add(graph, abuse_uri, HDS.affected, victim_uri)

        # Border crossings and extortion
        crossings = victim.get("borders_crossed", [])
        if isinstance(crossings, list):
            for border_crossing in crossings:
                if not isinstance(border_crossing, dict):
                    continue

                border_name = border_crossing.get("border")
                money_amount = border_crossing.get("money_extorted_amount")

                if not border_name or str(border_name).strip().lower() in {
                    "no data", "unknown", "none", "null", "not specified"
                }:
                    continue

                location_uri = URIRef(
                    f"{RESOURCE_BASE}Location/{sanitize_uri(border_name)}"
                )
                safe_add(graph, location_uri, RDF.type, HDS.Location)
                safe_add(graph, location_uri, HDS.description, as_literal(border_name))

                event_uri = URIRef(
                    f"{RESOURCE_BASE}Event/Crossing_"
                    f"{sanitize_uri(victim_id)}_{sanitize_uri(border_name)}"
                )
                safe_add(graph, event_uri, RDF.type, HDS.Event)
                safe_add(graph, event_uri, HDS.type, as_literal("Border Crossing"))
                safe_add(graph, event_uri, HDS.location, location_uri)
                safe_add(graph, event_uri, HDS.involved, victim_uri)

                if money_amount is not None and str(money_amount).strip().lower() not in {
                    "", "no data", "unknown", "none", "null", "not specified"
                }:
                    extortion_uri = URIRef(
                        f"{RESOURCE_BASE}Incident/Extortion_"
                        f"{sanitize_uri(victim_id)}_{sanitize_uri(border_name)}"
                    )
                    safe_add(graph, extortion_uri, RDF.type, HDS.Incident)
                    safe_add(graph, extortion_uri, HDS.type, as_literal("Extortion"))
                    safe_add(graph, extortion_uri, HDS.location, location_uri)
                    safe_add(graph, extortion_uri, HDS.affected, victim_uri)
                    safe_add(
                        graph,
                        extortion_uri,
                        HDS.description,
                        as_literal(f"Extorted amount: {money_amount}"),
                    )

    return graph


def verify_repository(host, port, repo_name, username, password):
    """Read-only check against the verified root-catalog endpoint."""
    catalog_url = f"http://{host}:{port}/catalogs/root/repositories"
    response = requests.get(
        catalog_url,
        auth=(username, password),
        timeout=10,
    )

    if response.status_code != 200:
        raise RuntimeError(
            "Could not verify AllegroGraph repositories. "
            f"HTTP status: {response.status_code}. Upload stopped."
        )

    # The endpoint has returned a repository listing in the current setup.
    if repo_name not in response.text:
        raise RuntimeError(
            f"Target repository '{repo_name}' was not confirmed in the root "
            "catalog listing. Upload stopped; no repository was created."
        )

    print(f"Verified existing repository: {repo_name}")


def upload_rdf(rdf_file):
    """Upload the generated Turtle file only after verifying configuration/repo."""
    repo_name = os.getenv("AGRAPH_REPOSITORY")
    host = os.getenv("AGRAPH_HOST", "agraph")
    port = int(os.getenv("AGRAPH_PORT", "10035"))
    username = os.getenv("AGRAPH_SUPER_USER")
    password = os.getenv("AGRAPH_SUPER_PASSWORD")

    if not repo_name:
        raise RuntimeError("AGRAPH_REPOSITORY is not configured.")
    if not username or not password:
        raise RuntimeError(
            "Missing AllegroGraph credentials. Check AGRAPH_SUPER_USER and "
            "AGRAPH_SUPER_PASSWORD in the environment."
        )

    print(f"AllegroGraph host: {host}")
    print(f"AllegroGraph port: {port}")
    print(f"Target repository: {repo_name}")

    verify_repository(host, port, repo_name, username, password)

    with open(rdf_file, "rb") as file:
        rdf_content = file.read()

    if not rdf_content.strip():
        raise RuntimeError("The RDF output file is empty. Upload stopped.")

    size_url = f"http://{host}:{port}/repositories/{repo_name}/size"
    statements_url = f"http://{host}:{port}/repositories/{repo_name}/statements"

    # A size check is required before upload; do not assume zero on failure.
    size_response = requests.get(
        size_url, auth=(username, password), timeout=10
    )
    if size_response.status_code != 200:
        raise RuntimeError(
            "Could not verify the repository's initial triple count. "
            f"HTTP status: {size_response.status_code}. Upload stopped."
        )

    initial_count = int(size_response.text.strip())
    print(f"Current triple count in repository: {initial_count}")
    print(f"Read {len(rdf_content)} bytes from {rdf_file}")

    # This is the only write operation in the script.
    statements_response = requests.post(
        statements_url,
        auth=(username, password),
        headers={"Content-Type": "application/x-turtle"},
        data=rdf_content,
        timeout=60,
    )

    if statements_response.status_code not in (200, 201, 204):
        raise RuntimeError(
            "RDF upload failed with HTTP status "
            f"{statements_response.status_code}: {statements_response.text[:500]}"
        )

    print("RDF upload request completed.")

    final_response = requests.get(
        size_url, auth=(username, password), timeout=10
    )
    if final_response.status_code != 200:
        print("WARNING: Upload returned success, but final triple count could not be verified.")
        return

    final_count = int(final_response.text.strip())
    print(f"Final triple count in repository: {final_count}")
    print(f"Net triple-count change: {final_count - initial_count}")

    if final_count > initial_count:
        print("SUCCESS: The repository contains more triples than before.")
    else:
        print(
            "WARNING: No net increase in triple count was observed. "
            "The data may overlap existing triples or the repository may need inspection."
        )


def main():
    graph = load_graph()
    graph.serialize(destination=OUTPUT_FILE, format="turtle")
    print(f"Generated RDF file: {OUTPUT_FILE}")
    print(f"Generated graph triple count: {len(graph)}")

    # NOTE: Running this script writes RDF to the configured repository.
    # Review the generated TTL and confirm the target repository before running
    # it with production or sensitive data.
    upload_rdf(OUTPUT_FILE)


if __name__ == "__main__":
    try:
        main()
    except FileNotFoundError as error:
        print(f"ERROR: {error}")
    except requests.exceptions.RequestException as error:
        print(f"ERROR: AllegroGraph request failed: {error}")
    except Exception as error:
        print(f"ERROR: {error}")
        traceback.print_exc()
