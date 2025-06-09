# Makefile for Caddy Reverse Proxy with Docker Compose
#
# Available commands:
#   make help       - Show this help
#   make up         - Start all services in detached mode
#   make down       - Stop and remove all containers
#   make restart    - Restart all services
#   make logs       - View logs from all services
#   make logs-tail  - Follow logs in real-time
#   make status     - Show status of all containers
#   make test       - Run tests (auto-detects environment)
#   make test-local - Run tests using local Python environment
#   make test-docker - Run tests in Docker container
#   make clean      - Remove all containers, networks, and volumes
#   make shell      - Open shell in the Caddy container
#   make reload     - Reload Caddy configuration
#   make certs      - Check SSL certificate status

.PHONY: help up down restart logs logs-tail status clean test test-setup test-docker test-local shell reload certs

# Show help (default target)
help: ## Show this help
	@awk 'BEGIN {FS = ":.*##"; printf "\n\033[1mUsage:\n  make \033[36m<target>\033[0m\n\nTargets:\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

# Start all services in detached mode
up: .env ## Start all services in detached mode
	@echo "Starting services..."
	@docker-compose up -d
	@echo "\nServices started. Run 'make status' to check container status."
	@echo "Run 'make logs' to view logs.\n"

# Stop and remove all containers
down: ## Stop and remove all containers
	@echo "Stopping and removing containers..."
	@docker-compose down
	@echo "\nAll containers stopped and removed.\n"

# Restart all services
restart: ## Restart all services
	@echo "Restarting services..."
	@docker-compose restart
	@echo "\nServices restarted. Run 'make status' to check container status.\n"

# View logs from all services
logs: ## View logs from all services
	@docker-compose logs --tail=100 -f

# Follow logs in real-time
logs-tail: ## Follow logs in real-time
	@docker-compose logs -f --tail=50

# Show status of all containers
status: ## Show status of all containers
	@echo "\nContainer status:"
	@docker-compose ps
	@echo "\nRunning containers:"
	@docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" --filter "name=caddy"
	@echo

# Remove all containers, networks, and volumes
clean: ## Remove all containers, networks, and volumes
	@echo "Removing containers, networks, and volumes..."
	@docker-compose down -v --remove-orphans
	@echo "\nAll containers, networks, and volumes removed.\n"

# Set up test environment
test-setup:
	python3 -m venv venv || true
	. venv/bin/activate && \
	pip install --upgrade pip && \
	pip install -r requirements-ansible.txt

# Run tests (auto-detect environment)
test: ## Run tests (auto-detects environment)
	@echo "Running tests..."
	@if [ -f /.dockerenv ] || command -v docker >/dev/null 2>&1; then \
		echo "Using Docker environment"; \
		$(MAKE) test-docker; \
	else \
		echo "Using local environment"; \
		$(MAKE) test-local; \
	fi
	@echo "\nTests completed. Run 'make logs' to view container logs if needed.\n"

# Run tests in local environment
test-local: test-setup ## Run tests using local Python environment
	@echo "Running tests locally..."
	@./run_tests.sh
	@echo "\nLocal tests completed.\n"

# Run tests in Docker container
test-docker: ## Run tests in Docker container
	@echo "Running tests in Docker..."
	@./run_docker_tests.sh
	@echo "\nDocker tests completed.\n"

# Open shell in the Caddy container
shell: ## Open shell in the Caddy container
	@docker-compose exec caddy /bin/sh

# Reload Caddy configuration
reload: ## Reload Caddy configuration
	@echo "Reloading Caddy configuration..."
	@docker-compose exec caddy caddy reload --config /etc/caddy/Caddyfile || \
		echo "\n\033[33m⚠️  No custom Caddyfile found. Configuration is managed dynamically via Docker labels.\033[0m\n"
	@echo "\nCaddy configuration reloaded. Services will be automatically reconfigured.\n"

# Check SSL certificate status
certs: ## Check SSL certificate status
	@echo "Checking SSL certificates and configuration..."
	@echo "\n\033[1m=== Caddy Configuration ===\033[0m"
	@docker-compose exec caddy caddy list-modules || true
	@echo "\n\033[1m=== Active Certificates ===\033[0m"
	@docker-compose exec caddy caddy list --config /etc/caddy/Caddyfile 2>/dev/null || \
		echo "\n\033[33m⚠️  No static Caddyfile found. Configuration is managed dynamically via Docker labels.\033[0m"
	@echo "\n\033[1m=== Certificate Status ===\033[0m"
	@docker-compose logs caddy 2>&1 | grep -E 'certificate obtained|TLS handshake|error' | tail -n 10 || true
	@echo "\n\033[32m✅ Certificate check complete. Run 'make logs' for detailed logs.\033[0m\n"

# Create .env file if it doesn't exist
.env:
	@if [ ! -f .env ]; then \
		echo "Creating .env file from .env.example"; \
		cp .env.example .env; \
		echo "\n\033[33m⚠️  Please edit .env with your configuration\033[0m"; \
		echo "   Required: DOMAIN and CF_API_TOKEN\n"; \
		exit 1; \
	fi

# Create .env.example if it doesn't exist
.env.example: ## Create .env.example file if it doesn't exist
	@if [ ! -f .env.example ]; then \
		echo "Creating .env.example file"; \
		echo "# Required" > .env.example; \
		echo "DOMAIN=example.com" >> .env.example; \
		echo "CF_API_TOKEN=your_cloudflare_api_token" >> .env.example; \
		echo "" >> .env.example; \
		echo "# Optional (defaults shown)" >> .env.example; \
		echo "API_SUBDOMAIN=api" >> .env.example; \
		echo "WEB_SUBDOMAIN=app" >> .env.example; \
		echo "AUTH_SUBDOMAIN=auth" >> .env.example; \
		echo "" >> .env.example; \
		echo "# Email for Let's Encrypt notifications" >> .env.example; \
		echo "# EMAIL=admin@example.com" >> .env.example; \
		echo "\n\033[32m✅ .env.example created. Copy it to .env and update with your values.\033[0m\n"; \
	fi
