#!/bin/bash

# Exit on error and print commands
set -eo pipefail

# Load common functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${SCRIPT_DIR}/utils/common.sh"

# Default to showing all services if none specified
SERVICE="${1:---all}"

# Special case for Caddy access logs
if [ "$1" = "access" ]; then
    docker exec -it caddy tail -f /var/log/caddy/access.log
    exit 0
fi

# Special case for Caddy error logs
if [ "$1" = "error" ]; then
    docker exec -it caddy tail -f /var/log/caddy/error.log
    exit 0
fi

section "Viewing Logs"

# Show logs
status "Tailing logs for ${SERVICE} (Ctrl+C to exit)..."
if command -v docker-compose &> /dev/null; then
    docker-compose -f "${SCRIPT_DIR}/../docker-compose.yml" logs -f --tail=100 "${SERVICE}"
else
    docker compose -f "${SCRIPT_DIR}/../docker-compose.yml" logs -f --tail=100 "${SERVICE}"
fi
