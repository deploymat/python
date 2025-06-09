#!/bin/bash

# Exit on error and print commands
set -eo pipefail

# Load common functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${SCRIPT_DIR}/utils/common.sh"

section "SSL Certificate Renewal"

# Load environment variables
load_env "${SCRIPT_DIR}/../.env"

# Check if mkcert is installed
if ! command -v mkcert &> /dev/null; then
    error "mkcert is required but not installed. Please install it first."
fi

# Regenerate certificates
${SCRIPT_DIR}/certs/generate.sh

# Restart Caddy to pick up new certificates
${SCRIPT_DIR}/services/restart.sh caddy

success "SSL certificates renewed successfully"
