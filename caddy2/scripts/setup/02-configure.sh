#!/bin/bash

# Exit on error and print commands
set -eo pipefail

# Load common functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${SCRIPT_DIR}/utils/common.sh"

section "System Configuration"

# Load environment variables
load_env "${SCRIPT_DIR}/../.env"

# Update /etc/hosts if needed
HOSTS_ENTRY="127.0.0.1 ${DOMAIN} ${API_SUBDOMAIN}.${DOMAIN} ${WEB_SUBDOMAIN}.${DOMAIN} ${AUTH_SUBDOMAIN}.${DOMAIN}"
if ! grep -q "${DOMAIN}" /etc/hosts; then
    status "Adding entries to /etc/hosts..."
    echo "${HOSTS_ENTRY}" | sudo tee -a /etc/hosts > /dev/null
    success "Added ${DOMAIN} and subdomains to /etc/hosts"
fi

# Create docker network if not exists
if ! docker network inspect "${NETWORK_NAME:-caddy_network}" &> /dev/null; then
    status "Creating Docker network '${NETWORK_NAME:-caddy_network}'..."
    docker network create "${NETWORK_NAME:-caddy_network}"
    success "Docker network '${NETWORK_NAME:-caddy_network}' created"
else
    status "Using existing Docker network '${NETWORK_NAME:-caddy_network}'"
fi

# Set proper permissions for certs directory
if [ -d "${SCRIPT_DIR}/../certs" ]; then
    status "Setting proper permissions for certificates..."
    chmod 600 "${SCRIPT_DIR}"/../certs/*.key
    chmod 644 "${SCRIPT_DIR}"/../certs/*.crt
    success "Certificate permissions updated"
fi

success "System configuration completed"
