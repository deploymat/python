#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print section header
section() {
    echo -e "\n${BLUE}==> ${1}${NC}"
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

# Function to check if running as root
check_root() {
    if [ "$(id -u)" -eq 0 ]; then
        error "This script should not be run as root. Please run as a regular user with sudo privileges."
    fi
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check for required commands
check_commands() {
    for cmd in "$@"; do
        if ! command_exists "$cmd"; then
            error "Required command not found: ${cmd}"
        fi
    done
}

# Function to load environment variables
load_env() {
    local env_file="${1:-.env}"
    if [ -f "$env_file" ]; then
        # shellcheck source=/dev/null
        set -o allexport
        source "$env_file"
        set +o allexport
    else
        error "Environment file not found: $env_file"
    fi
}

# Function to install local CA
install_local_ca() {
    if [ ! -f "$HOME/.local/share/mkcert/rootCA.pem" ]; then
        status "Installing local CA..."
        if ! mkcert -install; then
            error "Failed to install local CA"
        fi
        success "Local CA installed successfully"
    fi
}

# Function to create necessary directories
create_directories() {
    local dirs=(
        "${SCRIPT_DIR}/../certs"
        "${SCRIPT_DIR}/../config"
        "${SCRIPT_DIR}/../data"
    )
    
    for dir in "${dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            chmod 755 "$dir"
        fi
    done
}

# Function to wait for a service to be healthy
wait_for_service() {
    local service="$1"
    local max_retries=30
    local retry_interval=5
    local retries=0
    
    status "Waiting for ${service} to be healthy..."
    
    while [ $retries -lt $max_retries ]; do
        if docker ps --filter "name=${service}" --format '{{.Status}}' | grep -q "healthy"; then
            success "${service} is healthy"
            return 0
        fi
        retries=$((retries + 1))
        sleep $retry_interval
        echo -n "."
    done
    
    error "Timed out waiting for ${service} to be healthy"
    return 1
}

# Function to check if a port is in use
port_in_use() {
    local port="$1"
    if command -v lsof >/dev/null; then
        lsof -i ":${port}" -sTCP:LISTEN -t >/dev/null
    else
        netstat -tuln | grep -q ":${port} "
    fi
    return $?
}

# Function to get a random available port
get_random_port() {
    local min=49152
    local max=65535
    local port
    
    while true; do
        port=$(shuf -i ${min}-${max} -n 1)
        if ! port_in_use "$port"; then
            echo "$port"
            return 0
        fi
    done
}
