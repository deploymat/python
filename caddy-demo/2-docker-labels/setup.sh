#!/bin/bash
set -e

# Check if running as root
if [ "$(id -u)" -ne 0 ]; then
    echo "This script needs to be run as root to modify /etc/hosts"
    echo "Please run with sudo or as root"
    exit 1
fi

# Add entries to /etc/hosts
echo "Adding entries to /etc/hosts..."
if ! grep -q "web.demo.local" /etc/hosts; then
    echo "127.0.0.1 web.demo.local api.demo.local" >> /etc/hosts
    echo "Added entries to /etc/hosts"
else
    echo "Entries already exist in /etc/hosts"
fi

# Create network if it doesn't exist
if ! docker network inspect caddy_network >/dev/null 2>&1; then
    echo "Creating Docker network..."
    docker network create caddy_network
fi

echo ""
echo "Setup complete! You can now start the services with:"
echo "docker-compose up -d"
echo ""
echo "Then access the services at:"
echo "- Web: https://web.demo.local"
echo "- API: https://api.demo.local"
echo ""
echo "Note: You may need to accept the self-signed certificate in your browser."
