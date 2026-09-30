# THINX — FAIR Human Trafficking Data Analytics Platform

A data analytics and semantic knowledge-graph platform designed to support the integration, exploration, and analysis of human-trafficking data using **FAIR data principles, RDF, SPARQL, and containerized services**.

## Overview

THINX provides a structured environment for transforming and exploring human-trafficking data through semantic technologies and linked-data principles.

The platform combines:

* **RDF-based semantic data modeling**
* **Knowledge graph technologies**
* **SPARQL querying**
* **FAIR data principles**
* **Data processing and transformation**
* **Docker-based deployment**
* **Web-based data exploration and analytics**

## Architecture

The platform consists of several interconnected components:

```text
                    ┌─────────────────────┐
                    │     Web Frontend     │
                    │      Vue.js          │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     Flask API       │
                    │      Backend        │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │    AllegroGraph     │
                    │   Knowledge Graph   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ RDF / SPARQL Data   │
                    │ Semantic Models     │
                    └─────────────────────┘
```

## Technologies

| Area            | Technologies             |
| --------------- | ------------------------ |
| Frontend        | Vue.js                   |
| Backend         | Python, Flask            |
| Knowledge Graph | AllegroGraph             |
| Semantic Data   | RDF, Turtle              |
| Query Language  | SPARQL                   |
| Data Processing | Python, Jupyter          |
| Deployment      | Docker, Docker Compose   |
| Data Modeling   | Semantic Knowledge Graph |
| API             | REST-style HTTP API      |

## Key Features

### 1. Semantic Data Modeling

The project represents structured human-trafficking information using RDF and semantic relationships.

Example:

```text
Entity → Relationship → Entity
Victim → associatedWith → Case
Case → occurredIn → Location
```

This enables relationships between different entities to be represented and queried semantically.

### 2. SPARQL Querying

The platform supports querying the knowledge graph using SPARQL.

Example:

```sparql
SELECT ?victim ?location
WHERE {
    ?victim <associatedWith> ?case .
    ?case <occurredIn> ?location .
}
```

### 3. Data Processing

Python-based processing workflows are included for transforming and preparing data for semantic representation.

Relevant project components include:

* `processing.ipynb`
* `federated_query.py`
* `federated_requirements.txt`

### 4. Web Application

The project includes a web-based interface for interacting with the backend and knowledge graph.

```text
Vue.js
   ↓
Flask API
   ↓
AllegroGraph
   ↓
RDF Knowledge Graph
```

### 5. Dockerized Environment

The project can be deployed using Docker Compose to simplify setup and ensure consistent environments.

```bash
docker compose up --build
```

## Project Structure

```text
THINX/
│
├── backend/                 # Flask backend/API
├── frontend/                # Vue.js frontend
├── docs/                    # Project documentation
├── Mock data/               # Anonymized/sample data
├── sparql queries/          # SPARQL queries
│
├── docker-compose.yml       # Container orchestration
├── hds_cdm.ttl              # Semantic data model
├── federated_query.py       # Federated query workflow
├── processing.ipynb         # Data processing notebook
│
├── README.md
├── QUICK_START.md
├── ADMIN_GUIDE.md
├── USER_GUIDE.md
└── FAQ.md
```

## Running the Project

### Prerequisites

Install:

* Docker
* Docker Compose
* Python 3.x
* Node.js / npm

### Start with Docker

```bash
docker compose up --build
```

After the containers start, access the relevant services using the ports configured in `docker-compose.yml`.

## Data and Privacy

This repository does **not** include private production data or local AllegroGraph database storage.

Sensitive/generated data and database runtime files are excluded through `.gitignore`.

The repository is intended to demonstrate the project's architecture, data modeling, processing workflows, and software implementation.

## FAIR Data Principles

The project explores the use of FAIR principles:

* **Findable**
* **Accessible**
* **Interoperable**
* **Reusable**

Semantic technologies such as RDF and SPARQL support interoperability and structured data discovery.

## My Contribution

My work on the project included contributions to:

* Data modeling and semantic representation
* RDF/Turtle data preparation
* Knowledge graph integration
* SPARQL query development
* Python-based data processing
* Backend/API development
* Docker-based deployment and testing
* Integration between the frontend, backend, and knowledge graph
* Documentation and project setup

## Project Purpose

THINX demonstrates how semantic technologies and FAIR data practices can be applied to human-trafficking data to support structured data integration, querying, and analysis.

## Disclaimer

The repository contains development/demo materials and anonymized or mock data where applicable. It should not be interpreted as a repository of real-world personally identifiable human-trafficking records.

## License

Add the appropriate project license here if the project owner has specified one.
