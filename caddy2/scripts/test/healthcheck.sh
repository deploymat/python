#!/bin/bash

# Exit on error and print commands
set -eo pipefail

# Load common functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${SCRIPT_DIR}/utils/common.sh"

section "Caddy Health Check"

# Load environment variables
load_env "${SCRIPT_DIR}/../.env"

# Check if Caddy container is running
status "Checking if Caddy is running..."
if ! docker ps --format '{{.Names}}' | grep -q '^caddy$'; then
    error "Caddy container is not running. Please start it with './scripts/services/start.sh'"
fi
success "Caddy is running"

# Check container health
status "Checking container health..."
CONTAINER_HEALTH=$(docker inspect --format='{{.State.Health.Status}}' caddy 2>/dev/null || echo "unknown")
if [ "$CONTAINER_HEALTH" = "healthy" ]; then
    success "Caddy container is healthy"
else
    error "Caddy container health status: ${CONTAINER_HEALTH}"
    docker logs caddy --tail 20
    exit 1
fi

# Test health check endpoint
status "Testing health check endpoint..."
HEALTH_CHECK_URL="https://${DOMAIN}/healthz"
if curl -s -k -f "${HEALTH_CHECK_URL}" | grep -q "OK"; then
    success "Health check endpoint is working"
else
    error "Health check endpoint failed"
    exit 1
fi

# Check certificate expiration
status "Checking certificate expiration..."
CERT_EXPIRY=$(echo | openssl s_client -servername ${DOMAIN} -connect localhost:${HTTPS_PORT} 2>/dev/null | \
    openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)

if [ -z "$CERT_EXPIRY" ]; then
    error "Could not retrieve certificate information"
    exit 1
fi

# Convert expiration date to timestamp
CERT_TIMESTAMP=$(date -d "$CERT_EXPIRY" +%s)
CURRENT_TIMESTAMP=$(date +%s)
DAYS_LEFT=$(( (CERT_TIMESTAMP - CURRENT_TIMESTAMP) / 86400 ))

if [ $DAYS_LEFT -le 7 ]; then
    error "Certificate expires in $DAYS_LEFT days (on $CERT_EXPIRY)"
    exit 1
else
    success "Certificate is valid for $DAYS_LEFT days (expires $CERT_EXPIRY)"
fi

# Check disk space
status "Checking disk space..."
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | tr -d '%')
if [ "$DISK_USAGE" -gt 90 ]; then
    error "Disk space is critically low: ${DISK_USAGE}% used"
    exit 1
else
    success "Disk space is OK: ${DISK_USAGE}% used"
fi

# Final status
success "\n✅ All health checks passed!"
