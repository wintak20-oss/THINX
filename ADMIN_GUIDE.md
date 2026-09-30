# Thinx Administrator Guide
## Central Deployment and System Management

---

## Table of Contents

1. [Overview](#overview)
2. [System Requirements](#system-requirements)
3. [Installation and Deployment](#installation-and-deployment)
4. [Configuration](#configuration)
5. [User Management](#user-management)
6. [Database Management](#database-management)
7. [Security and Access Control](#security-and-access-control)
8. [Monitoring and Maintenance](#monitoring-and-maintenance)
9. [Backup and Recovery](#backup-and-recovery)
10. [Troubleshooting](#troubleshooting)
11. [Scaling and Performance](#scaling-and-performance)

---

## Overview

### Purpose of This Guide

This guide is for system administrators responsible for:
- Deploying Thinx in central or production environments
- Managing user accounts and access
- Maintaining database and services
- Ensuring security and compliance
- Supporting researchers using the platform

### Architecture Summary

Thinx consists of three main components:

```
┌─────────────────────────────────────────────┐
│  Frontend (Vue.js)                          │
│  - User interface                           │
│  - Port 80 (HTTP)                           │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│  Backend (Flask/Python)                     │
│  - API server                               │
│  - Business logic                           │
│  - Port 5000                                │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│  AllegroGraph Database                      │
│  - RDF triple store                         │
│  - Port 10035                               │
└─────────────────────────────────────────────┘
```

**Optional Components:**
- Ollama (for AI Smart Mapper): Port 11434
- Reverse Proxy (Nginx/Apache): For HTTPS/SSL

---

## System Requirements

### Hardware Requirements

**Minimum (Testing/Small Teams):**
- CPU: 2 cores
- RAM: 4GB
- Storage: 20GB
- Network: 100 Mbps

**Recommended (Production):**
- CPU: 4+ cores
- RAM: 8GB+ (16GB for AI features)
- Storage: 100GB+ SSD
- Network: 1 Gbps

**Large Scale (Multiple Teams, Big Datasets):**
- CPU: 8+ cores
- RAM: 16GB+ (32GB with AI)
- Storage: 500GB+ SSD
- Network: 1 Gbps+ with load balancing

### Software Requirements

**Required:**
- Docker Engine 20.10+
- Docker Compose 1.29+
- Modern web browser (for admin interface)

**Operating System:**
- Linux (Ubuntu 20.04+, RHEL 8+, Debian 11+) - Recommended
- Windows Server 2019+ with WSL2
- macOS 11+ (for development/testing only)

**Network:**
- Static IP or DNS name
- Firewall rules for required ports
- SSL certificate for HTTPS (optional)

---

## Installation and Deployment

### Quick Deployment (Development/Testing)

1. Clone the repository:
   ```bash
   git clone https://github.com/Justin2280/DataScienceInPractice.git
   cd DataScienceInPractice
   ```

2. Run the full system:
   ```bash
   docker-compose --profile full up -d
   ```

3. Access the platform:
   - Frontend: http://localhost
   - Backend API: http://localhost:5000
   - AllegroGraph: http://localhost:10035

### Production Deployment

Note: See the [Production Deployment Checklist](#production-deployment-checklist) at the end of this guide before starting.

#### Step 1: Prepare the Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add your user to docker group
sudo usermod -aG docker $USER
# Log out and back in for this to take effect
```

#### Step 2: Clone and Configure

```bash
# Clone repository
cd /opt
sudo git clone https://github.com/Justin2280/DataScienceInPractice.git thinx
cd thinx
sudo chown -R $USER:$USER .
```

#### Step 3: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit with production values
nano .env
```

**Key environment variables to set:**

```bash
# Application
FLASK_ENV=production
SECRET_KEY=<generate-a-strong-random-key>

# Database
AGRAPH_HOST=allegrograph
AGRAPH_PORT=10035
AGRAPH_REPOSITORY=humantrafficking
AGRAPH_USER=admin
AGRAPH_PASSWORD=<strong-password>

# Frontend
FRONTEND_URL=http://your-domain.com
BACKEND_URL=http://your-domain.com/api

# Security
ALLOWED_ORIGINS=http://your-domain.com,https://your-domain.com
SESSION_TIMEOUT=3600

# Optional: AI Features
OLLAMA_ENABLED=true
OLLAMA_MODEL=llama3.2
```

#### Step 4: Generate Strong Keys

```bash
# Generate SECRET_KEY
python3 -c "import secrets; print(secrets.token_hex(32))"

# Generate AllegroGraph password
python3 -c "import secrets; print(secrets.token_urlsafe(16))"
```

#### Step 5: Deploy Services

```bash
# Start services
docker-compose --profile full up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

#### Step 6: Initialize Database

```bash
# Create AllegroGraph repository
docker-compose exec backend python -c "
from utils.allegrograph import AllegroGraphClient
client = AllegroGraphClient('allegrograph', 10035, 'humantrafficking', 'admin', 'your-password')
print('Database initialized')
"
```

#### Step 7: Create First Admin User

```bash
# Access backend container
docker-compose exec backend python

# In Python shell:
from models import UserManager
from pathlib import Path

user_manager = UserManager(Path('data/users.json'))
admin = user_manager.create_user('admin', 'your-secure-password')
print(f"Admin user created: {admin['username']}")
exit()
```

---

## Configuration

### Docker Compose Profiles

Thinx supports different deployment profiles:

**Full Profile (All features):**
```bash
docker-compose --profile full up -d
```
Includes: Frontend, Backend, AllegroGraph, Ollama

**No-AI Profile (Without AI features):**
```bash
docker-compose --profile no-ai up -d
```
Includes: Frontend, Backend, AllegroGraph

**Minimal Profile (Core only):**
```bash
docker-compose up -d
```
Includes: Frontend, Backend (requires external AllegroGraph)

### Application Configuration

`backend/config.py` - Main configuration file:

```python
import os

class Config:
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', 3600))
    
    # Database
    AGRAPH_HOST = os.getenv('AGRAPH_HOST', 'allegrograph')
    AGRAPH_PORT = int(os.getenv('AGRAPH_PORT', 10035))
    AGRAPH_REPOSITORY = os.getenv('AGRAPH_REPOSITORY', 'humantrafficking')
    
    # CORS
    ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost').split(',')
    
    # Uploads
    MAX_UPLOAD_SIZE = int(os.getenv('MAX_UPLOAD_SIZE', 52428800))  # 50MB
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', '/app/uploads')
    
    # AI Features
    OLLAMA_ENABLED = os.getenv('OLLAMA_ENABLED', 'true').lower() == 'true'
    OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'ollama')
    OLLAMA_PORT = int(os.getenv('OLLAMA_PORT', 11434))
```

### Reverse Proxy (Production)

For HTTPS and domain names, configure Nginx:

```nginx
# /etc/nginx/sites-available/thinx

upstream thinx_frontend {
    server localhost:80;
}

upstream thinx_backend {
    server localhost:5000;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/ssl/certs/your-domain.crt;
    ssl_certificate_key /etc/ssl/private/your-domain.key;
    
    # Frontend
    location / {
        proxy_pass http://thinx_frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Backend API
    location /api {
        proxy_pass http://thinx_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Longer timeout for data processing
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
    }
    
    # File upload limit
    client_max_body_size 50M;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/thinx /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## User Management

### Creating Users

**Method 1: Via Python Script**

Create `scripts/create_user.py`:

```python
#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from models import UserManager

def create_user(username, password):
    user_manager = UserManager(Path('backend/data/users.json'))
    try:
        user = user_manager.create_user(username, password)
        print(f"User created successfully: {user['username']}")
        print(f"   User ID: {user['id']}")
    except ValueError as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python create_user.py <username> <password>")
        sys.exit(1)
    
    create_user(sys.argv[1], sys.argv[2])
```

Usage:
```bash
python scripts/create_user.py researcher1 SecurePassword123
```

**Method 2: Via Docker Exec**

```bash
docker-compose exec backend python -c "
from models import UserManager
from pathlib import Path
um = UserManager(Path('data/users.json'))
user = um.create_user('researcher1', 'SecurePassword123')
print(f'Created: {user[\"username\"]}')
"
```

### Managing Users

**List all users:**

```bash
docker-compose exec backend python -c "
from models import UserManager
from pathlib import Path
import json
um = UserManager(Path('data/users.json'))
users = um.users
for u in users.values():
    print(f'{u[\"id\"]}: {u[\"username\"]} (created: {u[\"created_at\"]})')
"
```

**Delete a user:**

```bash
docker-compose exec backend python -c "
from models import UserManager
from pathlib import Path
um = UserManager(Path('data/users.json'))
um.delete_user('user_id_here')
print('User deleted')
"
```

**Reset user password:**

```bash
docker-compose exec backend python -c "
from models import UserManager
from pathlib import Path
um = UserManager(Path('data/users.json'))
um.reset_password('username', 'NewSecurePassword123')
print('Password reset successful')
"
```

### User Registration

By default, the platform allows self-registration. To disable:

`backend/app.py` - Comment out or remove the register endpoint:

```python
# @app.route('/api/register', methods=['POST'])
# def register():
#     ...
```

Or add admin-only registration:

```python
@app.route('/api/register', methods=['POST'])
def register():
    # Check if requester is admin
    admin_key = request.headers.get('X-Admin-Key')
    if admin_key != os.getenv('ADMIN_KEY'):
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    # ... rest of registration logic
```

---

## Database Management

### AllegroGraph Administration

**Access AllegroGraph WebView:**
```
http://your-server:10035
```

Default credentials (change immediately):
- Username: `admin`
- Password: Set in `.env`

### Creating Repositories

**Via Docker:**
```bash
docker-compose exec allegrograph agraph-python
```

```python
from franz.openrdf.sail.allegrographserver import AllegroGraphServer

server = AllegroGraphServer('localhost', port=10035, user='admin', password='your-password')
catalog = server.openCatalog('')
repo = catalog.createRepository('humantrafficking')
print("Repository created")
```

**Via WebView:**
1. Go to http://your-server:10035
2. Login
3. Navigate to "Repositories"
4. Click "Create Repository"
5. Name: `humantrafficking`
6. Click "Create"

### Loading the CDM Ontology

```bash
# Copy CDM file into container
docker cp hds_cdm.ttl thinx_backend:/tmp/

# Load into AllegroGraph
docker-compose exec backend python << EOF
from utils.allegrograph import AllegroGraphClient

client = AllegroGraphClient('allegrograph', 10035, 'humantrafficking', 'admin', 'your-password')
with open('/tmp/hds_cdm.ttl', 'r') as f:
    client.upload_rdf(f.read(), format='turtle')
print("CDM ontology loaded")
EOF
```

### Database Queries

**Count all victims:**
```sparql
PREFIX ex: <http://example.org/ontology#>
SELECT (COUNT(DISTINCT ?victim) as ?count)
WHERE {
  ?victim a ex:Victim .
}
```

**Export data:**
```bash
# Via curl
curl -X POST http://localhost:10035/repositories/humantrafficking/export \
  -u admin:password \
  -H "Accept: application/x-turtle" \
  -o export.ttl
```

---

## Security and Access Control

### Security Best Practices

1. **Change Default Passwords Immediately**
   ```bash
   # AllegroGraph
   docker-compose exec allegrograph agraph-control --password
   
   # Admin user
   # Use user management commands above
   ```

2. **Use Strong Secrets**
   ```bash
   # Generate secure random strings
   openssl rand -hex 32  # For SECRET_KEY
   openssl rand -base64 24  # For passwords
   ```

3. **Enable HTTPS**
   - Use Let's Encrypt for free SSL certificates
   - Configure reverse proxy (see above)
   - Redirect all HTTP to HTTPS

4. **Firewall Configuration**
   ```bash
   # Allow only necessary ports
   sudo ufw default deny incoming
   sudo ufw default allow outgoing
   sudo ufw allow 22/tcp   # SSH
   sudo ufw allow 80/tcp   # HTTP
   sudo ufw allow 443/tcp  # HTTPS
   sudo ufw enable
   ```

5. **Regular Updates**
   ```bash
   # Update Docker images
   docker-compose pull
   docker-compose up -d
   
   # Update system
   sudo apt update && sudo apt upgrade -y
   ```

### Access Control

**Network-Level:**
- Use VPN for remote access
- Whitelist IP addresses in firewall
- Use private networks for internal services

**Application-Level:**
- Implement role-based access control (future enhancement)
- Log all user actions
- Set session timeouts

**Data-Level:**
- Encrypt sensitive data at rest
- Use AllegroGraph's access control features
- Audit data access regularly

### GDPR Compliance

1. **Data Protection Officer**
   - Designate a DPO for your organization
   - Document data processing activities

2. **Privacy by Design**
   - Minimize data collection
   - Implement data retention policies
   - Enable data anonymization features

3. **User Rights**
   - Right to access: Provide data export functionality
   - Right to erasure: Implement user deletion scripts
   - Right to portability: Export in machine-readable formats

4. **Data Breach Protocol**
   - Monitor logs for suspicious activity
   - Have incident response plan
   - Document and report breaches within 72 hours

---

## Monitoring and Maintenance

### Health Checks

**Check service status:**
```bash
docker-compose ps
```

**Check API health:**
```bash
curl http://localhost:5000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "flask_api",
  "timestamp": "2025-12-07T12:00:00"
}
```

### Log Management

**View logs:**
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f allegrograph

# Last N lines
docker-compose logs --tail=100 backend
```

**Log rotation:**

Create `/etc/logrotate.d/docker-containers`:
```
/var/lib/docker/containers/*/*.log {
  rotate 7
  daily
  compress
  missingok
  delaycompress
  copytruncate
}
```

### Resource Monitoring

**Using Docker stats:**
```bash
docker stats
```

**Using htop:**
```bash
sudo apt install htop
htop
```

**Monitoring disk space:**
```bash
df -h
docker system df
```

**Clean up unused resources:**
```bash
# Remove unused containers, images, networks
docker system prune -a

# Clean old logs
docker-compose logs --tail=0 -f > /dev/null &
```

### Scheduled Maintenance

**Create maintenance script** (`/opt/thinx/maintenance.sh`):

```bash
#!/bin/bash
LOG_FILE="/var/log/thinx-maintenance.log"

echo "[$(date)] Starting maintenance..." >> $LOG_FILE

# Backup database
cd /opt/thinx
./scripts/backup.sh >> $LOG_FILE 2>&1

# Clean up old logs
docker-compose logs --tail=0 -f > /dev/null &

# Update images
docker-compose pull >> $LOG_FILE 2>&1

# Restart services
docker-compose restart >> $LOG_FILE 2>&1

echo "[$(date)] Maintenance complete" >> $LOG_FILE
```

**Schedule with cron:**
```bash
sudo crontab -e

# Add line for weekly maintenance (Sunday 2 AM):
0 2 * * 0 /opt/thinx/maintenance.sh
```

---

## Backup and Recovery

### Backup Strategy

**What to backup:**
1. User data (`backend/data/users.json`)
2. Connection configurations (`backend/data/connections.json`)
3. AllegroGraph database
4. Application configuration (`.env`)
5. Uploaded files (`uploads/`)

### Automated Backup Script

Create `scripts/backup.sh`:

```bash
#!/bin/bash

BACKUP_DIR="/backups/thinx/$(date +%Y-%m-%d_%H-%M-%S)"
mkdir -p "$BACKUP_DIR"

echo "Backing up to $BACKUP_DIR"

# Backup user data
docker cp thinx_backend:/app/data "$BACKUP_DIR/"

# Backup uploads
docker cp thinx_backend:/app/uploads "$BACKUP_DIR/"

# Backup AllegroGraph
docker-compose exec -T allegrograph agraph-backup \
  --repo humantrafficking \
  --output /tmp/ag-backup.tar.gz

docker cp thinx_allegrograph:/tmp/ag-backup.tar.gz "$BACKUP_DIR/"

# Backup configuration
cp .env "$BACKUP_DIR/"
cp docker-compose.yml "$BACKUP_DIR/"

# Create archive
cd /backups/thinx
tar -czf "$(date +%Y-%m-%d_%H-%M-%S).tar.gz" "$(date +%Y-%m-%d_%H-%M-%S)"
rm -rf "$(date +%Y-%m-%d_%H-%M-%S)"

# Keep only last 30 days
find /backups/thinx -name "*.tar.gz" -mtime +30 -delete

echo "Backup complete"
```

Make executable and schedule:
```bash
chmod +x scripts/backup.sh

# Daily backup at 1 AM
echo "0 1 * * * /opt/thinx/scripts/backup.sh" | sudo crontab -
```

### Recovery Procedure

**Full system recovery:**

```bash
# 1. Extract backup
cd /backups/thinx
tar -xzf 2025-12-07_01-00-00.tar.gz
cd 2025-12-07_01-00-00

# 2. Restore configuration
cp .env /opt/thinx/
cp docker-compose.yml /opt/thinx/

# 3. Start services
cd /opt/thinx
docker-compose down
docker-compose up -d

# 4. Restore user data
docker cp data/ thinx_backend:/app/
docker cp uploads/ thinx_backend:/app/

# 5. Restore AllegroGraph
docker cp ag-backup.tar.gz thinx_allegrograph:/tmp/
docker-compose exec allegrograph agraph-restore \
  --input /tmp/ag-backup.tar.gz \
  --repo humantrafficking

# 6. Restart services
docker-compose restart

echo "Recovery complete"
```

---

## Troubleshooting

### Common Issues

#### Services Won't Start

**Symptom:** `docker-compose up` fails

**Diagnosis:**
```bash
docker-compose logs
docker-compose ps
```

**Solutions:**
- Check port conflicts: `sudo netstat -tuln | grep LISTEN`
- Verify Docker daemon: `sudo systemctl status docker`
- Check disk space: `df -h`
- Review `.env` configuration

#### Backend API Errors

**Symptom:** 500 errors when accessing API

**Diagnosis:**
```bash
docker-compose logs backend
curl http://localhost:5000/api/health
```

**Solutions:**
- Check AllegroGraph connection
- Verify environment variables
- Restart backend: `docker-compose restart backend`

#### Database Connection Failures

**Symptom:** "Connection refused" or "Authentication failed"

**Diagnosis:**
```bash
# Check AllegroGraph is running
docker-compose ps allegrograph

# Test connection
curl -u admin:password http://localhost:10035/repositories
```

**Solutions:**
- Verify credentials in `.env`
- Check AllegroGraph logs: `docker-compose logs allegrograph`
- Ensure repository exists
- Restart database: `docker-compose restart allegrograph`

#### AI Smart Mapper Not Working

**Symptom:** No AI suggestions or timeout errors

**Diagnosis:**
```bash
docker-compose logs ollama
curl http://localhost:11434/api/tags
```

**Solutions:**
- Verify Ollama is running
- Check model is downloaded
- Increase timeout in backend config
- Try smaller model (phi3 instead of llama)

---

## Scaling and Performance

### Horizontal Scaling

For large deployments, consider:

**Load Balancer Setup:**
```
                      ┌──> Backend Instance 1
                      │
Internet ──> Nginx ───┼──> Backend Instance 2
                      │
                      └──> Backend Instance 3
                               │
                               └──> AllegroGraph Cluster
```

**Docker Swarm Example:**
```yaml
version: '3.8'
services:
  backend:
    deploy:
      replicas: 3
      restart_policy:
        condition: on-failure
```

### Performance Optimization

**Backend:**
- Use gunicorn with multiple workers
- Enable caching for frequent queries
- Optimize database queries

**Database:**
- Add indexes for common queries
- Increase AllegroGraph memory allocation
- Use federation for distributed data

**Frontend:**
- Enable Nginx caching
- Use CDN for static assets
- Implement lazy loading

### Monitoring Tools

**Recommended tools:**
- Prometheus + Grafana: Metrics and dashboards
- ELK Stack: Log aggregation and analysis
- Uptime Kuma: Uptime monitoring
- cAdvisor: Container metrics

---

## Support and Maintenance Contacts

### Documentation
- Main README: `/opt/thinx/README.md`
- User Guide: `/opt/thinx/USER_GUIDE.md`
- FAQ: `/opt/thinx/FAQ.md`

### Community
- GitHub: https://github.com/Justin2280/DataScienceInPractice
- Issues: https://github.com/Justin2280/DataScienceInPractice/issues

### Vendor Support
- AllegroGraph: https://franz.com/agraph/support/
- Docker: https://docs.docker.com/
- Ollama: https://ollama.com/

---

## Production Deployment Checklist

Use this checklist before deploying Thinx to production.

### Pre-Deployment

**System Requirements:**
- [ ] Server meets minimum requirements (4+ CPU cores, 8GB+ RAM, 100GB+ storage)
- [ ] Docker and Docker Compose installed and tested
- [ ] Network ports available: 80/443 (web), 5000 (API), 10035 (database)
- [ ] Static IP or DNS domain name configured
- [ ] SSL certificate obtained (Let's Encrypt or commercial)

**Security Setup:**
- [ ] Generated strong `SECRET_KEY` and added to `.env`
- [ ] Changed default AllegroGraph password
- [ ] Set `FLASK_ENV=production` in `.env`
- [ ] Set `FLASK_DEBUG=false` in `.env`
- [ ] Configured firewall rules (only necessary ports open)
- [ ] Reviewed and set `ALLOWED_ORIGINS` with actual domain(s)
- [ ] Set `SESSION_COOKIE_SECURE=true` if using HTTPS
- [ ] Decided on user registration policy (`ALLOW_REGISTRATION`)

**Configuration:**
- [ ] Copied `.env.example` to `.env`
- [ ] Updated all environment variables with production values
- [ ] Configured AllegroGraph connection details
- [ ] Set appropriate `MAX_UPLOAD_SIZE` for your data
- [ ] Configured log level (`LOG_LEVEL=INFO` recommended)
- [ ] Disabled AI features if not needed (`OLLAMA_ENABLED=false`)
- [ ] Set proper `UPLOAD_RETENTION_DAYS` for data retention compliance

### Deployment

**Initial Deployment:**
- [ ] Cloned repository to `/opt/thinx` (or chosen location)
- [ ] Created `.env` file with production configuration
- [ ] Built and started containers: `docker-compose --profile full up -d`
- [ ] Verified all containers are running: `docker-compose ps`
- [ ] Checked logs for errors: `docker-compose logs`

**Database Initialization:**
- [ ] Created AllegroGraph repository via WebView
- [ ] Loaded CDM ontology (`hds_cdm.ttl`) into repository
- [ ] Tested database connection from backend

**User Management:**
- [ ] Created initial admin user account
- [ ] Tested login functionality
- [ ] Decided on user creation process
- [ ] Created initial researcher accounts if needed

**Reverse Proxy (Optional but Recommended):**
- [ ] Installed and configured Nginx or Apache
- [ ] Configured SSL/TLS with certificates
- [ ] Set up HTTP to HTTPS redirect
- [ ] Tested proxy passes to frontend and backend
- [ ] Configured appropriate timeouts for data processing

### Testing

**Functionality Tests:**
- [ ] Can access frontend via domain/IP
- [ ] Login/logout works correctly
- [ ] Can create database connections
- [ ] Can upload sample data file
- [ ] Data processing workflow completes successfully
- [ ] Can view data in data viewer
- [ ] Can run sample queries
- [ ] AI Smart Mapper works (if enabled)

**Security Tests:**
- [ ] HTTPS enforced (if configured)
- [ ] Session timeouts working
- [ ] Unauthorized access properly blocked
- [ ] Password requirements enforced
- [ ] CORS restrictions working

**Performance Tests:**
- [ ] Page load times acceptable
- [ ] File upload works for maximum size
- [ ] Query responses under 5 seconds (for sample data)
- [ ] Multiple concurrent users can work without issues

### Monitoring and Maintenance

**Monitoring Setup:**
- [ ] Configured health check monitoring
- [ ] Set up log rotation
- [ ] Configured disk space alerts
- [ ] Set up uptime monitoring (optional)

**Backup Configuration:**
- [ ] Created backup script (see Backup and Recovery above)
- [ ] Tested backup and restore procedure
- [ ] Scheduled automatic daily backups (cron)
- [ ] Verified backup storage location and retention
- [ ] Documented restore procedure

**Documentation:**
- [ ] Created admin contact list
- [ ] Documented any custom configurations
- [ ] Created user onboarding guide for your organization
- [ ] Set up support channels (email, help desk)

### Post-Deployment

**User Onboarding:**
- [ ] Sent welcome emails to initial users
- [ ] Provided link to USER_GUIDE.md
- [ ] Conducted training session (optional)
- [ ] Set up feedback mechanism

**Maintenance Schedule:**
- [ ] Scheduled weekly system checks
- [ ] Scheduled monthly security updates
- [ ] Scheduled quarterly data retention reviews
- [ ] Planned backup verification tests

**Monitoring Tasks:**
- [ ] Check logs daily for first week
- [ ] Monitor disk space usage
- [ ] Monitor database size growth
- [ ] Track user registrations and usage

### Compliance and Governance (if applicable)

**GDPR Compliance:**
- [ ] Documented data processing activities
- [ ] Designated Data Protection Officer
- [ ] Created privacy policy
- [ ] Implemented data retention policies
- [ ] Set up data breach response plan
- [ ] Obtained necessary consents from data subjects

**Research Ethics:**
- [ ] Obtained IRB/ethics committee approval
- [ ] Documented data anonymization procedures
- [ ] Set up access control policies
- [ ] Created data sharing agreements
- [ ] Established audit trail procedures

### Deployment Sign-Off

**Deployed on:** _________________  
**Deployed by:** _________________  
**Version:** _________________

**System Administrator:** _____________________ Date: ____________  
**Project Lead:** _____________________ Date: ____________  
**Security Officer:** _____________________ Date: ____________

---

**This guide is maintained by the Thinx development team. Last updated: December 2025.**
