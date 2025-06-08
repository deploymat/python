```bash
docker network create web

echo "🐋 Building and starting containers..."
docker-compose --env-file .env up -d --build
docker-compose up -d

```    


lucaslorentz/caddy-docker-proxy: Obraz Caddy, który dynamicznie generuje konfigurację na podstawie Docker metadata (labels).

Brak Caddyfile: Wszystko robisz przez labelsy, co spełnia Twoje wymaganie jednoplikowej konfiguracji.

Certyfikaty SSL: W pełni automatyczne dzięki integracji z Cloudflare przez caddy.tls.dns.





Absolutely! Below you'll find:

---

## ✅ 1. **Log Viewing Command**

To show logs for your API service (`myapi`):

```bash
docker-compose logs -f myapi
```

To show logs for **Caddy reverse proxy**:

```bash
docker-compose logs -f caddy
```

> Add `--tail=100` to limit to the last 100 lines.

---

## 🛠️ 2. **Installation Script** — `install.sh`

This script will:

* Clone or create your project folder
* Set up FastAPI app
* Write Dockerfile and `docker-compose.yml`
* Create `.env` file (you just need to add your Cloudflare token)
* Pull Docker images
* Build and run the services

## 🚀 How to use:

```bash
chmod +x install.sh
./install.sh
```



## 📦 How to use

1. Save as `Makefile` in your project root (same dir as `docker-compose.yml`)
2. Ensure `.env` exists (with `CF_API_TOKEN`)
3. Run commands like:

```bash
make up
make logs
make down
make restart
```

---

### ✅ Optional Enhancements:

* Add `lint`, `test`, or `deploy` commands
* Auto-reload support for dev via volumes
* Multiple service support: `PROJECT_NAME ?= $(SERVICE)` via arguments

Let me know if you'd like those included too.
