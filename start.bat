@echo off
echo ========================================================
echo  Thinx - Human Trafficking Research Platform
echo  (Data Science in Practice - Leiden University)
echo ========================================================
echo.
echo  Documentation:
echo   - Quick Start: QUICK_START.md
echo   - Main Docs: README.md
echo   - All Docs: docs/README.md
echo   - Mock Data: Mock data/ folder
echo.
echo ========================================================
echo.

echo Checking Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not installed or not running.
    echo Please install Docker Desktop and try again.
    pause
    exit /b 1
)

echo Docker is ready!
echo.
echo Starting services (this may take a few minutes on first run)...
echo.

docker-compose up --build

pause
