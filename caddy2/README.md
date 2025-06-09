# 🚀 Caddy Reverse Proxy with Docker

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Docker Pulls](https://img.shields.io/docker/pulls/lucaslorentz/caddy-docker-proxy.svg)](https://hub.docker.com/r/lucaslorentz/caddy-docker-proxy/)

A production-ready Caddy reverse proxy setup with Docker Compose, featuring automatic HTTPS via Let's Encrypt and Cloudflare DNS. Designed for zero-downtime deployments and dynamic service discovery.

## 📋 Table of Contents

- [Features](#-features)
- [Prerequisites](#-prerequisites)
- [Quick Start](#-quick-start)
- [Configuration](#-configuration)
- [Project Structure](#-project-structure)
- [Usage](#-usage)
- [Testing](#-testing)
- [Troubleshooting](#-troubleshooting)
- [License](#-license)

## ✨ Features

- **Zero Config**: Uses Docker labels for configuration
- **Automatic HTTPS**: Via Let's Encrypt with Cloudflare DNS challenge
- **Dynamic Service Discovery**: Add/remove services without restarting Caddy
- **Multi-Architecture**: Supports both AMD64 and ARM64
- **Built-in Testing**: Ansible tests for local and CI environments
- **Simple Management**: Comprehensive Makefile for common tasks

## 🛠 Prerequisites

- Docker and Docker Compose
- Domain with DNS managed by Cloudflare
- Cloudflare API token with DNS edit permissions
- `mkcert` for local development (optional)

## ⚡ Quick Start

1. Clone the repository:
   ```bash
   git clone <repository-url> caddy2
   cd caddy2
   ```

2. Set up environment:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. Start services:
   ```bash
   make up
   ```

4. Verify installation:
   ```bash
   make test
   ```

## ⚙️ Configuration

### Environment Variables

Create or edit `.env` file with these variables:

```env
# Required for Cloudflare DNS challenge
DOMAIN=yourdomain.com
CF_API_TOKEN=your_cloudflare_token

# Optional: Email for Let's Encrypt notifications
# EMAIL=your-email@example.com

# Optional: Staging mode for testing (set to 'true' to avoid rate limits)
# STAGING=false

# Optional: Additional domains (space-separated)
# EXTRA_DOMAINS=www.yourdomain.com api.yourdomain.com

# Optional (defaults shown)
API_SUBDOMAIN=api
WEB_SUBDOMAIN=app
AUTH_SUBDOMAIN=auth
```

### Adding Services

Add new services to `docker-compose.yml` with these labels:

```yaml
service-name:
  image: your-image:tag
  labels:
    - caddy=${SERVICE_SUBDOMAIN}.${DOMAIN}
    - caddy.reverse_proxy={{upstreams 80}}
  networks:
    - app-network
```

## 🧪 Testing

### Run All Tests
```bash
make test  # Auto-detects environment
```

### Test in Docker
```bash
make test-docker
```

### Test Locally
```bash
make test-local
```

## 🛠 Makefile Commands

| Command           | Description                                      |
|-------------------|--------------------------------------------------|
| `make up`        | Start all services in detached mode              |
| `make down`      | Stop and remove all containers                   |
| `make restart`   | Restart all services                            |
| `make logs`      | View logs from all services                     |
| `make status`    | Show status of all containers                   |
| `make test`      | Run tests (auto-detects environment)            |
| `make test-docker`| Run tests in Docker container                   |
| `make test-local`| Run tests using local Python environment        |
| `make clean`     | Remove all containers, networks, and volumes    |


## 🔄 Adding New Services

1. Add your service to `docker-compose.yml`
2. Add appropriate Caddy labels
3. Update the `.env` file if needed
4. Run `make up` to deploy

Example service configuration:

```yaml
service-name:
  image: nginx:alpine
  labels:
    - caddy=service.${DOMAIN}
    - caddy.reverse_proxy={{upstreams 80}}
  networks:
    - app-network
```

## 🔒 Security Considerations

- Keep your `.env` file secure and never commit it to version control
- Use least-privilege Cloudflare API tokens
- Regularly update your Docker images
- Enable Docker content trust

## 📚 Documentation

- [Caddy Docker Proxy](https://github.com/lucaslorentz/caddy-docker-proxy/)
- [Caddy Documentation](https://caddyserver.com/docs/)
- [Cloudflare API Tokens](https://dash.cloudflare.com/profile/api-tokens)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

### ✅ Key Features
- **Zero external config files** (no Caddyfile)
- **Automatic HTTPS via Let's Encrypt + Cloudflare DNS**
- **Dynamic service discovery** (add/remove services via Docker labels)
- **ARM64 compatible**
- **Single Docker Compose file**

---

### 🧩 Docker Compose Configuration

```yaml
version: '3.8'

networks:
  app-network:
    driver: bridge

## 📁 Project Structure

```
caddy2/
├── .env                    # Environment variables
├── .env.example            # Example environment configuration
├── .gitignore              # Git ignore rules
├── Caddyfile               # Base Caddy configuration
├── docker-compose.yml      # Main Docker Compose configuration
├── Makefile                # Project automation
├── README.md               # This file
├── config/                 # Additional Caddy configuration files
│   └── custom-config.json  # Custom Caddy JSON config
├── certs/                  # SSL certificates (auto-generated)
│   ├── localhost.crt      # Local development certificate
│   └── localhost.key       # Local development key
└── scripts/                # Utility scripts
    ├── generate-certs.sh   # Certificate generation script
    └── test/               # Test scripts
        ├── run_tests.sh    # Test runner
        └── test_api.py     # API test cases
```

## 🚀 Usage

### Starting Services

```bash
# Start all services in detached mode
make up

# View logs
make logs

# Check service status
make status
```

### Managing Services

```bash
# Stop services
make down

# Restart services
make restart

# Rebuild and restart
make rebuild
```

### Development

```bash
# Open shell in Caddy container
make shell

# Reload Caddy configuration
make reload

# Check certificate status
make certs
```

## 🧪 Testing

Run the test suite:

```bash
# Auto-detect environment and run appropriate tests
make test

# Run tests locally (requires Python and Ansible)
make test-local

# Run tests in Docker container
make test-docker
```

## 🐛 Troubleshooting

### Common Issues

1. **Certificate Generation Fails**
   - Ensure your domain's DNS is properly configured
   - Verify Cloudflare API token has correct permissions
   - Check Docker logs: `docker-compose logs caddy`

2. **Port Conflicts**
   - Stop other services using ports 80/443
   - Or modify ports in `docker-compose.yml`

3. **Container Fails to Start**
   - Check logs: `make logs`
   - Verify environment variables are set correctly

### Viewing Logs

```bash
# View last 100 log lines
make logs

# Follow logs in real-time
make logs-tail
```

## 📜 License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Caddy Server](https://caddyserver.com/)
- [Caddy Docker Proxy](https://github.com/lucaslorentz/caddy-docker-proxy)
- [Let's Encrypt](https://letsencrypt.org/)

## 📝 Todo

- [ ] Add monitoring setup
- [ ] Include rate limiting example
- [ ] Add backup/restore scripts
- [ ] Document advanced configurations
      - CADDY_DOCKER_PROXY_ACME_DNS=cloudflare ${CF_API_TOKEN}
      - CADDY_DOCKER_PROXY_ACME_EMAIL=admin@example.com
      - DOMAIN=example.com
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    ports:
      - "80:80"
      - "443:443"
    networks:
      - app-network

  # Example Microservice 1: API Service
  api:
    image: your-api-image:latest
    labels:
      - caddy=${API_SUBDOMAIN}.${DOMAIN}
      - caddy.reverse_proxy={{upstreams 8080}}
    networks:
      - app-network

  # Example Microservice 2: Web App
  web:
    image: your-web-app:latest
    labels:
      - caddy=${WEB_SUBDOMAIN}.${DOMAIN}
      - caddy.reverse_proxy={{upstreams 3000}}
    networks:
      - app-network

  # Example Microservice 3: Auth Service
  auth:
    image: your-auth-service:latest
    labels:
      - caddy=${AUTH_SUBDOMAIN}.${DOMAIN}
      - caddy.reverse_proxy={{upstreams 4000}}
    networks:
      - app-network
```

---

### 📁 Environment Variables (`.env` file)

```env
DOMAIN=example.com
CF_API_TOKEN=your_cloudflare_api_token
API_SUBDOMAIN=api
WEB_SUBDOMAIN=app
AUTH_SUBDOMAIN=auth
```

---

### 🔐 How It Works

- **Dynamic Configuration**: The `caddy-docker-proxy` image automatically detects containers with `caddy.*` labels.
- **HTTPS Automation**: Uses Cloudflare DNS for Let's Encrypt challenges via the `CADDY_DOCKER_PROXY_ACME_DNS` environment variable.
- **Service Discovery**: The `{{upstreams PORT}}` template routes traffic to the correct container based on exposed ports.

---

### 🧪 Adding New Services

To deploy a new service (e.g., `dashboard`), simply add it to your Docker Compose with the appropriate labels:

```yaml
dashboard:
  image: your-dashboard:latest
  labels:
    - caddy=dashboard.example.com
    - caddy.reverse_proxy={{upstreams 8000}}
  networks:
    - app-network
```

No need to restart Caddy or edit any configuration files — it auto-reloads!

---

### 🛡️ Security Notes

- **Docker Socket**: Mounting `/var/run/docker.sock` gives Caddy access to Docker events. Ensure your system is secured (e.g., restricted access to Docker).
- **Cloudflare Token**: Use a **scoped token** with only DNS write permissions for `example.com`.

---

### 📦 Resource Usage

- **Memory**: ~40–80MB baseline
- **Performance**: Sufficient for most microservices (3,750+ req/s)
- **ARM Compatibility**: Works on Raspberry Pi 3+ and newer ARM64 devices

---

### ✅ Why This Works

- **No Caddyfile needed** — all config via environment variables and Docker labels.
- **Fully declarative** — everything defined in `docker-compose.yml`.
- **Scalable** — add new services with minimal effort.
- **Secure** — automatic HTTPS via DNS-01 with Cloudflare.

---

### 🧼 Cleanup (Optional)

If you want to reset SSL certificates or force Caddy to re-fetch config:

```bash
docker-compose down -v
```

This removes persistent data (e.g., certificates), and a fresh setup will occur on next `up`.

---

### 📌 Summary

This solution offers the **best balance of simplicity, flexibility, and security** for microservices on resource-constrained systems. It avoids vendor lock-in (unlike Cloudflare Tunnels), keeps memory usage low (unlike Traefik), and provides **zero-config deployment** with full HTTPS automation.