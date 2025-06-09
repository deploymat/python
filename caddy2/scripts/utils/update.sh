#!/bin/bash

# Exit on error and print commands
set -eo pipefail

# Load common functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${SCRIPT_DIR}/utils/common.sh"

section "Update Caddy and Services"

# Load environment variables
load_env "${SCRIPT_DIR}/../.env"

# Backup current configuration
status "Creating backup of current configuration..."
${SCRIPT_DIR}/utils/backup.sh

# Pull latest images
status "Pulling latest Docker images..."
if command -v docker-compose &> /dev/null; then
    docker-compose -f "${SCRIPT_DIR}/../docker-compose.yml" pull
else
    docker compose -f "${SCRIPT_DIR}/../docker-compose.yml" pull
fi

# Restart services with new images
status "Restarting services with new images..."
${SCRIPT_DIR}/services/restart.sh

# Check service health
status "Checking service health..."
${SCRIPT_DIR}/test/healthcheck.sh

success "\n✅ Update completed successfully!"
