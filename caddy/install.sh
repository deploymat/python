#!/bin/bash

set -e
# from .env import all variables
source .env

# Function to run tests
run_tests() {
    echo "🚀 Running tests..."
    if [ -f "tests/run_tests.sh" ]; then
        cd tests
        ./run_tests.sh
        cd ..
    else
        echo "⚠️  Test script not found. Skipping tests."
    fi
}

echo "📁 Creating project structure..."
mkdir -p $APP_NAME/app
cd $APP_NAME

# Create FastAPI app if it doesn't exist
if [ ! -f "app/main.py" ]; then
    echo "from fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get(\"/\")\nasync def read_root():\n    return {\"message\": \"Hello, World!\"}" > app/main.py
fi

# Create requirements.txt if it doesn't exist
if [ ! -f "requirements.txt" ]; then
    echo "fastapi\nuvicorn" > requirements.txt
fi

# Create Dockerfile if it doesn't exist
if [ ! -f "Dockerfile" ]; then
    echo "FROM python:3.9-slim\n\nWORKDIR /app\n\nCOPY requirements.txt .\nRUN pip install --no-cache-dir -r requirements.txt\n\nCOPY . .\n\nCMD [\"uvicorn\", \"app.main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8080\"]" > Dockerfile
fi

# Create docker-compose.yml if it doesn't exist
if [ ! -f "../docker-compose.yml" ]; then
    echo "services:
  caddy:
    image: caddy:2.8.0
    container_name: caddy
    ports:
      - \"80:80\"
      - \"443:443\"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile
      - caddy_data:/data
      - caddy_config:/config
    environment:
      - CLOUDFLARE_API_TOKEN=\${CF_API_TOKEN}
    networks:
      - web
    restart: unless-stopped

  myapi:
    build: .
    container_name: myapi
    expose:
      - \"8080\"
    networks:
      - web
    command: uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

networks:
  web:
    external: true

volumes:
  caddy_data:
  caddy_config:" > ../docker-compose.yml
fi

# Create Caddyfile if it doesn't exist
if [ ! -f "../Caddyfile" ]; then
    echo "${DOMAIN} {
    reverse_proxy myapi:8080
    tls {
        dns cloudflare {env.CLOUDFLARE_API_TOKEN}
    }" > ../Caddyfile
fi

echo "🚀 Starting services..."
cd ..
docker-compose up -d --build

echo "⏳ Waiting for services to be ready..."
sleep 10

# Run tests
run_tests

echo "✅ Setup completed successfully!"
echo "🌐 Your FastAPI app should be available at: https://${DOMAIN}"
