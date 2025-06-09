#!/bin/bash

# Exit on error and print commands
set -eo pipefail

# Load common functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${SCRIPT_DIR}/utils/common.sh"

section "Caddy Reverse Proxy Setup"

# Check if running as root
check_root

# Check for required commands
check_commands docker docker-compose mkcert

# Load environment variables
load_env "${SCRIPT_DIR}/../.env"

# Create necessary directories
create_directories

# Install local CA if needed
install_local_ca

# Generate SSL certificates
${SCRIPT_DIR}/certs/generate.sh

# Configure system settings
${SCRIPT_DIR}/setup/02-configure.sh

# Start services
${SCRIPT_DIR}/services/start.sh

# Print success message
success "\n✅ Caddy reverse proxy setup completed successfully!"
echo -e "\nYou can now access the following services:"
echo -e "- Web UI:   https://${WEB_SUBDOMAIN:-app}.${DOMAIN}"
echo -e "- API:      https://${API_SUBDOMAIN:-api}.${DOMAIN}"
echo -e "- Auth:     https://${AUTH_SUBDOMAIN:-auth}.${DOMAIN}\n"
