.PHONY: up down restart logs clean certs help

# Default target
help:
	@echo "Available commands:"
	@echo "  make up      - Start all services in detached mode"
	@echo "  make down    - Stop and remove all containers"
	@echo "  make logs    - View container logs"
	@echo "  make restart - Restart all services"
	@echo "  make certs   - Generate SSL certificates"
	@echo "  make clean   - Remove containers and volumes"

# Start services
up:
	@echo "Starting services..."
	docker-compose up -d

# Stop and remove containers
down:
	@echo "Stopping services..."
	docker-compose down

# View logs
logs:
	docker-compose logs -f

# Restart services
restart: down up

# Generate SSL certificates
certs:
	@if ! command -v mkcert &> /dev/null; then \
		echo "Error: mkcert is not installed. Please install it first:"; \
		echo "https://github.com/FiloSottile/mkcert#installation"; \
		exit 1; \
	fi
	@mkdir -p certs
	@echo "Generating local certificates..."
	mkcert -install
	mkcert -cert-file certs/localhost.crt -key-file certs/localhost.key "localhost"
	@echo "Certificates generated in certs/"

# Clean up
clean: down
	@echo "Removing volumes..."
	@docker volume rm -f 1-caddyfile_caddy_data 1-caddyfile_caddy_config 2>/dev/null || true
	@echo "Cleanup complete"
