# Thinx: Human Trafficking Research Platform

**Project:** Thinx  
**Course:** Data Science in Practice (Leiden University)

## Documentation Guide

**Quick Navigation:**

| User Type | Documentation |
|-----------|---------------|
| New User | [QUICK_START.md](QUICK_START.md) - Installation and setup |
| Researcher | [USER_GUIDE.md](USER_GUIDE.md) - Complete user guide |
| Administrator | [ADMIN_GUIDE.md](ADMIN_GUIDE.md) - Deployment and management |
| Support | [FAQ.md](FAQ.md) - Common questions |

**Additional Documentation:**
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - System design and components
- [docs/AI_MAPPER.md](docs/AI_MAPPER.md) - AI Smart Mapper setup and usage
- [docs/](docs/) - Complete technical documentation
- `check-setup.ps1` / `check-setup.sh` - System prerequisites validation

---

## Table of Contents

- [Introduction](#introduction)
- [Quick Start](#quick-start)
- [User Guide](#user-guide)
- [AI Smart Mapper](#ai-smart-mapper)
- [Developer Guide](#developer-guide)
- [Troubleshooting](#troubleshooting)
- [Project Background](#project-background)
- [License](#license)

---

## Introduction

Thinx is a research platform designed to help social scientists and humanitarian researchers analyze human trafficking data without programming skills. Built at Leiden University, this tool enables exploration of interview data, visualization of patterns, and generation of insights about refugee trafficking routes and victim experiences.

### Core Capabilities

- **Database Connectivity** - Connect to research databases using simple configuration forms
- **Data Visualization** - View statistics, charts, and tables without writing code
- **AI-Assisted Processing** - Automatic mapping of interview columns to standard formats
- **Pattern Analysis** - Explore trafficking routes, victim demographics, and crime patterns
- **Privacy-First Design** - All data processing occurs on local infrastructure

### Target Users

- Researchers studying human trafficking and migration
- Data analysts working with interview and survey data
- Policy makers requiring evidence-based insights
- Students learning about data science in humanitarian contexts

### Key Features

| Feature | Description | Benefit |
|---------|-------------|---------|
| Simple Setup | Single-command installation | Minimal technical expertise required |
| Multiple Datasets | Connect to different research databases | Compare data from multiple sources |
| FAIR Data Discovery | Browse EEPA data catalogs | Find relevant datasets before requesting access |
| Interactive Dashboards | Point-and-click data exploration | Immediate pattern visibility |
| AI Smart Mapper | Automatic column organization | Reduces manual data preparation |
| Privacy Protected | Local data processing | GDPR compliant and secure |

For detailed usage instructions, see [USER_GUIDE.md](USER_GUIDE.md).

For FAIR Data Point integration, see [docs/FAIR_DATA_POINT.md](docs/FAIR_DATA_POINT.md).

---

## Quick Start

### Prerequisites Verification

Run the automated checker to verify your system:

**Windows:**
```powershell
.\check-setup.ps1
```

**Mac/Linux:**
```bash
chmod +x check-setup.sh
./check-setup.sh
```

This script verifies:
- Docker installation and status
- Available disk space
- Port availability
- Project files integrity

### System Requirements

| Requirement | Purpose | Source |
|------------|---------|--------|
| Docker Desktop | Application runtime | [docker.com/get-started](https://docker.com/get-started) |
| Web Browser | Interface access | Chrome, Firefox, Edge, or Safari |
| 2GB Disk Space | Application storage | Available on system drive |
| Dataset Credentials | Research data access | Contact data provider |

Note: Run `check-setup.ps1` (Windows) or `check-setup.sh` (Mac/Linux) to verify system automatically.

### Installation Steps

**Step 1: Verify Docker Status**
- Check for Docker whale icon in taskbar/menu bar
- If not visible, open Docker Desktop application

**Step 2: Download Project**
- Using Git: `git clone [repository-url]`
- Or download and extract ZIP file

**Step 3: Open Terminal**
- **Windows**: Search for "PowerShell" or "Command Prompt"
- **Mac**: Search for "Terminal"
- Navigate to project: `cd path/to/DataScienceInPractice`

**Step 4: Start Application**

Choose deployment option:

**Option A: Full System (Recommended)**
Includes database, AI features, and interface.
```bash
docker-compose --profile full up --build
```

**Option B: Without AI Features**
Faster startup, excludes automatic data mapping.
```bash
docker-compose --profile no-ai up --build
```

**Step 5: Wait for Startup**
Monitor terminal output for completion messages:
- `frontend_1 | ready in XXX ms`
- `backend_1 | Running on http://0.0.0.0:5000`

Initial startup: 2-5 minutes
Subsequent startups: 30-60 seconds

**Step 6: Access Application**
Open browser to: **http://localhost**

---

## Application Access

After startup, the following services are available:

| Service | URL | Purpose |
|---------|-----|---------|
| Main Interface | http://localhost | Primary user interface |
| API Server | http://localhost:5000 | Backend (typically not accessed directly) |
| Database Admin | http://localhost:10035 | Advanced users - raw data access |

---

## User Guide

This section explains platform usage without requiring programming knowledge.

### Understanding Connections

A connection is a saved configuration for database access. Similar to a browser bookmark, Thinx stores database connections for easy switching between datasets.

**Purpose:** Research data resides in secure databases (AllegroGraph). Connections store:
- Database server address
- Repository name
- Authentication credentials

Connection details are typically provided by research coordinators or data providers.

### Adding a Dataset Connection

#### Step 1: Access Connection Form

Locate and click "Add New Connection" button.

#### Step 2: Complete Connection Form

| Field | Description | Input | Example |
|-------|-------------|-------|---------|
| Connection Name | User-defined identifier | Any memorable name | "Libya Study 2024" or "Main Dataset" |
| Server URL/IP | Database location | From data provider | `allegrograph` (Docker)<br>`192.168.1.100` (remote) |
| Port | Network port | Usually 10035 | `10035` |
| Repository Name | Specific database | From data provider | `humantrafficking` or `research_data` |
| Username | Authentication | From data provider | `researcher1` |
| Password | Authentication | From data provider | (encrypted storage) |

Note: Passwords are encrypted and never displayed after entry.

#### Step 3: Save Configuration

1. Click "Save Connection"
2. Wait for connection verification
3. Success indicator: "Connection created successfully"
4. New connection appears in list

#### Connection Issues

If connection fails, verify:

| Problem | Check | Solution |
|---------|-------|----------|
| Connection refused | Database status | Contact data provider or restart Docker |
| Invalid credentials | Username/password | Verify credentials (avoid typos) |
| Unknown host | Server address | Confirm server URL with data provider |
| Timeout | Network connectivity | Check internet connection or firewall |

For detailed troubleshooting, see [Troubleshooting](#troubleshooting) section.

### Viewing and Exploring Data

#### Step 1: Select Connection

Locate desired dataset in Connections List.

#### Step 2: Activate and View

Click "View Data" button next to chosen connection.

Result:
1. Database connection established
2. Connection marked as "Active"
3. Data Viewer screen displays

#### Step 3: Interface Overview

The Data Viewer contains three sections:

**Statistics Dashboard (Top)**

Displays four key metrics:

| Metric | Description | Use |
|--------|-------------|-----|
| Victims | Total victims in dataset | Understand research scale |
| Crimes | Criminal incidents recorded | View documented abuse events |
| Borders | Unique border crossings | Identify migration routes |
| Total Triples | Database size (technical) | Approximately total data points × 3 |

**Data Table (Middle)**

Spreadsheet view of victim records:
- **Victim ID** - Unique identifier (e.g., `victim_001`)
- **Age** - Age at interview (or "N/A" if not recorded)
- **Gender** - Gender identity (Male, Female, Non-binary, or Unknown)
- **Nationality** - Country of origin

**Navigation Controls (Bottom)**
- Refresh Data - Reload if database updated
- Results per page - Display 25, 50, 100, or 200 rows
- Previous/Next - Navigate between pages
- Page indicator - Current page display

### Managing Multiple Connections

To work with multiple datasets:

1. Return to Connection Manager (click "Back to Connections")
2. View all saved connections
3. Click "Activate" to switch datasets
4. Click "Edit" to modify connection details
5. Click "Delete" to remove connection

### FAIR-OLR Compliance

This system adheres to FAIR-OLR (Findable, Accessible, Interoperable, Reusable - Ownership, Locale, Regulatory) principles:

- **Findable:** Datasets discoverable through external FAIR Data Points (FDPs)
- **Accessible:** Data accessible via standard protocols (SPARQL, HTTP) with authentication
- **Interoperable:** Data uses `hds_cdm.ttl` Common Data Model for semantic consistency
- **Reusable:** Data structured with clear licensing and provenance metadata

---

## AI Smart Mapper

### Overview

The AI Smart Mapper is an experimental feature using local Large Language Models (LLMs) to automatically suggest mappings between data columns and Common Data Model (CDM) fields. This reduces manual work when structuring interview data.

**Key Features:**
- Local Processing - All data remains on local infrastructure (GDPR compliant)
- Intelligent Mapping - AI understands context and suggests matches
- Fast Setup - Download models directly from UI
- High Accuracy - Uses state-of-the-art open-source models

### Quick Start

#### 1. Start with Full Profile

AI mapper requires Ollama service:

```bash
docker-compose --profile full up --build
```

This starts all services including Ollama container.

#### 2. Navigate to Step 3

1. Upload data file in Step 2
2. Go to Step 3: Schema & Validation
3. Locate "AI Smart Mapper" section

#### 3. Download Model

In "Download New Model" section:

1. Enter model name (e.g., `llama3.2`)
2. Click "Download"
3. Wait 5-15 minutes for download (model size dependent)
4. Click "Refresh" to view in list

#### 4. Generate Mappings

1. Select downloaded model from dropdown
2. Click "Suggest Mappings"
3. Review AI suggestions in table
4. Click "Apply Mapping to File" to restructure data

### Model Selection

Browse complete model library at [ollama.com/library](https://ollama.com/library)

**Recommended Models:**

| Model Name | Size | Best For | Use Case |
|------------|------|----------|----------|
| `llama3.2` | 2GB | General use, good accuracy | Standard recommendation |
| `phi3` | 2.3GB | Fast processing | Limited resources |
| `mistral` | 4GB | High accuracy | Better results needed |
| `gemma2:2b` | 1.6GB | Lightweight | Quick testing |

Selection guidance:
- New users: Start with `llama3.2` (balanced speed and quality)
- Better accuracy: Try `mistral` or `llama3:8b`
- Fast processing: Use `phi3` or `gemma2:2b`

### Operation

```
Data File → AI Analyzer → Suggested Mappings → Apply → Structured Data
                 ↓
          (Ollama + LLM Model)
```

Process flow:
1. Upload Excel/JSON file with arbitrary column names
2. AI compares columns to CDM schema
3. Returns mapping (e.g., "name" → "victim_name")
4. Automatically renames columns in file
5. Continue to RDF generation with structured data

Note: All processing occurs locally in Docker containers. Sensitive data never leaves local infrastructure.

### Documentation

For comprehensive information including technical details, troubleshooting, and configuration, see [docs/AI_MAPPER.md](docs/AI_MAPPER.md).

---

## Developer Guide

This section is for developers and maintainers who need to install, modify, or extend the application.

### Prerequisites

- Docker (20.10+) and Docker Compose (2.0+)
- Git (optional, for cloning)
- Node.js (20.x LTS) - for local frontend development only
- Python (3.11+) - for local backend development only

### Development Mode

For active development with hot-reload:

**Backend (Flask):**
```bash
cd backend
pip install -r requirements.txt
python app.py
# Server runs on http://localhost:5000
```

**Frontend (Vue.js):**
```bash
cd frontend
npm install
npm run dev
# Server runs on http://localhost:80
```

### Stopping Application

```bash
# Stop containers (preserves data)
docker-compose stop

# Stop and remove containers (preserves data in volumes)
docker-compose down

# Stop and remove everything including data
docker-compose down -v
```

### Architecture

The application uses microservices architecture with three containers:

```
┌─────────────────────────────────────────────────────────┐
│                  Docker Compose Network                  │
│                                                           │
│  ┌──────────────┐    ┌──────────────┐    ┌───────────┐ │
│  │   Frontend   │◄──►│   Backend    │◄──►│AllegroGraph│
│  │   Vue.js     │    │   Flask API  │    │  Database  │
│  │   (Port 80)  │    │  (Port 5000) │    │(Port 10035)│
│  └──────────────┘    └──────────────┘    └───────────┘ │
└─────────────────────────────────────────────────────────┘
```

**Technology Stack:**

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Frontend | Vue.js 3 + Vite | User interface |
| Backend | Flask 3.0 | REST API |
| Database | AllegroGraph 8.0 | RDF triple store |
| Web Server | Nginx (Alpine) | Frontend serving |
| Containerization | Docker Compose | Orchestration |

For detailed architecture documentation, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

### Data Processing Pipeline

The project includes a complete data processing pipeline for converting raw interview data into RDF format:

#### 1. Data Extraction and Cleaning

**Purpose:** Clean and organize raw data into structured format.

- **Input:** Raw interview data in Excel format
- **Process:**
  - `processing.ipynb`: Cleans and standardizes data
  - `json_creator.ipynb`: Merges duplicate records and creates final JSON
- **Outputs:**
  - `victims.json`: Structured dataset with one entry per interview
  - `cleaned_data.json`: Final clean dataset with one record per victim

#### 2. Data Storage (RDF Conversion)

**Purpose:** Convert structured data into RDF format and store in AllegroGraph.

**Key Steps:**
1. Loading CDM (`hds_cdm.ttl`): Load Common Data Model ontology
2. RDF Triple Generation: Transform victim attributes into RDF triples
3. Saving RDF Data: Save as `Human_trafficking_output.ttl`
4. Uploading to AllegroGraph: Push data to database

**Script:** `push_to_allegrograph.py`

```python
# Basic usage
python push_to_allegrograph.py
```

#### 3. Data Analytics

**Purpose:** Analyze and visualize structured data using SPARQL queries.

The `sparql queries/` folder contains sample queries:

**Production Queries (full datasets):**
- `count_abuse_witnessed.rq` - Total victims who witnessed abuses
- `top10_highest_victim_borders.rq` - Top 10 borders by victim count
- `victim_count_by_border_and_trafficker.rq` - Trafficker-border relationships
- `total_extortion_amount_per_border.rq` - Total extortion by border
- `max_extortion_amount_per_border.rq` - Maximum extortion per border

**Mock Data Queries (testing):**
- `mock_data_test.rq` - Basic victim information retrieval
- `mock_extortion_analysis.rq` - Extortion statistics by nationality
- `mock_crime_stats.rq` - Crime type frequency analysis

Note: Use mock data queries when testing with files from `Mock data/` folder.

### Modifying the Common Data Model

The Common Data Model (CDM) is defined in `hds_cdm.ttl` and reflected in `backend/models.py`. To modify:

#### Adding a New Field to Existing Entity

**Example:** Add `birthdate` field to Victim entity

**Step 1: Update CDM Schema**

File: `backend/models.py`

```python
CDM_SCHEMA = {
    'Victim': {
        'description': 'Personal information about trafficking victims',
        'fields': [
            # ... existing fields ...
            {'name': 'birthdate', 'type': 'string', 'required': False, 
             'sensitive': True, 'gdpr_category': 'personal'},
        ]
    },
    # ... rest of schema ...
}
```

**Step 2: Update Backend Query**

File: `backend/app.py` - Find `get_data()` function:

```python
query = f"""
PREFIX ht: <http://example.org/humantrafficking/>

SELECT DISTINCT ?victim ?age ?gender ?nationality ?birthdate
WHERE {{
    ?victim a ht:Victim .
    OPTIONAL {{ ?victim ht:age ?age }}
    OPTIONAL {{ ?victim ht:gender ?gender }}
    OPTIONAL {{ ?victim ht:nationality ?nationality }}
    OPTIONAL {{ ?victim ht:birthdate ?birthdate }}
}}
LIMIT {limit}
OFFSET {offset}
"""
```

**Step 3: Update Frontend DataViewer**

File: `frontend/src/components/DataViewer.vue`

```vue
<template>
  <table class="data-table">
    <thead>
      <tr>
        <th>Victim ID</th>
        <th>Age</th>
        <th>Gender</th>
        <th>Nationality</th>
        <th>Birth Date</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="(row, index) in data" :key="index">
        <td>{{ truncateUri(row.victim) }}</td>
        <td>{{ row.age || 'N/A' }}</td>
        <td>{{ row.gender || 'N/A' }}</td>
        <td>{{ row.nationality || 'N/A' }}</td>
        <td>{{ row.birthdate || 'N/A' }}</td>
      </tr>
    </tbody>
  </table>
</template>
```

**Step 4: Rebuild and Test**

```bash
# Rebuild containers
docker-compose up --build

# Test application at http://localhost
```

#### GDPR Categories

Use these categories for sensitive data:

- `'personal'` - Name, age, contact info
- `'special_category'` - Race, ethnicity, sexual orientation
- `'criminal_offense'` - Crime details
- `None` - Non-sensitive data

### API Documentation

**Base URL:**
```
http://localhost:5000/api
```

#### Connection Management

**GET /api/connections**
- Get all saved connections
- Response: `{ success: true, connections: [...], count: 2 }`

**POST /api/connections**
- Create new connection
- Body: `{ name, host, port, repository, username, password }`
- Response: `{ success: true, message: "...", connection: {...} }`

**GET /api/connections/:id**
- Get specific connection
- Response: `{ success: true, connection: {...} }`

**PUT /api/connections/:id**
- Update connection
- Response: `{ success: true, connection: {...} }`

**DELETE /api/connections/:id**
- Delete connection
- Response: `{ success: true, message: "..." }`

**POST /api/connections/:id/activate**
- Set active connection
- Response: `{ success: true, message: "..." }`

**GET /api/connections/active**
- Get active connection
- Response: `{ success: true, connection: {...} }`

#### Data Operations

**GET /api/data**
- Query victim data
- Params: `connection_id` (optional), `limit`, `offset`
- Response: `{ success: true, data: [...], count: 50 }`

**POST /api/query**
- Execute custom SPARQL query
- Body: `{ query: "SELECT ...", connection_id: "..." }`
- Response: `{ success: true, results: [...] }`

**GET /api/statistics**
- Get dataset statistics
- Params: `connection_id` (optional)
- Response: `{ success: true, statistics: {...} }`

#### Metadata

**GET /api/ontology**
- Get CDM structure
- Response: `{ success: true, ontology: {...} }`

**GET /api/health**
- Health check
- Response: `{ status: "healthy", service: "flask_api", timestamp: "..." }`

---

## Troubleshooting

### Connection refused when accessing http://localhost

**Solution:**
1. Check if containers are running: `docker-compose ps`
2. Restart services: `docker-compose restart`
3. Check logs: `docker-compose logs frontend`

### Failed to connect to AllegroGraph

**Solution:**
1. Verify AllegroGraph is running: `docker-compose logs allegrograph`
2. Check credentials are correct
3. Try accessing directly: http://localhost:10035

### Frontend shows "API Error: No response from server"

**Solution:**
1. Check backend is running: `docker-compose ps backend`
2. Check backend logs: `docker-compose logs backend`
3. Verify CORS is enabled in `backend/app.py`

### No data found in repository

**Solution:**
1. Verify data uploaded to AllegroGraph using `push_to_allegrograph.py`
2. Check repository name matches
3. Test with simple SPARQL query in AllegroGraph console

### Changes not appearing after editing code

**Solution:**
```bash
# Rebuild containers
docker-compose up --build

# Or rebuild specific service
docker-compose up --build backend
```

### Port already in use

**Solution:**
```bash
# Find process using port 80 (Windows)
netstat -ano | findstr :80

# Find process using port 80 (Mac/Linux)
lsof -i :80

# Stop other services or change ports in docker-compose.yml
```

---

## Project Background

Thinx is a course project for Data Science in Practice at Leiden University's Master's programme. The project demonstrates practical application of:
- Data engineering and ETL pipelines
- Semantic web technologies (RDF, SPARQL, ontologies)
- Modern web architecture (microservices, containerization)
- Ethical data management
- Full-stack development (Flask backend + Vue.js frontend)

The platform focuses on analyzing, cleaning, and visualizing data about human trafficking, particularly in North Africa.

### Research Context

Human trafficking is a humanitarian crisis affecting refugees fleeing difficult situations. Many refugees are promised safe passage but are instead taken hostage, exploited, or abused. This application helps researchers:

- Document trafficking patterns through structured data
- Analyze migration routes and identify high-risk areas
- Support humanitarian efforts with actionable insights
- Inform policy-making with evidence-based research

### Dataset

The dataset is based on interviews with refugees and contains:
- Transit routes through Libya and North Africa
- Trafficker information and criminal networks
- Abuse reports (sexual violence, extortion, deaths)
- Border crossing details and geographic data

### Mock Data for Testing

The `Mock data/` folder contains sample datasets for testing and learning:

**Interview_mock_comprehensive.csv (Recommended)**
- Complete CDM-aligned dataset with 10 realistic cases
- Covers all entities: Victim, Incident, Trafficker, Location
- Suitable for testing AI Smart Mapper with proper Entity.field mappings
- Includes varied scenarios: trafficking, smuggling, kidnapping

**Legacy Excel files** (Interview_mock_1.xlsx, Interview_mock_2.xlsx, Interview_mock_3.xlsx)
- Original test files (may need column updates)

**Use mock data for:**
- Testing AI mapping and data transformation features
- Learning Thinx workflow with realistic data
- Development without exposing sensitive information
- Platform capability demonstrations

See `Mock data/README.md` for detailed usage instructions and CDM mapping examples.

### Ethical Considerations

All data is:
- Anonymized - No personally identifiable information
- Consent-based - Collected with participant permission
- GDPR compliant - Sensitive fields marked and protected
- Research-only - For academic and humanitarian purposes
- Mock data available - Safe testing data in `Mock data/` folder

---

## Experimental AI Features

This project includes experimental AI integration using [Ollama](https://ollama.com/) to provide "Smart Mapping" capabilities. This allows automatic suggestion of mappings between uploaded file columns and the Common Data Model (CDM).

### Enabling AI Features

1. Start application with AI profile:
   ```bash
   docker-compose --profile ai up --build
   ```

2. Pull LLM model (first time only):
   ```bash
   docker exec -it ollama_service ollama pull llama3
   ```
   Note: Requires approximately 4GB disk space and time depending on internet connection.

3. "Smart Map" feature available in API.

---

## Querying Multiple Repositories (Federated Queries)

AllegroGraph doesn't support SPARQL SERVICE clauses for cross-repository queries on the same server. To query multiple repositories (e.g., danieltesfa, Kai Smits, Morgana), use the Python script approach:

**Usage:**
```bash
pip install -r federated_requirements.txt
python federated_query.py
```

This script uses AllegroGraph's REST API to query all repositories and combines results into CSV files for aggregate statistics, border analysis, and demographics.

---

## License

MIT License - See LICENSE file for details

---

## Additional Documentation

For complete documentation index, see [docs/README.md](docs/README.md).

Core documentation:
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - Detailed architecture documentation
- [docs/DOCKER_USAGE.md](docs/DOCKER_USAGE.md) - Docker deployment guide
- [docs/AI_MAPPER.md](docs/AI_MAPPER.md) - AI Smart Mapper guide
- [docs/FAIR_DATA_POINT.md](docs/FAIR_DATA_POINT.md) - FAIR Data Point integration

---

## Support and Contact

- **GitHub Repository:** https://github.com/Justin2280/DataScienceInPractice
- **Documentation:** See additional markdown files in repository
- **Issues:** Report bugs or request features via GitHub Issues

---

## Acknowledgments

- Leiden University - Data Science in Practice course
- FIELD Lab - Human trafficking research initiative
- AllegroGraph - RDF database platform

---

**Last Updated:** December 2025  
**Version:** 2.0.0  
**Architecture:** Flask API + Vue.js SPA
