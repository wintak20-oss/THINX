# Thinx Setup Validation Script
# This script checks if your system is ready to run Thinx

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Thinx - System Prerequisites Checker" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

$allChecks = @()

# Function to add check result
function Add-Check {
    param($Name, $Status, $Message)
    $allChecks += [PSCustomObject]@{
        Check = $Name
        Status = $Status
        Message = $Message
    }
}

# Check 1: Docker Installation
Write-Host "[1/6] Checking Docker installation..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>$null
    if ($dockerVersion) {
        Write-Host "  ✅ Docker is installed: $dockerVersion" -ForegroundColor Green
        Add-Check "Docker Installed" "✅ PASS" $dockerVersion
    } else {
        Write-Host "  ❌ Docker is not installed" -ForegroundColor Red
        Write-Host "     Download from: https://docker.com/get-started" -ForegroundColor Yellow
        Add-Check "Docker Installed" "❌ FAIL" "Not installed"
    }
} catch {
    Write-Host "  ❌ Docker is not installed" -ForegroundColor Red
    Add-Check "Docker Installed" "❌ FAIL" "Not found"
}

# Check 2: Docker Running
Write-Host "[2/6] Checking if Docker is running..." -ForegroundColor Yellow
try {
    $dockerInfo = docker info 2>$null
    if ($dockerInfo) {
        Write-Host "  ✅ Docker is running" -ForegroundColor Green
        Add-Check "Docker Running" "✅ PASS" "Docker daemon is active"
    } else {
        Write-Host "  ❌ Docker is not running" -ForegroundColor Red
        Write-Host "     Please start Docker Desktop" -ForegroundColor Yellow
        Add-Check "Docker Running" "❌ FAIL" "Docker daemon not responding"
    }
} catch {
    Write-Host "  ❌ Docker is not running" -ForegroundColor Red
    Add-Check "Docker Running" "❌ FAIL" "Cannot connect to daemon"
}

# Check 3: Docker Compose
Write-Host "[3/6] Checking Docker Compose..." -ForegroundColor Yellow
try {
    $composeVersion = docker-compose --version 2>$null
    if ($composeVersion) {
        Write-Host "  ✅ Docker Compose is available: $composeVersion" -ForegroundColor Green
        Add-Check "Docker Compose" "✅ PASS" $composeVersion
    } else {
        Write-Host "  ❌ Docker Compose is not available" -ForegroundColor Red
        Add-Check "Docker Compose" "❌ FAIL" "Not installed"
    }
} catch {
    Write-Host "  ❌ Docker Compose is not available" -ForegroundColor Red
    Add-Check "Docker Compose" "❌ FAIL" "Not found"
}

# Check 4: Disk Space
Write-Host "[4/6] Checking available disk space..." -ForegroundColor Yellow
try {
    $drive = Get-PSDrive -Name C
    $freeSpaceGB = [math]::Round($drive.Free / 1GB, 2)
    if ($freeSpaceGB -ge 10) {
        Write-Host "  ✅ Sufficient disk space: $freeSpaceGB GB available" -ForegroundColor Green
        Add-Check "Disk Space" "✅ PASS" "$freeSpaceGB GB free"
    } elseif ($freeSpaceGB -ge 5) {
        Write-Host "  ⚠️  Low disk space: $freeSpaceGB GB available (10GB recommended)" -ForegroundColor Yellow
        Add-Check "Disk Space" "⚠️  WARN" "$freeSpaceGB GB free (low)"
    } else {
        Write-Host "  ❌ Insufficient disk space: Only $freeSpaceGB GB available" -ForegroundColor Red
        Write-Host "     10GB minimum required for full installation" -ForegroundColor Yellow
        Add-Check "Disk Space" "❌ FAIL" "Only $freeSpaceGB GB free"
    }
} catch {
    Write-Host "  ⚠️  Could not check disk space" -ForegroundColor Yellow
    Add-Check "Disk Space" "⚠️  WARN" "Unable to check"
}

# Check 5: Port Availability
Write-Host "[5/6] Checking required ports..." -ForegroundColor Yellow
$portsToCheck = @(80, 5000, 10035, 11434)
$portsInUse = @()

foreach ($port in $portsToCheck) {
    $connection = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($connection) {
        $portsInUse += $port
    }
}

if ($portsInUse.Count -eq 0) {
    Write-Host "  ✅ All required ports are available" -ForegroundColor Green
    Add-Check "Port Availability" "✅ PASS" "Ports 80, 5000, 10035, 11434 are free"
} else {
    $portsList = $portsInUse -join ", "
    Write-Host "  ⚠️  Some ports are in use: $portsList" -ForegroundColor Yellow
    Write-Host "     These ports may cause conflicts. You can change them in docker-compose.yml" -ForegroundColor Yellow
    Add-Check "Port Availability" "⚠️  WARN" "Ports in use: $portsList"
}

# Check 6: Project Files
Write-Host "[6/6] Checking project files..." -ForegroundColor Yellow
$requiredFiles = @("docker-compose.yml", "backend/app.py", "frontend/package.json", "README.md")
$missingFiles = @()

foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        $missingFiles += $file
    }
}

if ($missingFiles.Count -eq 0) {
    Write-Host "  ✅ All required project files are present" -ForegroundColor Green
    Add-Check "Project Files" "✅ PASS" "All files present"
} else {
    $filesList = $missingFiles -join ", "
    Write-Host "  ❌ Missing files: $filesList" -ForegroundColor Red
    Write-Host "     Make sure you're in the correct directory" -ForegroundColor Yellow
    Add-Check "Project Files" "❌ FAIL" "Missing: $filesList"
}

# Summary
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Summary" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
$allChecks | Format-Table -AutoSize

# Final Verdict
$failCount = ($allChecks | Where-Object { $_.Status -like "*FAIL*" }).Count
$warnCount = ($allChecks | Where-Object { $_.Status -like "*WARN*" }).Count

Write-Host ""
if ($failCount -eq 0 -and $warnCount -eq 0) {
    Write-Host "🎉 Your system is ready to run Thinx!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Run: docker-compose --profile full up --build" -ForegroundColor White
    Write-Host "  2. Wait 3-7 minutes for first-time setup" -ForegroundColor White
    Write-Host "  3. Open browser to: http://localhost" -ForegroundColor White
    Write-Host ""
    Write-Host "For detailed instructions, see: QUICK_START.md" -ForegroundColor Yellow
} elseif ($failCount -eq 0) {
    Write-Host "⚠️  Your system is mostly ready, but there are some warnings." -ForegroundColor Yellow
    Write-Host "   You can proceed, but address the warnings if you encounter issues." -ForegroundColor Yellow
} else {
    Write-Host "❌ Your system has some issues that need to be addressed." -ForegroundColor Red
    Write-Host ""
    Write-Host "Action items:" -ForegroundColor Cyan
    
    if (($allChecks | Where-Object { $_.Check -eq "Docker Installed" -and $_.Status -like "*FAIL*" })) {
        Write-Host "  • Install Docker Desktop from: https://docker.com/get-started" -ForegroundColor White
    }
    
    if (($allChecks | Where-Object { $_.Check -eq "Docker Running" -and $_.Status -like "*FAIL*" })) {
        Write-Host "  • Start Docker Desktop application" -ForegroundColor White
    }
    
    if (($allChecks | Where-Object { $_.Check -eq "Disk Space" -and $_.Status -like "*FAIL*" })) {
        Write-Host "  • Free up disk space (10GB recommended)" -ForegroundColor White
    }
    
    if (($allChecks | Where-Object { $_.Check -eq "Project Files" -and $_.Status -like "*FAIL*" })) {
        Write-Host "  • Navigate to the Thinx project directory" -ForegroundColor White
    }
    
    Write-Host ""
    Write-Host "For help, see: FAQ.md or QUICK_START.md" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
