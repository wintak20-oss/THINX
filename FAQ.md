# Thinx - Frequently Asked Questions (FAQ)

**Quick Navigation:**
- [Absolute Beginner Questions](#absolute-beginner-questions)
- [Getting Started](#getting-started)
- [Installation and Setup](#installation-and-setup)
- [Using the Interface](#using-the-interface)
- [Data and Connections](#data-and-connections)
- [AI Smart Mapper](#ai-smart-mapper)
- [Troubleshooting Errors](#troubleshooting-errors)
- [Privacy and Security](#privacy-and-security)
- [Technical Questions](#technical-questions)

---

## Absolute Beginner Questions

### I've never used anything like this before. Where do I start?

Step-by-step path:

1. Read [QUICK_START.md](QUICK_START.md) - takes 5 minutes
2. Install Docker: [Docker Desktop](https://docker.com/get-started) - takes 10 minutes
3. Start Thinx: Run one command in terminal - takes 2-3 minutes
4. Access application: Open browser to http://localhost

Total time from zero to running: 20 minutes

### What is a "terminal" or "command prompt"?

**Windows:** Press `Windows Key + R`, type `powershell`, press Enter. A blue window opens.

**Mac:** Press `Command + Space`, type `terminal`, press Enter. A window opens.

This window lets you type commands to your computer.

### What does "localhost" mean?

**Localhost = Your own computer**

When you see `http://localhost`, it means "open this website that's running on MY computer, not the internet."

Analogy: Like having a private website that only you can see, running on your laptop.

### Do I need to be connected to the internet?

**For installation: Yes** (to download Docker and Thinx)

**For using Thinx: No** (works completely offline after installation)

**Exception:** AI Smart Mapper downloads models from internet (one-time, optional)

### What if something goes wrong?

**First:** Check [Troubleshooting Errors](#troubleshooting-errors) section below

**Second:** Look at the error message - it usually tells you what's wrong

**Third:** Contact your system administrator or research coordinator

Note: You can't break anything. If stuck, close everything and restart.

### I'm not good with computers. Is this for me?

Thinx is designed for researchers, not programmers.

**You don't need to know:**
- How to code
- How databases work
- What RDF means
- How Docker works

**You only need to know:**
- How to open files
- How to click buttons
- How to fill in forms

If you can use Excel or Word, you can use Thinx.

---

## Getting Started

### What is Thinx?

Thinx is a web-based platform that helps researchers analyze human trafficking and migration data. It provides:
- Connection to research databases without programming
- Visualization of victim data with dashboards and charts
- AI to automatically organize interview data
- Query tools to find patterns and insights

Think of it as a user-friendly interface for exploring complex research databases.

### Who is Thinx for?

- Social science researchers studying human trafficking
- Data analysts working with interview data
- NGO workers analyzing humanitarian data
- Graduate students learning data science methods

No programming experience required.

### Do I need to know programming?

No. Thinx is designed for non-technical users. You can:
- Click buttons to connect to databases
- Use dropdowns to select options
- Fill in forms to configure settings
- View data in tables and charts

Optional: Advanced users can write custom SPARQL queries, but it's not required.

### How long does it take to get started?

- Installation: 5-10 minutes (first time)
- Setup: 2-3 minutes (create connection)
- Learning: 15-30 minutes (explore features)

Total: You can be exploring data in under 20 minutes.

---

## Installation and Setup

### What do I need to install?

**Only one thing:** Docker Desktop

- **Download:** [docker.com/get-started](https://docker.com/get-started)
- **Size:** Approximately 500MB download
- **Requirements:** 
  - Windows 10/11 (Pro, Enterprise, or Education) OR Windows 10 Home with WSL2
  - Mac OS 10.15 or newer
  - 4GB RAM minimum (8GB recommended)
  - 10GB free disk space

Everything else runs inside Docker containers.

### Do I need to install Python, Node.js, or other tools?

No. Docker includes everything you need:
- Python (backend)
- Node.js (frontend)
- Database (AllegroGraph)
- AI models (Ollama)

You don't install anything manually.

### How much disk space does Thinx need?

| Component | Size | When Needed |
|-----------|------|-------------|
| Docker images | 2-3 GB | Always (first time) |
| AI model (optional) | 2-5 GB | Only if using AI mapper |
| Your data | Varies | Depends on dataset size |
| **Total** | **4-10 GB** | |

Tip: Use `docker system prune` to clean up old containers and free space.

### Can I run Thinx without Docker?

Not recommended for non-technical users. Docker is the easiest way.

**For developers:** Yes, you can run components locally:
- Frontend: `npm install && npm run dev`
- Backend: `pip install -r requirements.txt && python app.py`
- Database: Install AllegroGraph separately

See [README.md - Developer Guide](README.md#developer-guide) for details.

### My antivirus is blocking Docker. What should I do?

**Common with:** Norton, McAfee, Kaspersky

**Solution:**
1. Add Docker to your antivirus "exceptions" or "whitelist"
2. Specifically allow: `Docker Desktop.exe` and `dockerd.exe`
3. Restart Docker Desktop

**Still blocked?** Contact your IT department for permission.

---

## Using the Interface

### How do I start Thinx?

1. Open terminal/command prompt:
   - Windows: Search for "PowerShell"
   - Mac: Search for "Terminal"

2. Navigate to project folder:
   ```bash
   cd path/to/DataScienceInPractice
   ```

3. Start Docker containers:
   ```bash
   docker-compose --profile full up
   ```

4. Open your browser: http://localhost

Detailed instructions: See [QUICK_START.md](QUICK_START.md)

### How do I stop Thinx?

**Option 1 - Keep data, stop services:**
```
1. Go to the terminal with running services
2. Press Ctrl+C
3. Type: docker-compose down
```

**Option 2 - Stop everything (faster):**
```bash
docker-compose stop
```

**Next time:** Run `docker-compose up` (no `--build` needed)

### Can I access Thinx from another computer?

**On the same network:** Yes

1. Find your computer's IP address:
   - Windows: `ipconfig` (look for IPv4 Address)
   - Mac: System Preferences → Network

2. On another computer, open browser to:
   ```
   http://YOUR_IP_ADDRESS
   ```

**Example:** `http://192.168.1.100`

**Security Warning:** This exposes Thinx to your local network. Only use on trusted networks.

### What browsers work best?

| Browser | Status | Notes |
|---------|--------|-------|
| Chrome | Recommended | Fully tested |
| Firefox | Recommended | Fully tested |
| Edge | Supported | Works well |
| Safari | Supported | Mac/iOS |
| Internet Explorer | Not supported | Too old |

**Minimum versions:** Released in the last 2 years

---

## Data and Connections

### What is a "connection"?

A connection is like a bookmark to a research database. It stores:
- Where the database is located (server address)
- How to log in (username and password)
- Which dataset to access (repository name)

You create connections so Thinx knows where to find your data.

### Where do I get connection credentials?

From your:
- Research coordinator (academic projects)
- Data provider (NGO or research institution)
- IT department (organizational databases)
- Project documentation (if self-hosting)

**Typically includes:**
- Server URL (e.g., `192.168.1.100` or `research.university.edu`)
- Port number (usually `10035` for AllegroGraph)
- Repository name (e.g., `humantrafficking`)
- Username and password

### Can I connect to multiple databases?

Yes. You can save multiple connections and switch between them.

**Example use case:**
- Connection 1: "Libya Study 2023"
- Connection 2: "Mediterranean Routes 2024"
- Connection 3: "Test Data"

Click "Activate" on any connection to view that dataset.

### What data formats does Thinx support?

**For uploading/processing:**
- CSV (Comma-separated values)
- Excel (`.xlsx`, `.xls`)
- JSON (for advanced users)

**For storage:**
- RDF (Resource Description Framework) - handled automatically
- Stored in AllegroGraph database

### Can I upload my own data?

Yes. Follow this workflow:

1. **Prepare your data:**
   - Format: CSV or Excel
   - Include column headers
   - Use descriptive column names

2. **Upload through interface:**
   - Go to Step 2: Upload Data
   - Click "Choose File"
   - Select your file

3. **Map columns (optional):**
   - Use AI Smart Mapper to auto-organize
   - Or manually map columns to CDM fields

4. **Process to RDF:**
   - Follow the workflow steps
   - Data converts to RDF format

5. **Upload to database:**
   - Use `push_to_allegrograph.py` script
   - Or import through AllegroGraph interface

See [README.md - Data Processing Pipeline](README.md#data-processing-pipeline)

### What is RDF and why do I need it?

**RDF = Resource Description Framework**

**Simple explanation:** A way of storing data that shows relationships between things.

**Example:**
- Traditional table: `[Victim: Ahmed, Age: 25, Nationality: Syrian]`
- RDF: `Ahmed -> is a -> Victim`, `Ahmed -> has age -> 25`, `Ahmed -> has nationality -> Syrian`

**Why it matters:**
- Better for complex relationships (victim → incident → trafficker → location)
- Enables powerful queries (find all victims who crossed border X)
- Standard format for research data sharing

**Do I need to understand RDF?** No. Thinx handles it automatically.

---

## AI Smart Mapper

### What does the AI Smart Mapper do?

**Problem:** Your data has columns like:
```
name | age | gender | country | date | trafficker
```

**But Thinx needs:**
```
Victim.name | Victim.age | Victim.gender | Victim.nationality | Incident.date | Trafficker.name
```

**Solution:** AI reads your columns and automatically suggests the correct mapping.

### Is my data sent to the internet?

No. The AI runs 100% locally on your computer (or your organization's server).

**How we ensure privacy:**
- AI model runs in Docker container
- No external API calls
- No data uploaded to cloud services
- No internet connection required (after model download)

This is called "local AI" or "on-premise AI."

### Which AI model should I use?

**For most users:** `llama3.2`

| Model | Size | Speed | Accuracy | When to Use |
|-------|------|-------|----------|-------------|
| **llama3.2** | 2GB | Fast | Good | Start here - best balance |
| **phi3** | 2.3GB | Very Fast | Good | Older/slower computers |
| **mistral** | 4GB | Medium | Excellent | Need better accuracy |
| **gemma2:2b** | 1.6GB | Very Fast | Decent | Quick testing only |
| **llama3:8b** | 4.7GB | Slow | Excellent | Maximum accuracy needed |

Don't overthink it. Try `llama3.2` first - it works well for 90% of cases.

### How long does AI mapping take?

| Step | Time |
|------|------|
| Download model (first time) | 5-15 minutes |
| Analyze your data | 30-90 seconds |
| Apply mappings | 1-2 seconds |

**Total first time:** Approximately 20 minutes  
**Subsequent uses:** Approximately 1 minute

### Can I manually fix AI suggestions?

Feature may vary by implementation. Typically:

**Option 1 - Edit before applying:**
- Review suggestion table
- Modify incorrect mappings
- Click "Apply"

**Option 2 - Fix after applying:**
- Re-upload original file
- Manually rename columns in Excel/CSV
- Upload corrected version

**Option 3 - Skip AI entirely:**
- Name your columns correctly from the start
- Use format: `Entity.field` (e.g., `Victim.age`)

---

## Troubleshooting Errors

### "Connection refused" when accessing http://localhost

**Cause:** Docker containers haven't finished starting

**Solution:**
1. Wait 30 more seconds
2. Refresh browser (press F5)
3. Check terminal for "ready" messages
4. Verify Docker is running (check system tray)

**If still failing:**
```bash
docker-compose ps
# All containers should show "Up" status
```

### "Port already in use" error when starting

**Cause:** Something else is using port 80 (common: IIS, XAMPP, Apache)

**Solution A - Stop other services:**
1. Check if you have other web servers running
2. Stop them (XAMPP control panel, IIS Manager, etc.)
3. Try starting Thinx again

**Solution B - Find what's using the port:**

**Windows:**
```bash
netstat -ano | findstr :80
```
Note the PID (last number), then:
```bash
taskkill /PID [number] /F
```

**Mac/Linux:**
```bash
lsof -i :80
```

**Solution C - Use different port:**
Edit `docker-compose.yml`:
```yaml
frontend:
  ports:
    - "8080:80"  # Change 80 to 8080
```
Then access at: http://localhost:8080

### "Cannot connect to Docker daemon"

**Cause:** Docker Desktop isn't running

**Solution:**
1. Open Docker Desktop application
2. Wait for whale icon to stop animating (in system tray)
3. Icon should say "Docker Desktop is running"
4. Try your command again

**Still not working:**
```bash
docker --version
# Should show Docker version. If error, Docker isn't installed.
```

### "No data found" after connecting

**Cause:** Database repository is empty

**Solution:**
1. You need to load data into the database first
2. **Option A:** Use mock data - see `Mock data/README.md`
3. **Option B:** Process your own data - see [README.md](README.md#data-processing-pipeline)
4. **Option C:** Ask data provider if data was uploaded

### "Failed to connect to AllegroGraph"

**Cause:** Database isn't running or credentials are wrong

**Solution:**
1. Check if AllegroGraph is running:
   ```bash
   docker-compose ps allegrograph
   # Should show "Up"
   ```

2. Try accessing AllegroGraph directly:
   - Open http://localhost:10035
   - Can you log in?

3. Verify credentials:
   - Default username: `admin`
   - Default password: `admin123`
   - Repository must exist (create in AllegroGraph interface)

4. Check server address in connection form:
   - Using Docker: Enter `allegrograph`
   - External server: Enter IP or domain name

### Website shows "502 Bad Gateway"

**Cause:** Backend is still starting or crashed

**Solution:**
1. Wait 30 seconds and refresh
2. Check backend logs:
   ```bash
   docker-compose logs backend
   ```
3. Look for errors in output
4. Common issues:
   - Python package import errors
   - Configuration problems
   - Port conflicts

**If backend crashed:**
```bash
docker-compose restart backend
```

### AI mapper returns all "null" or empty results

**Cause:** AI couldn't understand your column names

**Solutions:**

**Option 1 - Better column names:**
Your column names might be too vague:
- Bad: `col1`, `field_a`, `data`
- Good: `victim_age`, `incident_type`, `trafficker_name`

Rename columns in Excel/CSV before uploading.

**Option 2 - Try different model:**
- Download `mistral` or `llama3:8b`
- These understand ambiguous names better

**Option 3 - Check data format:**
- Is first row your column headers?
- Are there special characters?
- Is file a valid CSV/Excel?

---

## Privacy and Security

### Is Thinx GDPR compliant?

Yes, when used correctly:

- Data minimization - Only collect necessary fields
- Local processing - AI runs on your infrastructure
- Access control - Username/password authentication
- Anonymization - System marks sensitive fields
- Data retention - You control data lifecycle

**Your responsibilities:**
- Use appropriate consent forms for data collection
- Anonymize data before uploading
- Secure your Docker host environment
- Follow your organization's data policies

### Who can access my data?

**Default setup:**
- Anyone on your computer (local access)
- Anyone on your local network (if exposed)

**How to secure:**

**Option 1 - Localhost only (default):**
```yaml
# docker-compose.yml
ports:
  - "127.0.0.1:80:80"  # Only accessible from this computer
```

**Option 2 - Password protection:**
- Enable authentication in settings
- Require login for all users

**Option 3 - Firewall rules:**
- Configure Windows/Mac firewall
- Block external access to ports 80, 5000, 10035

**For production:** Deploy behind institutional firewall or VPN.

### Can I use Thinx for sensitive research data?

Yes, but with precautions:

**Do:**
- Anonymize data before uploading (remove names, IDs, contact info)
- Run on secure, institutional servers
- Use strong passwords for database
- Enable access logs
- Follow ethical review board requirements

**Don't:**
- Upload personally identifiable information (PII)
- Run on public networks (coffee shops, etc.)
- Share database credentials
- Use weak passwords

Consult your ethics board and data protection officer.

### What data does Thinx collect about me?

**Thinx collects:**
- Connection configurations (server addresses, repository names)
- Usernames (for authentication)
- Hashed passwords (encrypted, not plaintext)
- Activity logs (optional, for troubleshooting)

**Thinx does NOT collect:**
- Your research data (stays in your database)
- Usage analytics
- Personal information
- Telemetry data

Everything is stored locally in Docker volumes.

---

## Technical Questions

### What ports does Thinx use?

| Port | Service | Purpose | Can I Change It? |
|------|---------|---------|------------------|
| 80 | Frontend | Web interface | Yes (edit docker-compose.yml) |
| 5000 | Backend | API server | Yes |
| 10035 | AllegroGraph | Database | Yes |
| 11434 | Ollama | AI service | Yes |

### How do I update Thinx to the latest version?

```bash
# Stop containers
docker-compose down

# Pull latest code (if using Git)
git pull origin main

# Rebuild containers
docker-compose --profile full up --build
```

Note: This preserves your data in Docker volumes.

### How do I backup my data?

**Option 1 - Backup Docker volumes:**
```bash
# Export volume to tar file
docker run --rm -v datascienceinpractice_agraph_data:/data -v $(pwd):/backup alpine tar czf /backup/agraph_backup.tar.gz /data
```

**Option 2 - Backup from AllegroGraph:**
1. Open http://localhost:10035
2. Select your repository
3. Go to "Administration" → "Backup"
4. Download backup file

**Option 3 - Export as RDF:**
```bash
# Through SPARQL query that exports all triples
```

### Can I run Thinx on a server?

Yes. Deploy on:
- University research servers
- Cloud VMs (AWS, Azure, Google Cloud)
- On-premise servers
- Raspberry Pi (for lightweight use)

**Requirements:**
- Docker installed
- Ports open (80, 5000, 10035)
- Sufficient RAM (4GB minimum, 8GB recommended)

**Security recommendations:**
- Use HTTPS (reverse proxy like Nginx)
- Enable firewall
- Strong passwords
- Regular updates

### How do I contribute or report bugs?

**Report bugs:**
1. Check if issue already exists on GitHub
2. Create new issue with:
   - Operating system
   - Docker version
   - Steps to reproduce
   - Error messages
   - Screenshots (if applicable)

**Contribute:**
1. Fork the repository
2. Create feature branch
3. Make your changes
4. Submit pull request

**Repository:** https://github.com/Justin2280/DataScienceInPractice

---

## Still Have Questions?

### Documentation

- [README.md](README.md) - Complete user guide
- [QUICK_START.md](QUICK_START.md) - Installation guide
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - Technical details
- [docs/AI_MAPPER.md](docs/AI_MAPPER.md) - AI guide
- [Mock data/README.md](Mock data/README.md) - Test data tutorials

### Debugging

```bash
# Check all containers
docker-compose ps

# View logs
docker-compose logs

# View specific service logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs allegrograph

# Check Docker version
docker --version
docker-compose --version
```

### Get Help

**Before asking:**
1. Search this FAQ
2. Check documentation
3. Review error logs
4. Try mock data to isolate issue

**When asking:**
Include:
- Operating system and version
- Docker version
- Exact error message
- Steps to reproduce
- What you've tried already
