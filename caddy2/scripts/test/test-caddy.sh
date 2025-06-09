#!/bin/bash

# Exit on error and print commands
set -eo pipefail

# Load common functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${SCRIPT_DIR}/utils/common.sh"

section "Testing Caddy Setup"

# Load environment variables
load_env "${SCRIPT_DIR}/../.env"

# Check if Caddy is running
if ! docker ps --format '{{.Names}}' | grep -q '^caddy$'; then
    error "Caddy container is not running. Please start it with './scripts/services/start.sh'"
fi

# Test endpoints
status "Testing HTTP/HTTPS endpoints..."

# Define test domains and expected status codes
declare -A TEST_ENDPOINTS=(
    ["http://${DOMAIN}"]=301
    ["https://${DOMAIN}"]=404
    ["https://${API_SUBDOMAIN}.${DOMAIN}"]=200
    ["https://${WEB_SUBDOMAIN}.${DOMAIN}"]=200
    ["https://${AUTH_SUBDOMAIN}.${DOMAIN}"]=200
)

# Add extra domains if defined
if [ -n "${EXTRA_DOMAINS}" ]; then
    IFS=',' read -ra EXTRA_DOMAIN_ARRAY <<< "${EXTRA_DOMAINS}"
    for domain in "${EXTRA_DOMAIN_ARRAY[@]}"; do
        # Remove wildcard if present
        clean_domain=${domain#\*\\.}
        TEST_ENDPOINTS["https://${clean_domain}"]=200
    done
fi

# Test each endpoint
FAILED_TESTS=0
for url in "${!TEST_ENDPOINTS[@]}"; do
    expected_status=${TEST_ENDPOINTS[$url]}
    echo -n "Testing ${url} (expecting ${expected_status})... "
    
    # Get HTTP status code
    status_code=$(curl -s -k -o /dev/null -w "%{http_code}" -I "${url}" 2>/dev/null || echo "000")
    
    # Check if status code matches expected
    if [[ "${status_code:0:1}" == "${expected_status:0:1}" ]]; then
        echo "✅ OK (${status_code})"
    else
        echo "❌ Failed (got ${status_code})"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
done

# Test certificate information
status "\n🔍 Checking certificate information..."
CERT_INFO=$(echo | openssl s_client -showcerts -connect localhost:${HTTPS_PORT} 2>/dev/null | \
    openssl x509 -noout -issuer -dates -subject 2>/dev/null || echo "Error: Could not retrieve certificate information")

echo "${CERT_INFO}"

# Test health check endpoint
status "\nTesting health check endpoint..."
HEALTH_CHECK_URL="https://${DOMAIN}/healthz"
if curl -s -k -f "${HEALTH_CHECK_URL}" | grep -q "OK"; then
    echo "✅ Health check OK"
else
    echo "❌ Health check failed"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

# Print summary
if [ ${FAILED_TESTS} -eq 0 ]; then
    success "\n✅ All tests passed!"
    exit 0
else
    error "\n❌ ${FAILED_TESTS} test(s) failed!"
fi
