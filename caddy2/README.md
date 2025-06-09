To integrate Caddy into your Docker Compose setup for dynamic subdomain routing without external configuration files, use the `caddy-docker-proxy` solution. This approach leverages Docker labels for service discovery and environment variables for global settings, eliminating the need for a standalone Caddyfile.

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

services:
  # Caddy Reverse Proxy with Docker Integration
  caddy:
    image: lucaslorentz/caddy-docker-proxy:latest
    environment:
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