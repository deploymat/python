#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_section() {
    echo -e "\n${BLUE}==> $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for required commands
print_section "Checking system requirements"
for cmd in python3 pip3 ansible-playbook; do
    if ! command_exists "$cmd"; then
        print_error "Required command not found: $cmd"
        exit 1
    fi
    print_success "Found: $cmd"
done

# Create a Python virtual environment if it doesn't exist
VENV_DIR="${PWD}/.venv"
if [ ! -d "$VENV_DIR" ]; then
    print_section "Creating Python virtual environment"
    python3 -m venv "$VENV_DIR"
    source "${VENV_DIR}/bin/activate"
    
    # Upgrade pip and install required packages
    pip install --upgrade pip
    pip install ansible docker requests
    
    deactivate
fi

# Activate the virtual environment
source "${VENV_DIR}/bin/activate"

# Install required Ansible collections
print_section "Installing Ansible collections"
if [ ! -f "ansible-requirements.yml" ]; then
    print_error "ansible-requirements.yml not found"
    exit 1
fi

ansible-galaxy collection install -r ansible-requirements.yml

# Run the tests
print_section "Running Ansible tests"
if [ ! -f "ansible_tests.yml" ]; then
    print_error "ansible_tests.yml not found"
    exit 1
fi

# Set environment variables
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Export Python path for Ansible
export ANSIBLE_PYTHON_INTERPRETER="${VENV_DIR}/bin/python"

# Run the playbook with verbose output
set +e
ansible-playbook ansible_tests.yml -i localhost, -c local -v
PLAYBOOK_EXIT_CODE=$?
set -e

# Check the result
if [ $PLAYBOOK_EXIT_CODE -eq 0 ]; then
    print_success "✅ All tests passed!"
    exit 0
else
    print_error "❌ Some tests failed. Check the output above for details."
    
    # Show container status
    print_section "Container Status"
    docker ps -a --filter "name=caddy|myapi" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    
    # Show container logs
    for container in caddy myapi; do
        if docker ps -a --format '{{.Names}}' | grep -q "^${container}$"; then
            print_section "${container} logs (last 10 lines)"
            docker logs --tail 10 "$container" 2>&1 | sed 's/^/  /' || true
        fi
    done
    
    exit 1
fi
