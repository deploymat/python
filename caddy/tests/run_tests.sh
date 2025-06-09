#!/bin/bash
set -e

# Set up Python virtual environment
VENV_DIR=".venv"
PYTHON_PATH=$(which python3)

echo "🔧 Setting up Python virtual environment..."
if [ ! -d "$VENV_DIR" ]; then
    $PYTHON_PATH -m venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip
    pip install ansible docker requests packaging
    deactivate
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Install required Ansible collections
echo "📦 Installing required Ansible collections..."
ansible-galaxy collection install -r tests/requirements.yml

# Set Python interpreter for Ansible
export ANSIBLE_PYTHON_INTERPRETER=$PYTHON_PATH

# Run the tests with verbose output
echo "🚀 Running tests..."
ansible-playbook tests/test.yml -i localhost, -c local -v \
  -e "ansible_python_interpreter=$PYTHON_PATH" \
  -e "caddy_domain=${DOMAIN:-localhost}" \
  -e "validate_certs=no"

# Deactivate virtual environment
deactivate

echo "✅ All tests completed successfully!"
