#!/bin/bash

# Exit on error and print commands
set -eo pipefail

# Load common functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${SCRIPT_DIR}/utils/common.sh"

section "Starting Services"

# Load environment variables
load_env "${SCRIPT_DIR}/../.env"

# Check if Docker is running
if ! docker info &> /dev/null; then
    error "Docker daemon is not running. Please start Docker and try again."
fi

# Start services
status "Starting Caddy and services..."
if command -v docker-compose &> /dev/null; then
    docker-compose -f "${SCRIPT_DIR}/../docker-compose.yml" up -d --build
else
    docker compose -f "${SCRIPT_DIR}/../docker-compose.yml" up -d --build
fi

# Wait for services to be healthy
MAX_RETRIES=30
RETRY_INTERVAL=5
retries=0

while [ $retries -lt $MAX_RETRIES ]; do
    if docker ps --filter "name=caddy" --format '{{.Status}}' | grep -q "healthy"; then
        break
    fi
    retries=$((retries + 1))
    sleep $RETRY_INTERVAL
    echo -n "."
done
echo ""

if [ $retries -eq $MAX_RETRIES ]; then
    echo -e "${YELLOW}⚠️  Services are taking longer than expected to start. Please check logs with '${SCRIPT_DIR}/services/logs.sh'.${NC}"
else
    success "All services are up and running"
fi
