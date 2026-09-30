# Thinx - Technical Documentation

Welcome to the Thinx technical documentation. This folder contains detailed guides for developers and system administrators.

**New user?** Start with [../QUICK_START.md](../QUICK_START.md)  
**Looking for user docs?** See [../USER_GUIDE.md](../USER_GUIDE.md)  
**Deploying for a team?** See [../ADMIN_GUIDE.md](../ADMIN_GUIDE.md)

---

## Quick Navigation

| User Type | Documentation |
|-----------|---------------|
| New User | [../QUICK_START.md](../QUICK_START.md) |
| Researcher | [../USER_GUIDE.md](../USER_GUIDE.md) |
| Administrator | [../ADMIN_GUIDE.md](../ADMIN_GUIDE.md) |
| Developer | [ARCHITECTURE.md](ARCHITECTURE.md) |
| Support | [../FAQ.md](../FAQ.md) |

---

## Documentation Files

| Document | Purpose | For |
|----------|---------|-----|
| [ARCHITECTURE.md](ARCHITECTURE.md) | System design and component overview | Developers, Admins |
| [AI_MAPPER.md](AI_MAPPER.md) | AI Smart Mapper setup and usage | Data processors |
| [DOCKER_USAGE.md](DOCKER_USAGE.md) | Docker commands and profiles | Admins, Developers |
| [FAIR_DATA_POINT.md](FAIR_DATA_POINT.md) | FAIR Data Point integration | Researchers, Data owners |

---

## Common Tasks

| I want to... | Read this |
|-------------|-----------|
| Understand the system architecture | [ARCHITECTURE.md](ARCHITECTURE.md) |
| Set up AI Smart Mapper | [AI_MAPPER.md](AI_MAPPER.md) |
| Use Docker profiles | [DOCKER_USAGE.md](DOCKER_USAGE.md) |
| Deploy to production | [../ADMIN_GUIDE.md](../ADMIN_GUIDE.md) |
| Use AI to map columns | [AI_MAPPER.md](AI_MAPPER.md) |
| Download AI models | [AI_MAPPER.md](AI_MAPPER.md#step-2-download-an-ai-model) |
| Test with sample data | [../Mock data/README.md](../Mock%20data/README.md) |
| Modify the data model | [CDM Tutorial](../README.md#modifying-the-common-data-model) |
| Use the API | [API Documentation](../README.md#api-documentation) |
| Fix a problem | [Troubleshooting](../README.md#troubleshooting) or [../FAQ.md](../FAQ.md) |
| Understand architecture | [ARCHITECTURE.md](ARCHITECTURE.md) |
| Process raw data | [Data Processing Pipeline](../README.md#data-processing-pipeline) |
| Deploy with Docker | [DOCKER_USAGE.md](DOCKER_USAGE.md) |

---

## Project File Structure

```
DataScienceInPractice/
├── README.md                  - Main documentation
├── QUICK_START.md             - 5-minute setup guide
├── docker-compose.yml         - Container orchestration
├── start.bat / start.sh       - Easy startup scripts
│
├── docs/                      - Technical documentation
│   ├── README.md             - This file
│   ├── ARCHITECTURE.md       - System design
│   ├── DOCKER_USAGE.md       - Docker guide
│   ├── AI_MAPPER.md          - AI Smart Mapper guide
│   └── FAIR_DATA_POINT.md    - FAIR Data Point integration
│
├── backend/                   - Flask REST API
│   ├── app.py                - Main API application
│   ├── models.py             - Data models and CDM schema
│   └── requirements.txt      - Python dependencies
│
├── frontend/                  - Vue.js interface
│   └── src/
│       ├── components/       - Vue components
│       ├── router/           - Routing
│       └── services/         - API client
│
├── sparql queries/            - Sample SPARQL queries
└── [data files & notebooks]   - Data processing
```

---

## Need Help?

### Common Problems

| Problem | Solution |
|---------|----------|
| Can't access http://localhost | Check Docker is running → [Troubleshooting](../README.md#troubleshooting) |
| Connection fails | Verify credentials → [Troubleshooting](../README.md#troubleshooting) |
| Code changes not appearing | Rebuild containers: `docker-compose up --build` |
| Port already in use | Stop other services → [DOCKER_USAGE.md](DOCKER_USAGE.md) |

### Still Stuck?

1. Check [Troubleshooting](../README.md#troubleshooting) section in main README
2. Review [DOCKER_USAGE.md](DOCKER_USAGE.md) for Docker issues
3. Check container logs: `docker-compose logs -f`

---

## Documentation Quick Stats

- **Total Documentation Files:** 8
- **Estimated Total Reading Time:** 2-3 hours (full documentation)
- **Quick Start Time:** 5 minutes
- **Minimum Time to Get Started:** 20 minutes (Quick Start + End-User Manual)

---

## Learning Paths

### Path 1: "Just Want to Use It" (30 minutes)
1. [QUICK_START.md](../QUICK_START.md)
2. [User Guide](../USER_GUIDE.md)
3. Start using the application

### Path 2: "Want to Understand It" (90 minutes)
1. [README.md](../README.md) - Full read
2. [ARCHITECTURE.md](ARCHITECTURE.md)

### Path 3: "Need to Modify It" (2-3 hours)
1. [README.md](../README.md) - Developer section
2. [ARCHITECTURE.md](ARCHITECTURE.md)
3. [CDM Tutorial](../README.md#modifying-the-common-data-model)
4. [API Documentation](../README.md#api-documentation)

---

## Quick Reference Commands

### Starting and Stopping
```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# Stop services
docker-compose down

# Rebuild and start
docker-compose up --build
```

### Accessing Services
- Frontend: http://localhost
- Backend API: http://localhost:5000
- AllegroGraph: http://localhost:10035

### Useful Commands
```bash
# View logs
docker-compose logs -f

# Check running containers
docker-compose ps

# Restart one service
docker-compose restart backend
```

---

**Last Updated:** December 2025  
**Version:** 2.0.0  
**Status:** Current (Flask + Vue.js architecture)

---

Ready to start? Go to [QUICK_START.md](../QUICK_START.md)
