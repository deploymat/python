#!/bin/bash

# Exit on error and print commands
set -eo pipefail

# Load common functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${SCRIPT_DIR}/utils/common.sh"

section "Restarting Services"

# Restart specific service if provided, otherwise restart all
if [ $# -eq 1 ]; then
    service=$1
    status "Restarting ${service} service..."
    if command -v docker-compose &> /dev/null; then
        docker-compose -f "${SCRIPT_DIR}/../docker-compose.yml" restart "${service}"
    else
        docker compose -f "${SCRIPT_DIR}/../docker-compose.yml" restart "${service}"
    fi
    success "Service ${service} restarted"
else
    ${SCRIPT_DIR}/services/stop.sh
    ${SCRIPT_DIR}/services/start.sh
fi
