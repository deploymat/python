#!/bin/bash
set -e

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Install test dependencies if not in Docker
if [ ! -f /.dockerenv ]; then
    echo "Not running in Docker, starting test container..."
    docker build -t caddy-tests -f Dockerfile.test .
    docker run --rm \
        --network=host \
        -v /var/run/docker.sock:/var/run/docker.sock \
        -v "$(pwd)":/tests \
        -w /tests \
        -e DOMAIN=${DOMAIN:-localhost} \
        -e API_SUBDOMAIN=${API_SUBDOMAIN:-api} \
        -e WEB_SUBDOMAIN=${WEB_SUBDOMAIN:-app} \
        -e AUTH_SUBDOMAIN=${AUTH_SUBDOMAIN:-auth} \
        caddy-tests
    exit $?
fi

# Inside Docker container
if [ ! -f /.dockerenv ]; then
    echo "This script should run inside a Docker container"
    exit 1
fi

# Install Ansible requirements
if [ -f requirements-ansible.txt ]; then
    pip install -r requirements-ansible.txt
fi

# Wait for services to be ready
if command_exists docker-compose; then
    echo "Waiting for services to be ready..."
    timeout 300 bash -c 'until docker-compose ps | grep -q "Up (healthy)"; do sleep 5; done' || \
        (echo "Services did not start in time" && docker-compose logs && exit 1)
fi

# Run tests with verbose output
echo "Running Ansible tests..."
ansible-playbook ansible_tests.yml -i "localhost," -c local -v

# Check the result and exit with appropriate status
if [ $? -eq 0 ]; then
    echo "✅ All tests passed successfully!"
    exit 0
else
    echo "❌ Some tests failed!"
    exit 1
fi
