# 🚀 Caddy Reverse Proxy with Docker + FastAPI

A lightweight, automated, and production-ready reverse proxy setup using **Caddy** with **Docker**, featuring:

* ✅ Automatic SSL via **Cloudflare DNS**
* ✅ Dynamic reverse proxy via Docker **labels**
* ✅ No manual Caddyfile needed
* ✅ **FastAPI** backend with auto-reload support
* ✅ Unified control with **Makefile**

---

## 📋 Table of Contents

* [✨ Features](#-features)
* [📋 Prerequisites](#-prerequisites)
* [🚀 Quick Start](#-quick-start)
* [📦 Installation](#-installation)
* [🛠️ Usage (Makefile)](#️-usage-makefile)
* [📜 Logs](#-logs)
* [⚙️ Configuration](#-configuration)
* [🔧 Optional Enhancements](#-optional-enhancements)
* [ℹ️ Notes](#️-notes)

---

## ✨ Features

* 🔐 Automatic HTTPS with Cloudflare DNS
* 🐳 Dockerized FastAPI microservice
* 🔄 Auto-reload during development
* ⚙️ Declarative service routing via Docker labels
* 🧼 Clean, one-file `Makefile` interface
* 🧪 Ready for testing and CI workflows

---

## 📋 Prerequisites

* ✅ Docker & Docker Compose
* ✅ Cloudflare-managed domain
* ✅ Cloudflare API Token with DNS edit permission

---

## 🚀 Quick Start

1. Clone repo & navigate:

   ```bash
   git clone https://your-repo-url
   cd your-repo
   ```

2. Create a Docker network (once):

   ```bash
   docker network create web || true
   ```

3. Add your `.env` file:

   ```env
   CLOUDFLARE_API_TOKEN=your_cloudflare_token_here
   DOMAIN=example.com
   EMAIL=admin@example.com
   ```

4. Start everything:

   ```bash
   make up
   ```

---

## 📦 Installation

You can also use the provided installation script:

```bash
chmod +x install.sh
./install.sh
```

The script will:

* Scaffold your project
* Download Docker images
* Configure FastAPI app
* Set up Caddy reverse proxy
* Start services

---

## 🛠️ Usage (Makefile)

Unified CLI control with:

```bash
make up         # Build and run all containers
make down       # Stop containers
make restart    # Restart containers
make logs       # Show combined logs (API + Caddy)
make logs-api   # Show only API logs
make logs-caddy # Show only Caddy logs
make shell      # Open shell in the API container
make clean      # Remove all containers, volumes, and dangling images
make health     # Check public HTTP health of the service
```

---

## 🧪 Developer Tools

You can also use these commands:

```bash
make lint     # Run linter (flake8)
make test     # Run tests (pytest)
make deploy   # (alias for up, or hook for real deploy)
```

✅ These run inside temporary containers – you don't need local Python installed.

---

## 📜 Logs

```bash
# Combined logs
make logs

# Individual service logs
make logs-api
make logs-caddy
```

---

## ⚙️ Configuration

1. `.env` file for secrets (required):

```env
CLOUDFLARE_API_TOKEN=your_cloudflare_token
EMAIL=admin@example.com
DOMAIN=example.com
```

2. Routing is defined via labels in `docker-compose.yml`:

```yaml
labels:
  caddy: api.${DOMAIN}
  caddy.reverse_proxy: "{{upstreams 8080}}"
  caddy.tls.dns: "cloudflare {env.CLOUDFLARE_API_TOKEN}"
```

No need to manually write a Caddyfile — Caddy dynamically reads this.

---

## 🔧 Optional Enhancements

### ✅ Lint & Test

Makefile includes:

```bash
make lint   # Runs flake8 on your Python code
make test   # Runs pytest inside container
```

### ♻️ Auto-reload

FastAPI auto-reload enabled via:

```yaml
command: uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
volumes:
  - ./app:/app/app:ro
```

### 📦 Multi-service support

Support multiple services using:

```bash
make logs SERVICE=auth
make shell SERVICE=web
```

`Makefile` dynamically uses `$(SERVICE)` to manage different containers.

---

## ℹ️ Notes

* Uses `lucaslorentz/caddy-docker-proxy` for dynamic reverse proxy configuration.
* All SSL certificates are auto-managed via Cloudflare DNS.
* Works well on ARM (Raspberry Pi), VPS, and dev machines.
* Recommended for small production deployments with minimal overhead.

