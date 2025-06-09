#!/bin/bash

# Exit on error and print commands
set -eo pipefail

# Load common functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${SCRIPT_DIR}/utils/common.sh"

section "Stopping Services"

# Stop services
status "Stopping Caddy and services..."
if command -v docker-compose &> /dev/null; then
    docker-compose -f "${SCRIPT_DIR}/../docker-compose.yml" down
else
    docker compose -f "${SCRIPT_DIR}/../docker-compose.yml" down
fi

success "All services have been stopped"
