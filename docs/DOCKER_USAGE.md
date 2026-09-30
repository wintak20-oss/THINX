# Docker Compose Usage Guide

This document explains how to run different combinations of services.

## Profiles Available

The docker-compose configuration uses profiles to allow flexible service selection:

- **full** - All services (frontend + backend + allegrograph + AI)
- **no-ai** - Standard stack (frontend + backend + allegrograph)
- **minimal** - Minimal stack (frontend + backend only)
- **frontend** - Vue.js UI only
- **backend** - Flask API only
- **allegrograph** - AllegroGraph database only
- **ai** - Ollama AI service only

---

## Usage Examples

### 1. Full Stack (All Services)

Starts frontend, backend, AllegroGraph, and Ollama AI:

```bash
docker-compose --profile full up --build
```

### 2. Standard Stack (No AI)

Starts frontend, backend, and AllegroGraph (lighter weight):

```bash
docker-compose --profile no-ai up --build
```

### 3. Minimal Stack (No AI, No AllegroGraph)

Use this when you have AllegroGraph running elsewhere:

```bash
docker-compose --profile minimal up --build
```

**Access:**
- Frontend: http://localhost
- Backend: http://localhost:5000
- AllegroGraph: http://localhost:10035 (if running)

---

### 4. Custom Combinations

**Configuration:**
1. Create `.env` file from `.env.example`
2. Set `AGRAPH_HOST=your-server-ip` (e.g., `192.168.1.100` or `agraph.example.com`)
3. Set `AGRAPH_PORT=10035` (or your port)

**Access:**
- Frontend: http://localhost
- Backend: http://localhost:5000

---

### 5. Backend + AllegroGraph Only (No Frontend)

Useful for API-only access or custom frontend:

```bash
docker-compose --profile backend --profile allegrograph up --build
```

**Access:**
- Backend: http://localhost:5000
- AllegroGraph: http://localhost:10035

---

### 6. Individual Services

Start one service at a time:

```bash
# Frontend only
docker-compose up --build frontend

# Backend only
docker-compose up --build backend

# AllegroGraph only
docker-compose up --build allegrograph
```

---

## Environment Configuration

### Using External AllegroGraph

Create a `.env` file:

```env
# Point to external AllegroGraph
AGRAPH_HOST=192.168.1.100
AGRAPH_PORT=10035

# Other settings
FLASK_DEBUG=True
VITE_API_URL=http://localhost:5000
```

Then start without AllegroGraph:

```bash
docker-compose up --build frontend backend
```

### Using Docker AllegroGraph

Use default `.env.example` settings:

```env
AGRAPH_HOST=allegrograph
AGRAPH_PORT=10035
```

Then start full stack:

```bash
docker-compose --profile full up --build
```

---

## Common Scenarios

### Scenario 1: Development with Local AllegroGraph

You have AllegroGraph running on your host machine at `localhost:10035`.

**Setup:**
1. Create `.env`:
   ```env
   AGRAPH_HOST=host.docker.internal
   AGRAPH_PORT=10035
   ```
2. Start without Docker AllegroGraph:
   ```bash
   docker-compose up --build frontend backend
   ```

### Scenario 2: Production with Remote AllegroGraph

You have AllegroGraph on a remote server.

**Setup:**
1. Create `.env`:
   ```env
   AGRAPH_HOST=agraph.production.com
   AGRAPH_PORT=10035
   AGRAPH_SUPER_USER=your-username
   AGRAPH_SUPER_PASSWORD=your-password
   ```
2. Start without Docker AllegroGraph:
   ```bash
   docker-compose up -d frontend backend
   ```

### Scenario 3: Testing Backend API Only

You want to test API endpoints without frontend.

**Setup:**
```bash
# Start backend + AllegroGraph
docker-compose --profile backend --profile allegrograph up --build

# Or
docker-compose up --build backend allegrograph
```

**Test:**
```bash
curl http://localhost:5000/api/health
```

### Scenario 4: Frontend Development Only

Backend is running elsewhere, you only need frontend.

**Setup:**
1. Create `.env`:
   ```env
   VITE_API_URL=http://your-backend-server:5000
   ```
2. Start frontend only:
   ```bash
   docker-compose up --build frontend
   ```

---

## Stopping Services

```bash
# Stop all running services
docker-compose down

# Stop and remove volumes (clears data)
docker-compose down -v

# Stop specific services
docker-compose stop frontend
docker-compose stop backend
docker-compose stop allegrograph
```

---

## Troubleshooting

### "Cannot connect to AllegroGraph"

**If using Docker AllegroGraph:**
- Ensure it's running: `docker-compose ps`
- Check logs: `docker-compose logs allegrograph`
- Use `AGRAPH_HOST=allegrograph` in `.env`

**If using external AllegroGraph:**
- Use correct IP/hostname in `.env`
- Use `host.docker.internal` for host machine
- Ensure firewall allows connection

### "Port already in use"

**Option 1: Change ports in `docker-compose.yml`:**
```yaml
ports:
  - "8080:80"  # Change frontend to 8080
  - "5001:5000"  # Change backend to 5001
```

**Option 2: Stop conflicting service:**
```bash
# Find what's using port 80
netstat -ano | findstr :80

# Stop Docker service using it
docker stop <container-id>
```

### "Service 'backend' depends on service 'allegrograph' which is undefined"

You're trying to start backend without AllegroGraph dependency. Use:

```bash
docker-compose up --build backend
```

Instead of:
```bash
docker-compose --profile backend up --build
```

---

## Quick Reference

| Command | Services Started |
|---------|------------------|
| `docker-compose --profile full up` | All (Frontend + Backend + AG) |
| `docker-compose up frontend backend` | Frontend + Backend only |
| `docker-compose up backend allegrograph` | Backend + AllegroGraph only |
| `docker-compose up frontend` | Frontend only |
| `docker-compose up backend` | Backend only |
| `docker-compose up allegrograph` | AllegroGraph only |

---

## Default Behavior

Without profiles specified, **no services start by default** to prevent accidental resource usage.

To change default behavior, add this to your `.env`:

```env
COMPOSE_PROFILES=full
```

Then `docker-compose up` will start all services.
