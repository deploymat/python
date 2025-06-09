.PHONY: up down restart logs setup clean help

# Default target
help:
	@echo "Available commands:"
	@echo "  make up     - Start all services in detached mode"
	@echo "  make down   - Stop and remove all containers"
	@echo "  make logs   - View container logs"
	@echo "  make restart - Restart all services"
	@echo "  make setup  - Initial setup (modifies /etc/hosts)"
	@echo "  make clean  - Remove containers, networks, and volumes"

# Start services
up:
	@echo "Building and starting services..."
	docker-compose up -d --build
	@echo "\nServices available at:"
	@echo "- Web: https://web.demo.local"
	@echo "- API: https://api.demo.local"

# Stop and remove containers
down:
	@echo "Stopping services..."
	docker-compose down

# View logs
logs:
	docker-compose logs -f

# Restart services
restart: down up

# Initial setup
setup:
	@if [ "$(shell id -u)" -ne 0 ]; then \
		echo "Error: This command requires root privileges. Please run with sudo."; \
		exit 1; \
	fi
	@echo "Adding entries to /etc/hosts..."
	@if ! grep -q "web.demo.local" /etc/hosts; then \
		echo "127.0.0.1 web.demo.local api.demo.local" >> /etc/hosts; \
		echo "Added entries to /etc/hosts"; \
	else \
		echo "Entries already exist in /etc/hosts"; \
	fi
	@if ! docker network inspect caddy_network >/dev/null 2>&1; then \
		echo "Creating Docker network..."; \
		docker network create caddy_network; \
	fi
	@echo "\nSetup complete! You can now start the services with:"
	@echo "  make up"

# Clean up everything
clean: down
	@echo "Removing volumes and networks..."
	@docker volume rm -f 2-docker-labels_caddy_data 2-docker-labels_caddy_config 2>/dev/null || true
	@docker network rm caddy_network 2>/dev/null || true
	@echo "Cleanup complete"
