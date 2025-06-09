.PHONY: help up down restart logs status clean test test-setup

# Default target when just 'make' is run
help:
	@echo "Available targets:"
	@echo "  make up      - Start all services in detached mode"
	@echo "  make down    - Stop and remove all containers"
	@echo "  make restart - Restart all services"
	@echo "  make logs    - View logs from all services"
	@echo "  make status  - Show status of all containers"
	@echo "  make clean   - Remove all containers, networks, and volumes"
	@echo "  make test    - Run Ansible tests against the services"
	@echo "  test-setup   - Set up the test environment"

# Start all services in detached mode
up:
	@if [ ! -f .env ]; then \
		echo "Creating .env file from .env.example"; \
		cp .env.example .env; \
		echo "Please edit .env with your configuration"; \
		exit 1; \
	fi
	docker-compose up -d

# Stop and remove all containers
down:
	docker-compose down

# Restart all services
restart: down up

# View logs from all services
logs:
	docker-compose logs -f

# Show status of all containers
status:
	docker-compose ps

# Remove all containers, networks, and volumes
clean:
	docker-compose down -v --remove-orphans

# Set up test environment
test-setup:
	python3 -m venv venv || true
	. venv/bin/activate && \
	pip install --upgrade pip && \
	pip install -r requirements-ansible.txt

# Run tests
test:
	./run_tests.sh

# Create .env.example if it doesn't exist
.env.example:
	@echo "DOMAIN=example.com" > .env.example
	@echo "CF_API_TOKEN=your_cloudflare_api_token" >> .env.example
	@echo "API_SUBDOMAIN=api" >> .env.example
	@echo "WEB_SUBDOMAIN=app" >> .env.example
	@echo "AUTH_SUBDOMAIN=auth" >> .env.example
