# Architecture: Containerized Flask + Vue.js Application

## Overview

This document describes the refactored architecture for the Data Science in Practice application, transitioning from a monolithic Flask application to a modern containerized microservices architecture.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Compose Network                    │
│                                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Frontend   │    │   Backend    │    │  AllegroGraph│  │
│  │   Vue.js     │◄──►│   Flask API  │◄──►│   Database   │  │
│  │   (Port 80)  │    │  (Port 5000) │    │  (Port 10035)│  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                    │                    │          │
│         │                    │                    │          │
│         ▼                    ▼                    ▼          │
│    [Nginx Serve]     [Flask+CORS]         [Data Store]      │
│                      [Connection Mgr]                        │
└─────────────────────────────────────────────────────────────┘
```

## Services

### 1. Frontend Service (Vue.js)

- **Technology:** Vue.js 3 with Vite
- **Port:** 80 (HTTP)
- **Purpose:** User interface for connection management and data visualization
- **Key Features:**
  - Connection Manager dashboard
  - Dataset selection interface
  - Data visualization components

### 2. Backend Service (Flask)

- **Technology:** Flask (Python 3.11+)
- **Port:** 5000
- **Purpose:** REST API for connection management and data operations
- **Key Features:**
  - RESTful API endpoints
  - CORS enabled for frontend communication
  - Connection persistence (JSON file storage)
  - AllegroGraph query proxy

### 3. Database Service (AllegroGraph)

- **Technology:** AllegroGraph 8.0+
- **Port:** 10035
- **Purpose:** RDF triple store for human trafficking data
- **Key Features:**
  - SPARQL query endpoint
  - RDF data storage
  - Repository management

## Directory Structure

```
DataScienceInPractice/
├── docker-compose.yml           # Service orchestration
├── .env.example                 # Environment variables template
├── README.md                    # Comprehensive documentation
├── ARCHITECTURE.md              # This file
│
├── backend/                     # Flask REST API
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app.py                   # Main Flask application
│   ├── models.py                # Data models (CDM)
│   ├── config.py                # Configuration management
│   ├── data/                    # Persistent storage
│   │   └── connections.json     # Saved connections
│   └── utils/
│       └── allegrograph.py      # AllegroGraph client
│
└── frontend/                    # Vue.js UI
    ├── Dockerfile
    ├── package.json
    ├── vite.config.js
    ├── index.html
    ├── public/
    │   └── favicon.ico
    └── src/
        ├── main.js              # App entry point
        ├── App.vue              # Root component
        ├── router/
        │   └── index.js         # Route definitions
        ├── components/
        │   ├── ConnectionManager.vue
        │   ├── ConnectionForm.vue
        │   ├── ConnectionList.vue
        │   └── DataViewer.vue
        └── services/
            └── api.js           # Backend API client
```

## Data Flow

### Connection Management Flow

1. User enters connection details in Vue.js UI
2. Frontend sends POST request to Flask API (`/api/connections`)
3. Flask validates and saves connection to `connections.json`
4. Response returned to frontend with connection ID
5. Frontend updates connection list

### Data Query Flow

1. User selects active connection in UI
2. Frontend sends GET request to Flask API (`/api/data?connection_id=X`)
3. Flask loads connection from `connections.json`
4. Flask connects to AllegroGraph using stored credentials
5. Flask executes SPARQL query and formats results
6. JSON response returned to frontend
7. Vue.js renders data in table/chart format

### FAIR Metadata Flow

1. User enters FAIR Data Point URL in connection form
2. Frontend requests metadata (`/api/fair-metadata?url=X`)
3. Flask fetches metadata from FAIR Data Point
4. Metadata displayed in UI (Owner, License, Keywords, etc.)

## API Endpoints

### Connection Management

- `POST /api/connections` - Create new connection
- `GET /api/connections` - List all connections
- `GET /api/connections/<id>` - Get specific connection
- `PUT /api/connections/<id>` - Update connection
- `DELETE /api/connections/<id>` - Delete connection
- `POST /api/connections/<id>/activate` - Set active connection

### Data Operations

- `GET /api/data` - Query data from active connection
- `POST /api/query` - Execute custom SPARQL query
- `GET /api/statistics` - Get dataset statistics

### Metadata

- `GET /api/fair-metadata` - Fetch FAIR Data Point metadata
- `GET /api/ontology` - Get ontology structure

## Persistence Strategy

### Backend Data

- **Location:** `backend/data/connections.json`
- **Docker Volume:** Maps to container's `/app/data` directory
- **Format:** JSON array of connection objects
- **Backup:** Survives container restarts

### Frontend State

- **Storage:** Browser localStorage for UI preferences
- **Session:** Active connection stored in sessionStorage
- **No persistence:** Temporary UI state lost on refresh

## Security Considerations

### No Application Authentication

- As requested, no login/registration system
- Connection credentials stored in plaintext JSON
- **Warning:** Suitable for trusted environments only

### AllegroGraph Credentials

- User provides external credentials
- Credentials stored locally in backend
- Used for proxy connections only

### CORS Configuration

- Flask allows requests from Vue.js origin
- Whitelist specific frontend URL in production

## Deployment

### Development

```bash
docker-compose up --build
```

Access at:
- Frontend: http://localhost
- Backend API: http://localhost:5000
- AllegroGraph: http://localhost:10035

### Production Considerations

1. Use environment variables for sensitive config
2. Enable HTTPS with reverse proxy (Nginx/Traefik)
3. Implement rate limiting on API
4. Add connection encryption for AllegroGraph
5. Consider secrets management (HashiCorp Vault, etc.)

## Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Frontend Framework | Vue.js | 3.x |
| Build Tool | Vite | 5.x |
| Backend Framework | Flask | 3.0+ |
| CORS Middleware | flask-cors | 4.0+ |
| Database | AllegroGraph | 8.0+ |
| Orchestration | Docker Compose | 2.x |
| Python | CPython | 3.11+ |
| Node.js | Node | 20.x LTS |

## Common Data Model (CDM)

The CDM defines the structure of human trafficking data:

### Core Entities

1. **Victim** - Personal information (age, gender, nationality)
2. **Crime** - Abuse details (sexual violence, deaths witnessed)
3. **Trafficker** - Perpetrator information
4. **Border** - Geographic crossing points
5. **Extortion** - Financial exploitation data

### Modification Process

See Developer Guide in README.md for detailed CDM modification tutorial.

## Monitoring and Logs

### Container Logs

```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f allegrograph
```

### Health Checks

- Backend: `GET /api/health`
- AllegroGraph: `GET http://localhost:10035/repositories`

## Future Enhancements

1. **Authentication Layer** (if needed later)
2. **Multi-user Support** with role-based access
3. **Connection Encryption** for stored credentials
4. **Real-time Query Results** via WebSockets
5. **Advanced Visualization** (D3.js graphs, maps)
6. **Export Functionality** (CSV, Excel, JSON)
7. **Audit Logging** for data access
8. **Backup/Restore** for connections

## Migration from Monolithic App

The original `app.py` provided:
- Combined frontend/backend in single Flask app
- Template rendering with Jinja2
- Direct AllegroGraph connection

The new architecture provides:
- Separated concerns (API vs UI)
- Scalability (services scale independently)
- Modern UI framework (Vue.js vs Jinja2)
- Containerization (easy deployment)
- Connection management (multi-dataset support)

## References

- Flask Documentation: https://flask.palletsprojects.com/
- Vue.js Documentation: https://vuejs.org/
- AllegroGraph Documentation: https://franz.com/agraph/support/documentation/
- FAIR Data Principles: https://www.go-fair.org/fair-principles/
