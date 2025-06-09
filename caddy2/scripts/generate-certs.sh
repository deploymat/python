#!/bin/bash

# Exit on error
set -e

# Check if mkcert is installed
if ! command -v mkcert &> /dev/null; then
    echo "Error: mkcert is not installed. Please install it first."
    echo "On Ubuntu/Debian: sudo apt install mkcert"
    echo "On macOS: brew install mkcert"
    exit 1
fi

# Create certs directory if it doesn't exist
mkdir -p ../certs

# Generate local CA if it doesn't exist
if [ ! -f "$HOME/.local/share/mkcert/rootCA.pem" ]; then
    echo "Generating local CA..."
    mkcert -install
fi

# Generate certificates for local development
echo "Generating SSL certificates..."

# Generate certificate for localhost
mkcert -cert-file ../certs/localhost.crt -key-file ../certs/localhost.key \
    "localhost" "*.localhost" "127.0.0.1" "::1"

# Generate certificates for development domains
DOMAINS=(
    "lvh.me" "*.lvh.me"
    "test" "*.test"
    "local" "*.local"
    "localhost" "*.localhost"
    "127.0.0.1" "::1"
)

mkcert -cert-file ../certs/wildcard.crt -key-file ../certs/wildcard.key \
    "${DOMAINS[@]}"

echo "\nCertificates generated in the certs/ directory:"
ls -la ../certs/

echo "\n✅ Done! Certificates have been generated."
echo "You may need to add the following to your /etc/hosts file:"
echo "127.0.0.1  lvh.me api.lvh.me app.lvh.me auth.lvh.me"

exit 0
