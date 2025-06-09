#!/bin/bash

# Exit on error and print commands
set -eo pipefail

# Load common functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${SCRIPT_DIR}/utils/common.sh"

section "Backup Caddy Configuration"

# Load environment variables
load_env "${SCRIPT_DIR}/../.env"

# Set backup directory
BACKUP_DIR="${SCRIPT_DIR}/../backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/caddy_backup_${TIMESTAMP}.tar.gz"

# Create backup directory if it doesn't exist
mkdir -p "${BACKUP_DIR}"

# Files and directories to backup
BACKUP_PATHS=(
    "${SCRIPT_DIR}/../Caddyfile"
    "${SCRIPT_DIR}/../docker-compose.yml"
    "${SCRIPT_DIR}/../.env"
    "${SCRIPT_DIR}/../certs"
    "${SCRIPT_DIR}/../config"
    "${SCRIPT_DIR}/../data"
)

# Create backup
status "Creating backup..."
tar -czf "${BACKUP_FILE}" "${BACKUP_PATHS[@]}" 2>/dev/null || {
    error "Failed to create backup"
}

# Verify backup was created
if [ -f "${BACKUP_FILE}" ]; then
    BACKUP_SIZE=$(du -h "${BACKUP_FILE}" | cut -f1)
    success "Backup created successfully: ${BACKUP_FILE} (${BACKUP_SIZE})"
    
    # Keep only the last 5 backups
    status "Cleaning up old backups..."
    (cd "${BACKUP_DIR}" && ls -tp | grep -v '/$' | tail -n +6 | xargs -I {} rm -- {})
    success "Kept the 5 most recent backups"
    
    # List all backups
    echo -e "\n${BLUE}=== Available Backups ===${NC}"
    ls -lth "${BACKUP_DIR}" | grep -v 'total'
else
    error "Backup file was not created"
fi
