#!/bin/bash

set -e

# Load environment variables
if [ -f ".env" ]; then
    source .env
else
    echo "❌ Error: .env file not found"
    exit 1
fi

# Default values
DOMAIN=${DOMAIN:-localhost}
APP_NAME=${APP_NAME:-app}

# Function to check if a container is running
container_is_running() {
    docker ps --filter "name=$1" --format '{{.Names}}' | grep -q "^$1$"
}

# Function to wait for a container to be healthy
wait_for_container() {
    local container=$1
    local max_attempts=30
    local wait_seconds=5
    
    echo "⏳ Waiting for $container to be ready..."
    
    for ((i=1; i<=max_attempts; i++)); do
        if container_is_running "$container"; then
            echo "✅ $container is running"
            return 0
        fi
        echo "⏳ $container not ready yet (attempt $i/$max_attempts)..."
        sleep $wait_seconds
    done
    
    echo "❌ Timeout waiting for $container to start"
    return 1
}

echo "📁 Creating project structure..."
mkdir -p $APP_NAME/app
cd $APP_NAME

# Create FastAPI app if it doesn't exist
if [ ! -f "app/main.py" ]; then
    mkdir -p app
    echo "from fastapi import FastAPI\nfrom fastapi.middleware.cors import CORSMiddleware\n\napp = FastAPI()\n\n# Enable CORS\napp.add_middleware(\n    CORSMiddleware,\n    allow_origins=[\"*\"],\n    allow_credentials=True,\n    allow_methods=[\"*\"],\n    allow_headers=[\"*\"],\n)\n\n@app.get(\"/\")\nasync def read_root():\n    return {\"message\": \"Hello, World!\"}\n\n@app.get(\"/health\")\nasync def health_check():\n    return {\"status\": \"healthy\"}\n" > app/main.py
fi

# Create requirements.txt if it doesn't exist
if [ ! -f "requirements.txt" ]; then
    echo "fastapi\nuvicorn" > requirements.txt
fi

# Create Dockerfile if it doesn't exist
if [ ! -f "Dockerfile" ]; then
    echo "FROM python:3.9-slim\n\nWORKDIR /app\n\n# Install system dependencies\nRUN apt-get update && apt-get install -y --no-install-recommends \\\n    build-essential \\\n    && rm -rf /var/lib/apt/lists/*\n\n# Install Python dependencies\nCOPY requirements.txt .\nRUN pip install --no-cache-dir -r requirements.txt\n\n# Copy application code\nCOPY . .\n\n# Expose port\nEXPOSE 8080\n\n# Run the application\nCMD [\"uvicorn\", \"app.main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8080\"]" > Dockerfile
fi

# Create docker-compose.yml if it doesn't exist
if [ ! -f "../docker-compose.yml" ]; then
    echo "version: '3.8'\n\nservices:\n  caddy:\n    image: caddy:2.8.0\n    container_name: caddy\n    ports:\n      - \"80:80\"\n      - \"443:443\"\n    volumes:\n      - ./Caddyfile:/etc/caddy/Caddyfile:ro\n      - caddy_data:/data\n      - caddy_config:/config\n    environment:\n      - CLOUDFLARE_API_TOKEN=\${CF_API_TOKEN}\n    networks:\n      - web\n    restart: unless-stopped\n    healthcheck:\n      test: [\"CMD\", \"curl\", \"-f\", \"http://localhost:80/\"]\n      interval: 10s\n      timeout: 5s\n      retries: 3\n\n  myapi:\n    build:\n      context: .\n      dockerfile: Dockerfile\n    container_name: myapi\n    expose:\n      - \"8080\"\n    networks:\n      - web\n    restart: unless-stopped\n    healthcheck:\n      test: [\"CMD\", \"curl\", \"-f\", \"http://localhost:8080/health\"]\n      interval: 10s\n      timeout: 5s\n      retries: 3\n\nnetworks:\n  web:\n    driver: bridge\n\nvolumes:\n  caddy_data:\n  caddy_config:\n" > ../docker-compose.yml
fi

# Create Caddyfile if it doesn't exist
if [ ! -f "../Caddyfile" ]; then
    echo "${DOMAIN} {\n    # Enable the admin API (optional, for debugging)\n    # admin\n    \n    # Logging\n    log {\n        output file /var/log/caddy/access.log\n        format json\n    }\n    \n    # Handle API requests\n    handle_path /api/* {\n        reverse_proxy myapi:8080\n    }\n    \n    # Handle all other requests\n    handle {\n        reverse_proxy myapi:8080\n    }\n    \n    # Enable TLS with Cloudflare DNS challenge\n    tls {\n        dns cloudflare {env.CLOUDFLARE_API_TOKEN}\n    }\n}" > ../Caddyfile
fi

# Create logs directory
mkdir -p ../logs

# Create web network if it doesn't exist
if ! docker network inspect web >/dev/null 2>&1; then
    echo "🌐 Creating Docker network 'web'..."
    docker network create web
fi

echo "🚀 Starting services..."
cd ..

echo "🔧 Building and starting containers..."
docker-compose up -d --build

# Wait for containers to be ready
wait_for_container "caddy"
wait_for_container "myapi"

echo "✅ Services started successfully!"

# Run tests
echo -e "\n🚀 Running tests..."

# Run basic tests
if [ -f "./run_tests.sh" ]; then
    chmod +x ./run_tests.sh
    if ! ./run_tests.sh; then
        echo -e "\n${YELLOW}Basic tests failed. Check the output above for details.${NC}"
    fi
else
    echo -e "\n${YELLOW}⚠️  Basic test script not found. Skipping basic tests.${NC}"
fi

# Run Ansible tests
if [ -f "./run_ansible_tests.sh" ]; then
    echo -e "\n🔍 Running Ansible tests..."
    chmod +x ./run_ansible_tests.sh
    if ./run_ansible_tests.sh; then
        echo -e "\n${GREEN}✅ Ansible tests completed successfully!${NC}"
    else
        echo -e "\n${YELLOW}⚠️  Ansible tests completed with some failures.${NC}"
    fi
else
    echo -e "\n${YELLOW}⚠️  Ansible test script not found. Skipping Ansible tests.${NC}"
fi

echo "\n✅ Setup completed successfully!"
echo "🌐 Your FastAPI app should be available at: https://${DOMAIN}"
echo "📝 API documentation: https://${DOMAIN}/docs"

echo "\n📋 Container status:"
docker ps --filter "name=caddy|myapi" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
