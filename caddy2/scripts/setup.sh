#!/bin/bash

# Exit on error and print commands
set -eo pipefail

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Load environment variables
ENV_FILE="$(dirname "$0")/../.env"
ENV_EXAMPLE_FILE="$(dirname "$0")/../.env.example"

# Function to print section header
section() {
    echo -e "\n${GREEN}==> ${1}${NC}"
}

# Function to print status
status() {
    echo -e "${YELLOW}➜${NC} ${1}"
}

# Function to print success
success() {
    echo -e "${GREEN}✓${NC} ${1}"
}

# Function to print error and exit
error() {
    echo -e "${RED}✗ Error: ${1}${NC}" >&2
    exit 1
}

# Check if running as root
if [ "$(id -u)" -eq 0 ]; then
    error "This script should not be run as root. Please run as a regular user with sudo privileges."
fi

section "Environment Setup"

# Create .env from example if it doesn't exist
if [ ! -f "$ENV_FILE" ]; then
    if [ ! -f "$ENV_EXAMPLE_FILE" ]; then
        error "Neither .env nor .env.example file found in $(dirname "$ENV_FILE")"
    fi
    
    status "Creating .env file from example..."
    cp "$ENV_EXAMPLE_FILE" "$ENV_FILE"
    
    # Generate random passwords if needed
    if grep -q "GENERATE_RANDOM_PASSWORD" "$ENV_FILE"; then
        status "Generating random passwords..."
        sed -i.bak "s/GENERATE_RANDOM_PASSWORD/$(openssl rand -base64 24)/g" "$ENV_FILE"
        rm -f "${ENV_FILE}.bak"
    fi
    
    echo -e "\n${YELLOW}⚠️  Please edit the .env file with your configuration.${NC}"
    echo -e "   File location: ${YELLOW}${ENV_FILE}${NC}"
    exit 1
fi

# Load environment variables
status "Loading environment variables..."
set -a
# shellcheck source=/dev/null
source "$ENV_FILE"
set +a

# Set default values for required variables
export DOMAIN=${DOMAIN:-lvh.me}
export STAGING=${STAGING:-false}
export DISABLE_HTTPS=${DISABLE_HTTPS:-false}
export DEV_MODE=${DEV_MODE:-false}

# Set network name
export NETWORK_NAME=${NETWORK_NAME:-caddy_network}

# Set default ports
export HTTP_PORT=${HTTP_PORT:-80}
export HTTPS_PORT=${HTTPS_PORT:-443}

# Service ports
export API_PORT=${API_PORT:-8080}
export WEB_PORT=${WEB_PORT:-8081}
export AUTH_PORT=${AUTH_PORT:-8082}

section "Prerequisites Check"

# Check for required commands
check_command() {
    if ! command -v "$1" &> /dev/null; then
        return 1
    fi
    return 0
}

# List of required commands and installation instructions
declare -A REQUIRED_COMMANDS=(
    [docker]="Install Docker from https://docs.docker.com/get-docker/"
    [docker-compose]="Install Docker Compose from https://docs.docker.com/compose/install/"
    [mkcert]="Install mkcert: brew install mkcert (macOS) | sudo apt install mkcert (Ubuntu) | choco install mkcert (Windows)"
)

# Check each command
MISSING_DEPS=0
for cmd in "${!REQUIRED_COMMANDS[@]}"; do
    if ! check_command "$cmd"; then
        error "$cmd is required but not installed.\n   ${REQUIRED_COMMANDS[$cmd]}"
        MISSING_DEPS=1
    fi
done

if [ "$MISSING_DEPS" -ne 0 ]; then
    exit 1
fi

# Check Docker daemon
if ! docker info &> /dev/null; then
    error "Docker daemon is not running. Please start Docker and try again."
fi

success "All prerequisites are installed"

section "SSL Certificate Setup"

# Create certs directory
CERT_DIR="$(dirname "$0")/../certs"
mkdir -p "$CERT_DIR"

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
    "$DOMAIN"
    "*.$DOMAIN"
    "lvh.me"
    "*.lvh.me"
    "*.test"
    "*.local"
)

# Add extra domains if defined
if [ -n "$EXTRA_DOMAINS" ]; then
    IFS=',' read -ra EXTRA_DOMAIN_ARRAY <<< "$EXTRA_DOMAINS"
    for domain in "${EXTRA_DOMAIN_ARRAY[@]}"; do
        BASE_DOMAINS+=("$domain")
    done
fi

# Generate wildcard certificate for development domains
mkcert -cert-file "$CERT_DIR/wildcard.crt" -key-file "$CERT_DIR/wildcard.key" "${BASE_DOMAINS[@]}"

# Create combined certificate for Caddy
cat "$CERT_DIR/wildcard.crt" "$(mkcert -CAROOT)/rootCA.pem" > "$CERT_DIR/wildcard-fullchain.crt"

# Set proper permissions
chmod 600 "$CERT_DIR"/*.key
chmod 644 "$CERT_DIR"/*.crt

success "SSL certificates generated in $CERT_DIR"

section "System Configuration"

# Update /etc/hosts if needed
HOSTS_ENTRY="127.0.01  $DOMAIN $API_SUBDOMAIN.$DOMAIN $WEB_SUBDOMAIN.$DOMAIN $AUTH_SUBDOMAIN.$DOMAIN"
if ! grep -q "$DOMAIN" /etc/hosts; then
    status "Adding entries to /etc/hosts..."
    echo $HOSTS_ENTRY | sudo tee -a /etc/hosts > /dev/null
    success "Added $DOMAIN and subdomains to /etc/hosts"
fi

# Create docker network if not exists
if ! docker network inspect "$NETWORK_NAME" &> /dev/null; then
    status "Creating Docker network '$NETWORK_NAME'..."
    docker network create "$NETWORK_NAME"
    success "Docker network '$NETWORK_NAME' created"
else
    status "Using existing Docker network '$NETWORK_NAME'"
fi

section "Starting Services"

# Build and start services
status "Starting Caddy and services..."
if command -v docker-compose &> /dev/null; then
    docker-compose -f "$(dirname "$0")/../docker-compose.yml" up -d --build
else
    docker compose -f "$(dirname "$0")/../docker-compose.yml" up -d --build
fi

# Wait for services to start
status "Waiting for services to be ready..."
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
    echo -e "${YELLOW}⚠️  Services are taking longer than expected to start. Please check logs with 'make logs'.${NC}"
else
    success "All services are up and running"
fi

# Print summary
section "Setup Complete!"
echo -e "${GREEN}✅ Your Caddy reverse proxy is now running!${NC}\n"

echo "You can access the following services:"
echo "- Web UI:   https://${WEB_SUBDOMAIN:-app}.${DOMAIN}"
echo "- API:      https://${API_SUBDOMAIN:-api}.${DOMAIN}"
echo "- Auth:     https://${AUTH_SUBDOMAIN:-auth}.${DOMAIN}\n"

echo "Useful commands:"
echo "- View logs:        ${YELLOW}make logs${NC}"
echo "- Access container: ${YELLOW}make shell${NC}"
echo "- Stop services:    ${YELLOW}make down${NC}"
echo "- Restart services: ${YELLOW}make restart${NC}\n"

echo "For more information, refer to the README.md file."
echo -e "${GREEN}Happy coding! 🚀${NC}\n"
