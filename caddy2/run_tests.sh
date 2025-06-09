#!/bin/bash
set -e

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements-ansible.txt
else
    source venv/bin/activate
fi

# Run Ansible tests
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
