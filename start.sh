#!/bin/bash

echo "========================================================"
echo " Thinx - Human Trafficking Research Platform"
echo " (Data Science in Practice - Leiden University)"
echo "========================================================"
echo ""
echo " Documentation:"
echo "  - Quick Start: QUICK_START.md"
echo "  - Main Docs: README.md"
echo "  - All Docs: docs/README.md"
echo "  - Mock Data: Mock data/ folder"
echo ""
echo "========================================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed."
    echo "Please install Docker and try again."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "ERROR: Docker Compose is not installed."
    echo "Please install Docker Compose and try again."
    exit 1
fi

echo "Docker is ready!"
echo ""
echo "Starting services (this may take a few minutes on first run)..."
echo ""

docker-compose up --build
