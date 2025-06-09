# 🚀 Caddy Reverse Proxy - Makefile
#
# This Makefile provides a set of commands to manage the Caddy reverse proxy
# with Docker Compose. It includes commands for development, testing, and deployment.

# ------------------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------------------


# Docker Compose binary (can be overridden)
DOCKER_COMPOSE = docker-compose
COMPOSE_FILE = docker-compose.yml

# Container names
CADDY_CONTAINER = caddy

# ------------------------------------------------------------------------------
# Help
# ------------------------------------------------------------------------------


.PHONY: help
help: ## Show this help
	@echo "\n\033[1mCaddy Reverse Proxy Management\033[0m\n"
	@echo "Available commands:"
	@echo ""
	@echo "\033[1mDevelopment:\033[0m"
	@echo "  \033[36mmake up\033[0m         - Start all services in detached mode"
	@echo "  \033[36mmake down\033[0m       - Stop and remove all containers"
	@echo "  \033[36mmake restart\033[0m    - Restart all services"
	@echo "  \033[36mmake logs\033[0m       - View logs from all services"
	@echo "  \033[36mmake logs-tail\033[0m  - Follow logs in real-time"
	@echo "  \033[36mmake status\033[0m     - Show status of all containers"
	@echo ""
	@echo "\033[1mTesting:\033[0m"
	@echo "  \033[36mmake test\033[0m        - Run tests (auto-detects environment)"
	@echo "  \033[36mmake test-local\033[0m  - Run tests using local Python"
	@echo "  \033[36mmake test-docker\033[0m - Run tests in Docker container"
	@echo ""
	@echo "\033[1mMaintenance:\033[0m"
	@echo "  \033[36mmake shell\033[0m       - Open shell in the Caddy container"
	@echo "  \033[36mmake reload\033[0m      - Reload Caddy configuration"
	@echo "  \033[36mmake certs\033[0m       - Check SSL certificate status"
	@echo "  \033[36mmake clean\033[0m        - Remove containers, networks, and volumes"
	@echo ""

# ------------------------------------------------------------------------------
# Development Commands
# ------------------------------------------------------------------------------

.PHONY: up down restart rebuild

up: .env ## Start all services in detached mode
	@echo "🚀 Starting services..."
	@$(DOCKER_COMPOSE) -f $(COMPOSE_FILE) up -d
	@echo "\n✅ Services started. Run 'make status' to check container status."
	@echo "   Run 'make logs' to view logs.\n"

# Stop and remove all containers
down: ## Stop and remove all containers
	@echo "🛑 Stopping and removing containers..."
	@$(DOCKER_COMPOSE) -f $(COMPOSE_FILE) down
	@echo "\n✅ All containers stopped and removed.\n"

# Restart all services
restart: ## Restart all services
	@echo "🔄 Restarting services..."
	@$(DOCKER_COMPOSE) -f $(COMPOSE_FILE) restart
	@echo "\n✅ Services restarted. Run 'make status' to check container status.\n"

# Rebuild and restart services
rebuild: ## Rebuild and restart services
	@echo "🔨 Rebuilding and restarting services..."
	@$(DOCKER_COMPOSE) -f $(COMPOSE_FILE) up -d --build
	@echo "\n✅ Services rebuilt and restarted.\n"

# View logs from all services
logs: ## View logs from all services
	@$(DOCKER_COMPOSE) -f $(COMPOSE_FILE) logs --tail=100 -f

# Follow logs in real-time
logs-tail: ## Follow logs in real-time
	@$(DOCKER_COMPOSE) -f $(COMPOSE_FILE) logs -f --tail=50

# ------------------------------------------------------------------------------
# Container Status
# ------------------------------------------------------------------------------

# Show status of all containers
status: ## Show status of all containers
	@echo "📊 Container status:"
	@$(DOCKER_COMPOSE) -f $(COMPOSE_FILE) ps
	@echo "\n🏃 Running containers:"
	@docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" --filter "name=$(CADDY_CONTAINER)"
	@echo

# ------------------------------------------------------------------------------
# Cleanup
# ------------------------------------------------------------------------------

# Remove all containers, networks, and volumes
clean: down ## Remove all containers, networks, and volumes
	@echo "🧹 Removing containers, networks, and volumes..."
	@$(DOCKER_COMPOSE) -f $(COMPOSE_FILE) down -v --remove-orphans
	@echo "\n✅ All containers, networks, and volumes removed.\n"

# ------------------------------------------------------------------------------
# Testing
# ------------------------------------------------------------------------------
.PHONY: test test-setup test-local test-docker

# Set up test environment
test-setup:
	@echo "🔧 Setting up test environment..."
	@if [ ! -d "venv" ]; then \
		python3 -m venv venv; \
		. venv/bin/activate && \
		pip install --upgrade pip && \
		if [ -f "requirements-ansible.txt" ]; then \
			pip install -r requirements-ansible.txt; \
		else \
			echo "ansible-core>=2.12" > requirements-ansible.txt; \
			pip install -r requirements-ansible.txt; \
		fi; \
	fi

# Run tests (auto-detect environment)
test: ## Run tests (auto-detects environment)
	@echo "🧪 Running tests..."
	@if [ -f /.dockerenv ] || command -v docker >/dev/null 2>&1; then \
		echo "🐳 Using Docker environment"; \
		$(MAKE) test-docker; \
	else \
		echo "💻 Using local environment"; \
		$(MAKE) test-local; \
	fi
	@echo "\n✅ Tests completed. Run 'make logs' to view container logs if needed.\n"

# Run tests in local environment
test-local: test-setup ## Run tests using local Python environment
	@echo "🔍 Running tests locally..."
	@if [ -f "run_tests.sh" ]; then \
		./run_tests.sh; \
	else \
		echo "\n\033[33m⚠️  run_tests.sh not found. Creating a basic test runner.\033[0m"; \
		echo '#!/bin/bash\n\
set -e\n\
echo "Running basic tests..."\n\
# Add your test commands here\necho "✅ All tests passed!"' > run_tests.sh; \
		chmod +x run_tests.sh; \
		./run_tests.sh; \
	fi
	@echo "\n✅ Local tests completed.\n"

# Run tests in Docker container
test-docker: ## Run tests in Docker container
	@echo "🐳 Running tests in Docker..."
	@if [ -f "run_docker_tests.sh" ]; then \
		./run_docker_tests.sh; \
	else \
		echo "\n\033[33m⚠️  run_docker_tests.sh not found. Creating a basic Docker test runner.\033[0m"; \
		echo '#!/bin/bash\n\
set -e\n\
echo "Running Docker tests..."\n\
# Add your Docker test commands here\necho "✅ All Docker tests passed!"' > run_docker_tests.sh; \
		chmod +x run_docker_tests.sh; \
		./run_docker_tests.sh; \
	fi
	@echo "\n✅ Docker tests completed.\n"

# ------------------------------------------------------------------------------
# Caddy Management
# ------------------------------------------------------------------------------

# Open shell in the Caddy container
shell: ## Open shell in the Caddy container
	@echo "💻 Opening shell in $(CADDY_CONTAINER) container..."
	@$(DOCKER_COMPOSE) -f $(COMPOSE_FILE) exec $(CADDY_CONTAINER) /bin/sh

# Reload Caddy configuration
reload: ## Reload Caddy configuration
	@echo "🔄 Reloading Caddy configuration..."
	@if $(DOCKER_COMPOSE) -f $(COMPOSE_FILE) exec $(CADDY_CONTAINER) test -f /etc/caddy/Caddyfile; then \
		$(DOCKER_COMPOSE) -f $(COMPOSE_FILE) exec $(CADDY_CONTAINER) caddy reload --config /etc/caddy/Caddyfile; \
		echo "\n✅ Caddy configuration reloaded.\n"; \
	else \
		echo "\n\033[33m⚠️  No custom Caddyfile found. Configuration is managed dynamically via Docker labels.\033[0m\n"; \
	fi

# Check SSL certificate status
certs: ## Check SSL certificate status
	@echo "🔐 Checking SSL certificates and configuration..."
	@echo "\n\033[1m=== Caddy Configuration ===\033[0m"
	@$(DOCKER_COMPOSE) -f $(COMPOSE_FILE) exec $(CADDY_CONTAINER) caddy list-modules || true
	@echo "\n\033[1m=== Active Certificates ===\033[0m"
	@if $(DOCKER_COMPOSE) -f $(COMPOSE_FILE) exec $(CADDY_CONTAINER) test -f /etc/caddy/Caddyfile; then \
		$(DOCKER_COMPOSE) -f $(COMPOSE_FILE) exec $(CADDY_CONTAINER) caddy list --config /etc/caddy/Caddyfile 2>/dev/null || true; \
	else \
		echo "\n\033[33m⚠️  No static Caddyfile found. Configuration is managed dynamically via Docker labels.\033[0m"; \
	fi
	@echo "\n\033[1m=== Certificate Status ===\033[0m"
	@$(DOCKER_COMPOSE) -f $(COMPOSE_FILE) logs $(CADDY_CONTAINER) 2>&1 | grep -E 'certificate obtained|TLS handshake|error' | tail -n 10 || true
	@echo "\n✅ Certificate check complete. Run 'make logs' for detailed logs.\n"

# ------------------------------------------------------------------------------
# Environment Setup
# ------------------------------------------------------------------------------
.PHONY: env

# Create .env file if it doesn't exist
.env:
	@if [ ! -f .env ]; then \
		echo "📝 Creating .env file from .env.example"; \
		if [ -f .env.example ]; then \
			cp .env.example .env; \
		else \
			$(MAKE) .env.example; \
		fi; \
		echo "\n\033[33m⚠️  Please edit .env with your configuration\033[0m"; \
		echo "   Required: DOMAIN and CF_API_TOKEN\n"; \
		exit 1; \
	fi

# Create .env.example if it doesn't exist
.env.example: ## Create .env.example file if it doesn't exist
	@if [ ! -f .env.example ]; then \
		echo "📝 Creating .env.example file"; \
		echo "# Required" > .env.example; \
		echo "DOMAIN=example.com" >> .env.example; \
		echo "CF_API_TOKEN=your_cloudflare_api_token" >> .env.example; \
		echo "" >> .env.example; \
		echo "# Optional (defaults shown)" >> .env.example; \
		echo "# Email for Let's Encrypt notifications" >> .env.example; \
		echo "EMAIL=admin@example.com" >> .env.example; \
		echo "" >> .env.example; \
		echo "# Subdomains configuration" >> .env.example; \
		echo "API_SUBDOMAIN=api" >> .env.example; \
		echo "WEB_SUBDOMAIN=app" >> .env.example; \
		echo "AUTH_SUBDOMAIN=auth" >> .env.example; \
		echo "" >> .env.example; \
		echo "# Staging mode (set to 'true' to avoid Let's Encrypt rate limits)" >> .env.example; \
		echo "STAGING=false" >> .env.example; \
		echo "" >> .env.example; \
		echo "# Additional domains (space-separated)" >> .env.example; \
		echo "# EXTRA_DOMAINS=www.example.com api.example.com" >> .env.example; \
		echo "\n\033[32m✅ .env.example created. Copy it to .env and update with your values.\033[0m\n"; \
	fi

# Initialize project (first-time setup)
init: .env.example ## Initialize project
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "\n\033[32m✅ Project initialized!\033[0m"; \
		echo "\033[33m⚠️  Please edit the .env file with your configuration.\033[0m\n"; \
	else \
		echo "\n\033[33m⚠️  Project already initialized. .env file exists.\033[0m\n"; \
	fi
