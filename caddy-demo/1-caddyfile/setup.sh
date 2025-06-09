#!/bin/bash
set -e

# Check if mkcert is installed
if ! command -v mkcert &> /dev/null; then
    echo "Error: mkcert is not installed. Please install it first:"
    echo "https://github.com/FiloSottile/mkcert#installation"
    exit 1
fi

# Create certs directory if it doesn't exist
mkdir -p certs

# Generate certificates
echo "Generating local certificates..."
mkcert -install
mkcert -cert-file certs/localhost.crt -key-file certs/localhost.key "localhost"

echo "Setup complete! You can now start the services with:"
echo "docker-compose up -d"
echo ""
echo "Then open: https://localhost in your browser"
