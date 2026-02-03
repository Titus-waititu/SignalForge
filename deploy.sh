#!/bin/bash
# SignalForge Docker Deployment Script

set -e

echo "🔥 SignalForge Docker Deployment"
echo "================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed${NC}"
    exit 1
fi

# Create required directories
echo -e "${YELLOW}Creating required directories...${NC}"
mkdir -p data logs

# Check for .env file
if [ ! -f .env ]; then
    echo -e "${YELLOW}No .env file found. Creating from .env.docker template...${NC}"
    cp .env.docker .env
    echo -e "${GREEN}✓ Created .env file${NC}"
    echo -e "${YELLOW}Please edit .env file with your configuration before proceeding${NC}"
    read -p "Press Enter to continue after configuring .env..."
fi

# Build the Docker image
echo -e "${YELLOW}Building Docker image...${NC}"
docker-compose build

# Start the services
echo -e "${YELLOW}Starting SignalForge...${NC}"
docker-compose up -d

# Wait for health check
echo -e "${YELLOW}Waiting for application to be healthy...${NC}"
sleep 5

# Check if container is running
if docker ps | grep -q signalforge-app; then
    echo -e "${GREEN}✓ SignalForge is running!${NC}"
    echo ""
    echo "🌐 Dashboard: http://localhost:8000"
    echo "📡 API Docs: http://localhost:8000/docs"
    echo "💚 Health: http://localhost:8000/health"
    echo ""
    echo "📋 View logs: docker-compose logs -f"
    echo "⏹️  Stop: docker-compose stop"
    echo "🗑️  Remove: docker-compose down"
else
    echo -e "${RED}✗ Failed to start SignalForge${NC}"
    echo "Check logs with: docker-compose logs"
    exit 1
fi
