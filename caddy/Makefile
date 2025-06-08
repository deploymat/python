# Configuration
ENV_FILE=.env
COMPOSE=docker-compose --env-file $(ENV_FILE)
PROJECT_NAME=myapi
DOMAIN=api.example.com

# 🛠️ Build and Start
up:
	@echo "🚀 Starting services..."
	$(COMPOSE) up -d --build

# 🛑 Stop Services
down:
	@echo "🛑 Stopping services..."
	$(COMPOSE) down

# 🔄 Restart services
restart: down up

# 🧼 Clean up containers and images
clean:
	@echo "🧽 Cleaning up..."
	$(COMPOSE) down --volumes --remove-orphans
	docker rmi $$(docker images -f "dangling=true" -q) 2>/dev/null || true

# 📜 View logs
logs:
	@echo "📄 Showing logs (API and Caddy)..."
	$(COMPOSE) logs -f $(PROJECT_NAME) caddy

logs-api:
	$(COMPOSE) logs -f $(PROJECT_NAME)

logs-caddy:
	$(COMPOSE) logs -f caddy

# 🐚 Open shell inside API container
shell:
	docker exec -it $(PROJECT_NAME) /bin/sh

# 📡 Create Docker network (first-time setup)
network:
	docker network create web || true

# 🧪 Health check
health:
	curl -s https://$(DOMAIN) || echo "❌ Service not responding"

# 🆘 Help
help:
	@echo ""
	@echo "🛠️  Available commands:"
	@echo "  make up         – Build and start services"
	@echo "  make down       – Stop services"
	@echo "  make restart    – Restart services"
	@echo "  make clean      – Stop and remove all containers, volumes, and dangling images"
	@echo "  make logs       – Show logs for API and Caddy"
	@echo "  make logs-api   – Show logs only for API"
	@echo "  make logs-caddy – Show logs only for Caddy"
	@echo "  make shell      – Open shell in API container"
	@echo "  make network    – Create shared Docker network (web)"
	@echo "  make health     – Check public API response"
	@echo ""
