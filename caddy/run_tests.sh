#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Load environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Default values
DOMAIN=${DOMAIN:-localhost}
MAX_RETRIES=5
RETRY_DELAY=5

# Function to print section headers
print_section() {
    echo -e "\n${BLUE}==> $1${NC}"
}

# Function to print success message
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print warning message
print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Function to print error message
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Function to check if a container is running
container_is_running() {
    docker ps --filter "name=$1" --format '{{.Names}}' | grep -q "^$1$"
}

# Function to check container health
container_health() {
    local container=$1
    local health_status
    
    health_status=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null || echo "no healthcheck")
    echo "$health_status"
}

# Function to check if a URL returns HTTP 200
check_url() {
    local url=$1
    local validate_certs=$2
    local max_retries=${3:-$MAX_RETRIES}
    local retry_delay=${4:-$RETRY_DELAY}
    local status_code=0
    local response=""
    
    for i in $(seq 1 $max_retries); do
        echo -e "${BLUE}Checking $url (attempt $i/$max_retries)...${NC}"
        
        if [ "$validate_certs" = "yes" ]; then
            response=$(curl -k -s -w "\n%{http_code}" -o /dev/null "$url" 2>&1) || true
        else
            response=$(curl -k -s -w "\n%{http_code}" -o /dev/null "$url" 2>&1) || true
        fi
        
        # Extract status code (last line of output)
        status_code=$(echo "$response" | tail -n1)
        
        # Remove status code from response for cleaner output
        response=$(echo "$response" | sed '$d')
        
        if [[ "$status_code" =~ ^2[0-9]{2}$ ]]; then
            print_success "$url is accessible (HTTP $status_code)"
            if [ -n "$response" ]; then
                echo -e "Response: ${BLUE}$(echo "$response" | head -c 200)${NC}..."
            fi
            return 0
        elif [ -n "$status_code" ]; then
            print_warning "Unexpected status code: $status_code"
            if [ -n "$response" ]; then
                echo -e "Response: ${YELLOW}$(echo "$response" | head -c 200)${NC}..."
            fi
        else
            print_warning "Failed to connect to $url"
            if [ -n "$response" ]; then
                echo -e "Error: ${YELLOW}$(echo "$response" | head -c 200)${NC}..."
            fi
        fi
        
        if [ $i -lt $max_retries ]; then
            echo -e "${BLUE}⏳ Waiting $retry_delay seconds before retry...${NC}"
            sleep $retry_delay
        fi
    done
    
    print_error "Failed to access $url after $max_retries attempts"
    return 1
}

# Main execution
print_section "Starting Caddy and FastAPI Test Suite"
echo -e "Domain: ${BLUE}${DOMAIN}${NC}"

# Check if Docker is running
print_section "Checking Docker"
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
else
    print_success "Docker is running"
fi

# Check if containers are running
print_section "Checking Containers"
containers=("caddy" "myapi")
all_running=true
container_status=()

for container in "${containers[@]}"; do
    if container_is_running "$container"; then
        health=$(container_health "$container")
        status="running (health: $health)"
        print_success "Container $container is $status"
        container_status+=("$container: $status")
    else
        print_error "Container $container is not running"
        container_status+=("$container: not running")
        all_running=false
    fi
done

if [ "$all_running" = false ]; then
    print_error "Some containers are not running. Please start them with 'docker-compose up -d'"
    echo -e "\n${YELLOW}Container status:${NC}"
    for status in "${container_status[@]}"; do
        echo "  - $status"
    done
    exit 1
fi

# Test Caddy HTTPS endpoint
print_section "Testing Caddy HTTPS Endpoint"
check_url "https://$DOMAIN" "no"

# Test FastAPI endpoint through Caddy
print_section "Testing FastAPI Endpoint"
check_url "https://$DOMAIN/docs" "no"

# Test FastAPI health check endpoint
print_section "Testing FastAPI Health Check"
check_url "https://$DOMAIN/health" "no" 3 2

# Display container logs if any test failed
if [ $? -ne 0 ]; then
    print_section "Container Logs"
    for container in "${containers[@]}"; do
        echo -e "\n${YELLOW}=== $container logs ===${NC}"
        docker logs --tail 20 "$container" 2>&1 | sed 's/^/  /'
    done
    
    print_error "\n❌ Some tests failed. See logs above for details."
    exit 1
else
    print_success "\n✅ All tests completed successfully!"
    echo -e "\n${GREEN}Application is running at: https://${DOMAIN}${NC}"
    echo -e "${GREEN}API Documentation: https://${DOMAIN}/docs${NC}"
    exit 0
fi
