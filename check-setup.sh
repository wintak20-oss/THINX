#!/bin/bash
# Thinx Setup Validation Script
# This script checks if your system is ready to run Thinx

echo "============================================"
echo "  Thinx - System Prerequisites Checker"
echo "============================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check results
declare -a checks=()
fail_count=0
warn_count=0

# Function to add check result
add_check() {
    local name=$1
    local status=$2
    local message=$3
    checks+=("$name|$status|$message")
    
    if [[ $status == *"FAIL"* ]]; then
        ((fail_count++))
    elif [[ $status == *"WARN"* ]]; then
        ((warn_count++))
    fi
}

# Check 1: Docker Installation
echo -e "${YELLOW}[1/6] Checking Docker installation...${NC}"
if command -v docker &> /dev/null; then
    docker_version=$(docker --version)
    echo -e "  ${GREEN}✅ Docker is installed: $docker_version${NC}"
    add_check "Docker Installed" "✅ PASS" "$docker_version"
else
    echo -e "  ${RED}❌ Docker is not installed${NC}"
    echo -e "     ${YELLOW}Download from: https://docker.com/get-started${NC}"
    add_check "Docker Installed" "❌ FAIL" "Not installed"
fi

# Check 2: Docker Running
echo -e "${YELLOW}[2/6] Checking if Docker is running...${NC}"
if docker info &> /dev/null; then
    echo -e "  ${GREEN}✅ Docker is running${NC}"
    add_check "Docker Running" "✅ PASS" "Docker daemon is active"
else
    echo -e "  ${RED}❌ Docker is not running${NC}"
    echo -e "     ${YELLOW}Please start Docker Desktop${NC}"
    add_check "Docker Running" "❌ FAIL" "Docker daemon not responding"
fi

# Check 3: Docker Compose
echo -e "${YELLOW}[3/6] Checking Docker Compose...${NC}"
if command -v docker-compose &> /dev/null; then
    compose_version=$(docker-compose --version)
    echo -e "  ${GREEN}✅ Docker Compose is available: $compose_version${NC}"
    add_check "Docker Compose" "✅ PASS" "$compose_version"
else
    echo -e "  ${RED}❌ Docker Compose is not available${NC}"
    add_check "Docker Compose" "❌ FAIL" "Not installed"
fi

# Check 4: Disk Space
echo -e "${YELLOW}[4/6] Checking available disk space...${NC}"
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    free_space=$(df -g . | awk 'NR==2 {print $4}')
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    free_space=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
else
    free_space=0
fi

if [[ $free_space -ge 10 ]]; then
    echo -e "  ${GREEN}✅ Sufficient disk space: ${free_space}GB available${NC}"
    add_check "Disk Space" "✅ PASS" "${free_space}GB free"
elif [[ $free_space -ge 5 ]]; then
    echo -e "  ${YELLOW}⚠️  Low disk space: ${free_space}GB available (10GB recommended)${NC}"
    add_check "Disk Space" "⚠️  WARN" "${free_space}GB free (low)"
else
    echo -e "  ${RED}❌ Insufficient disk space: Only ${free_space}GB available${NC}"
    echo -e "     ${YELLOW}10GB minimum required for full installation${NC}"
    add_check "Disk Space" "❌ FAIL" "Only ${free_space}GB free"
fi

# Check 5: Port Availability
echo -e "${YELLOW}[5/6] Checking required ports...${NC}"
ports=(80 5000 10035 11434)
ports_in_use=()

for port in "${ports[@]}"; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        ports_in_use+=($port)
    fi
done

if [[ ${#ports_in_use[@]} -eq 0 ]]; then
    echo -e "  ${GREEN}✅ All required ports are available${NC}"
    add_check "Port Availability" "✅ PASS" "Ports 80, 5000, 10035, 11434 are free"
else
    ports_list=$(IFS=, ; echo "${ports_in_use[*]}")
    echo -e "  ${YELLOW}⚠️  Some ports are in use: $ports_list${NC}"
    echo -e "     ${YELLOW}These ports may cause conflicts. You can change them in docker-compose.yml${NC}"
    add_check "Port Availability" "⚠️  WARN" "Ports in use: $ports_list"
fi

# Check 6: Project Files
echo -e "${YELLOW}[6/6] Checking project files...${NC}"
required_files=("docker-compose.yml" "backend/app.py" "frontend/package.json" "README.md")
missing_files=()

for file in "${required_files[@]}"; do
    if [[ ! -f "$file" ]]; then
        missing_files+=("$file")
    fi
done

if [[ ${#missing_files[@]} -eq 0 ]]; then
    echo -e "  ${GREEN}✅ All required project files are present${NC}"
    add_check "Project Files" "✅ PASS" "All files present"
else
    files_list=$(IFS=, ; echo "${missing_files[*]}")
    echo -e "  ${RED}❌ Missing files: $files_list${NC}"
    echo -e "     ${YELLOW}Make sure you're in the correct directory${NC}"
    add_check "Project Files" "❌ FAIL" "Missing: $files_list"
fi

# Summary
echo ""
echo -e "${CYAN}============================================${NC}"
echo -e "${CYAN}  Summary${NC}"
echo -e "${CYAN}============================================${NC}"
printf "%-25s %-15s %s\n" "Check" "Status" "Message"
echo "--------------------------------------------------------------------"
for check in "${checks[@]}"; do
    IFS='|' read -r name status message <<< "$check"
    printf "%-25s %-15s %s\n" "$name" "$status" "$message"
done

# Final Verdict
echo ""
if [[ $fail_count -eq 0 && $warn_count -eq 0 ]]; then
    echo -e "${GREEN}🎉 Your system is ready to run Thinx!${NC}"
    echo ""
    echo -e "${CYAN}Next steps:${NC}"
    echo "  1. Run: docker-compose --profile full up --build"
    echo "  2. Wait 3-7 minutes for first-time setup"
    echo "  3. Open browser to: http://localhost"
    echo ""
    echo -e "${YELLOW}For detailed instructions, see: QUICK_START.md${NC}"
elif [[ $fail_count -eq 0 ]]; then
    echo -e "${YELLOW}⚠️  Your system is mostly ready, but there are some warnings.${NC}"
    echo "   You can proceed, but address the warnings if you encounter issues."
else
    echo -e "${RED}❌ Your system has some issues that need to be addressed.${NC}"
    echo ""
    echo -e "${CYAN}Action items:${NC}"
    
    for check in "${checks[@]}"; do
        IFS='|' read -r name status message <<< "$check"
        if [[ $status == *"FAIL"* ]]; then
            case $name in
                "Docker Installed")
                    echo "  • Install Docker Desktop from: https://docker.com/get-started"
                    ;;
                "Docker Running")
                    echo "  • Start Docker Desktop application"
                    ;;
                "Disk Space")
                    echo "  • Free up disk space (10GB recommended)"
                    ;;
                "Project Files")
                    echo "  • Navigate to the Thinx project directory"
                    ;;
            esac
        fi
    done
    
    echo ""
    echo -e "${YELLOW}For help, see: FAQ.md or QUICK_START.md${NC}"
fi

echo ""
echo -e "${CYAN}============================================${NC}"
