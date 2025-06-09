#!/bin/bash

# Exit on error and print commands
set -eo pipefail

# Load common functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${SCRIPT_DIR}/utils/common.sh"

section "SSL Certificate Generation"

# Load environment variables
load_env "${SCRIPT_DIR}/../.env"

# Create certs directory
CERT_DIR="${SCRIPT_DIR}/../certs"
mkdir -p "${CERT_DIR}"

# Install local CA if not already installed
if [ ! -f "$HOME/.local/share/mkcert/rootCA.pem" ]; then
    status "Installing local CA..."
    mkcert -install
    success "Local CA installed successfully"
fi

# Generate SSL certificates
status "Generating SSL certificates..."

# Base domains for certificates
BASE_DOMAINS=(
    "localhost"
    "127.0.0.1"
    "::1"
    "${DOMAIN}"
    "*.${DOMAIN}"
    "lvh.me"
    "*.lvh.me"
    "*.test"
    "*.local"
)

# Add extra domains if defined
if [ -n "${EXTRA_DOMAINS}" ]; then
    IFS=',' read -ra EXTRA_DOMAIN_ARRAY <<< "${EXTRA_DOMAINS}"
    for domain in "${EXTRA_DOMAIN_ARRAY[@]}"; do
        BASE_DOMAINS+=("${domain}")
    done
fi

# Generate wildcard certificate for development domains
mkcert -cert-file "${CERT_DIR}/wildcard.crt" -key-file "${CERT_DIR}/wildcard.key" "${BASE_DOMAINS[@]}"

# Create combined certificate for Caddy
cat "${CERT_DIR}/wildcard.crt" "$(mkcert -CAROOT)/rootCA.pem" > "${CERT_DIR}/wildcard-fullchain.crt"

# Set proper permissions
chmod 600 "${CERT_DIR}"/*.key
chmod 644 "${CERT_DIR}"/*.crt

success "SSL certificates generated in ${CERT_DIR}"
