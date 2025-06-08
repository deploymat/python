# 🐳 PyDock - Python Docker Deployment Manager

PyDock to narzędzie do automatycznego wdrażania aplikacji Docker Compose na VPS **bez modyfikacji środowiska lokalnego**. Wszystko działa w izolowanych kontenerach z automatycznym SSL i reverse proxy.

## ✨ Główne funkcje

- 🚀 **Jednokomendowy deployment** - `pydock deploy`
- 🔒 **Automatyczne SSL** - Let's Encrypt przez Caddy
- 🌐 **Reverse proxy** - Automatyczna konfiguracja domen
- 🐳 **Izolacja kontenerów** - Bez modyfikacji lokalnego środowiska
- 📊 **Monitoring** - Status, logi, metryki
- 🛡️ **Bezpieczeństwo** - SSH, generated passwords
- 🔄 **Zero-downtime** - Rolling updates


### 🚀 **REST API Endpoints (FastAPI):**

```bash
# Start API server
poetry run pydock api start --port 8080

# Deployment endpoint (jak w dynapsys)
curl -X POST http://localhost:8080/deploy \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "domain": "mojadomena.pl",
    "vps_ip": "192.168.1.100", 
    "cf_token": "cloudflare-token",
    "source": "https://github.com/user/repo.git",
    "auto_dns": true
  }'

# WebSocket for real-time logs
wscat -c ws://localhost:8080/ws

# Other endpoints
GET  /health              # Health check
GET  /deployments         # List deployments
POST /cloudflare/dns      # Setup DNS
GET  /logs/stream         # Stream logs
```

### 🐚 **Interactive Shell:**

```bash
poetry run pydock shell

# W shell:
(pydock) status              # Project status
(pydock) deploy              # Deploy with confirmation
(pydock) cloudflare setup    # Auto DNS setup
(pydock) git validate        # Validate repo
(pydock) server start        # Start API server
(pydock) env show            # Show environment
(pydock) help                # Full help
```

### ☁️ **Cloudflare Integration:**

```python
# Programmatic usage
from pydock.cloudflare import CloudflareManager

cf = CloudflareManager("your-token")

# Setup all DNS records automatically
await cf.setup_dns_records("mojadomena.pl", "192.168.1.100")

# Creates:
# mojadomena.pl -> 192.168.1.100
# app.mojadomena.pl -> 192.168.1.100
# site.mojadomena.pl -> 192.168.1.100
# api.mojadomena.pl -> 192.168.1.100
```

### 📂 **Git Integration:**

```bash
# Clone and deploy in one go
pydock git clone https://github.com/user/repo.git
cd repo
pydock init mojadomena.pl 192.168.1.100
pydock deploy

# Validate repository
pydock git validate
# ✅ Repository is ready for deployment!
# 💡 Recommendations:
#   • Add .env.template for environment configuration
#   • Add Dockerfile for containerization
```

### 🔧 **Environment Management:**

```bash
# Initialize from template
pydock env init

# Show current values  
pydock env show

# In shell - set values
(pydock) env set CLOUDFLARE_API_TOKEN your-token
(pydock) env load .env.production
```

### 🎯 **Jak to wszystko działa razem:**

```bash
# 1. Setup Poetry project
poetry new my-app && cd my-app
poetry add pydock

# 2. Initialize environment
poetry run pydock env init
# Edit .env with your values

# 3. Interactive development
poetry run pydock shell
(pydock) git clone https://github.com/user/repo.git src
(pydock) init mojadomena.pl 192.168.1.100
(pydock) cloudflare setup  # Auto DNS
(pydock) generate app      # Sample apps
(pydock) deploy            # Deploy!

# 4. API server for automation
poetry run pydock api start &

# 5. Deploy via API (like dynapsys)
curl -X POST localhost:8000/deploy -d '{
  "domain": "newdomain.pl",
  "cf_token": "token",
  "source": "https://github.com/user/newrepo.git"
}'
```

### 📊 **Porównanie z dynapsys:**

| Feature | dynapsys | PyDock |
|---------|----------|---------|
| **Deployment API** | ✅ | ✅ FastAPI + WebSocket |
| **Git clone** | ✅ | ✅ + validation |
| **Cloudflare DNS** | ✅ | ✅ + zones management |
| **Poetry support** | ❌ | ✅ |
| **Interactive shell** | ❌ | ✅ Rich-based |
| **Environment config** | ❌ | ✅ Pydantic Settings |
| **Docker isolation** | ❌ | ✅ |
| **SSL automation** | ❌ | ✅ Caddy |
| **Real-time logs** | ❌ | ✅ WebSocket |

### 🔒 **Security & Production:**

```bash
# Production .env
PYDOCK_ENVIRONMENT=production
PYDOCK_API_SECRET_KEY=secure-generated-key
CLOUDFLARE_API_TOKEN=production-token
SSL_STAGING=false

# API authentication
curl -H "Authorization: Bearer $API_SECRET_KEY" \
     http://api.yourdomain.com/deploy
```

### 🎉 **Kompletny przykład użycia:**## 🎯 **Podsumowanie - PyDock ma wszystko czego potrzebujesz:**

### ✅ **Spełnione wymagania:**

1. **Poetry support** ✅ - `pyproject.toml` z pełną konfiguracją dependency
2. **Lokalne .env** ✅ - Pydantic Settings z auto-loadingiem  
3. **Interactive shell** ✅ - Rich-based shell z kolorami i tabelami
4. **FastAPI REST API** ✅ - Kompatybilne z dynapsys + więcej funkcji
5. **Cloudflare integration** ✅ - Automatyczne DNS jak w dynapsys

### 🚀 **Użycie identyczne jak dynapsys:**

```python
# Start deployment server (jak dynapsys)
from pydock.api import run_server
run_server(port=8000)

# Deploy via API (kompatybilne z dynapsys)
curl -X POST http://localhost:8000/deploy \
  -d '{
    "domain": "your-domain.com", 
    "cf_token": "cloudflare-token",
    "source": "https://github.com/user/repo.git"
  }'
```

### 🎁 **Bonus funkcje (których nie ma dynapsys):**

- 🐚 **Interactive shell** z Rich UI
- 🔧 **Environment management** z Pydantic 
- 📦 **Poetry integration** 
- 🐳 **Docker isolation** - nie zmienia lokalnego środowiska
- 🔒 **Automatic SSL** z Caddy
- 📊 **Real-time monitoring** przez WebSocket
- 📂 **Git validation** i project detection
- 🌊 **Streaming logs**

### 💎 **PyDock = dynapsys + modern Python tooling!**

Masz teraz kompletne narzędzie, które:
- **Nie modyfikuje** lokalnego środowiska (wszystko przez SSH + Docker)
- **Używa Poetry** do zarządzania dependencies  
- **Ma .env configuration** z Pydantic Settings
- **Oferuje interactive shell** z Rich UI
- **Zapewnia REST API** kompatybilne z dynapsys
- **Integruje z Cloudflare** automatycznie
- **Zarządza Git operations** z validation

To jest **znacznie bardziej zaawansowane** rozwiązanie niż dynapsys, zachowując przy tym prostotę użytkowania! 🎉



## 🏗️ Architektura

```
Lokalne środowisko (niezmienione)
     ↓ SSH Deploy
VPS z Docker Compose:
├── Caddy (Reverse Proxy + SSL)
├── Web App (Flask/FastAPI)  
├── Static Site (Nginx)
└── Database (PostgreSQL)
```

## 📦 Instalacja

```bash
# Zainstaluj PyDock
pip install pydock

# Lub z kodu źródłowego
git clone https://github.com/pydock/pydock.git
cd pydock
pip install -e .
```

## 🚀 Szybki start

### 1. Inicjalizacja projektu

```bash
# Utwórz nowy projekt PyDock
pydock init mojadomena.pl 192.168.1.100 --ssh-key ~/.ssh/id_rsa

# Struktura katalogów zostanie utworzona automatycznie:
# ├── pydock.json          # Konfiguracja
# ├── docker-compose.prod.yml  # Docker Compose dla produkcji
# ├── Caddyfile.prod       # Konfiguracja reverse proxy
# ├── web-app/             # Twoja aplikacja
# ├── static-site/         # Strona statyczna
# └── .pydock/             # Pliki wewnętrzne
```

### 2. Konfiguracja DNS

W panelu dostawcy domeny dodaj rekordy A:

```
Typ: A, Nazwa: @,    Wartość: IP_VPS
Typ: A, Nazwa: app,  Wartość: IP_VPS  
Typ: A, Nazwa: site, Wartość: IP_VPS
Typ: A, Nazwa: api,  Wartość: IP_VPS
```

### 3. Wygeneruj przykładowe aplikacje

```bash
# Wygeneruj aplikację Flask
pydock generate app

# Lub FastAPI
pydock generate api

# Lub stronę statyczną
pydock generate static
```

### 4. Deploy na VPS

```bash
# Wykonaj deployment
pydock deploy

# 🎉 Gotowe! Twoje aplikacje są dostępne:
# https://mojadomena.pl       - główna strona
# https://app.mojadomena.pl   - aplikacja
# https://site.mojadomena.pl  - strona statyczna
# https://api.mojadomena.pl   - API endpoint
```

## 🔧 Zarządzanie

### Status aplikacji
```bash
pydock status
```

### Logi
```bash
# Wszystkie logi
pydock logs

# Logi konkretnej usługi
pydock logs caddy
pydock logs web-app

# Śledzenie na żywo
pydock logs -f
```

### Zatrzymanie
```bash
pydock stop
```

### Aktualizacja
```bash
# Zmień kod lokalnie, potem:
pydock deploy  # Automatycznie zaktualizuje VPS
```

## 📋 Konfiguracja

### Plik `pydock.json`

```json
{
  "domain": "mojadomena.pl",
  "vps_ip": "192.168.1.100",
  "ssh_key_path": "~/.ssh/id_rsa",
  "services": {
    "web-app": {
      "subdomain": "app",
      "port": 5000,
      "build_path": "./web-app"
    },
    "static-site": {
      "subdomain": "site",
      "port": 80,
      "image": "nginx:alpine"
    },
    "database": {
      "internal": true,
      "port": 5432,
      "image": "postgres:15-alpine"
    }
  },
  "caddy": {
    "auto_ssl": true,
    "email": "admin@mojadomena.pl"
  }
}
```

### Zmienne środowiskowe

PyDock automatycznie generuje `.env` na VPS:

```env
DOMAIN=mojadomena.pl
DB_PASSWORD=automatycznie_wygenerowane_hasło
FLASK_ENV=production
```

## 🔒 Bezpieczeństwo

- **SSH Keys** - Uwierzytelnianie kluczami SSH
- **Isolacja** - Każda usługa w osobnym kontenerze
- **Firewall** - Tylko porty 80/443 otwarte publicznie
- **SSL** - Automatyczne certyfikaty Let's Encrypt
- **Passwords** - Cryptographically secure generated passwords

## 📊 Przykłady użycia

### Flask Application

```python
# web-app/app.py (automatycznie wygenerowane)
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "🐳 Deployed by PyDock!"

@app.route('/api/status')
def status():
    return {"status": "running", "deployed_by": "PyDock"}
```

### FastAPI Application

```python
# web-app/main.py
from fastapi import FastAPI

app = FastAPI(title="PyDock API")

@app.get("/")
async def root():
    return {"message": "🐳 Deployed by PyDock!"}
```

### Static Site

```html
<!-- static-site/index.html (automatycznie wygenerowane) -->
<!DOCTYPE html>
<html>
<head><title>PyDock Site</title></head>
<body>
    <h1>🐳 Deployed by PyDock!</h1>
    <p>SSL ✅ | Docker ✅ | Auto Deploy ✅</p>
</body>
</html>
```

## 🛠️ Dostosowanie

### Dodanie nowej usługi

1. Edytuj `pydock.json`:
```json
{
  "services": {
    "new-service": {
      "subdomain": "new",
      "port": 3000,
      "build_path": "./new-service"
    }
  }
}
```

2. Utwórz katalog `new-service/` z Dockerfile

3. Deploy: `pydock deploy`

### Custom Caddyfile

Edytuj `Caddyfile.prod` aby dodać:
- Basic auth
- Rate limiting  
- Custom headers
- Redirects

```
app.mojadomena.pl {
    reverse_proxy web-app:5000
    
    # Basic auth
    basicauth {
        admin $2a$14$hashed_password
    }
    
    # Rate limiting
    rate_limit {
        zone app {
            key {remote_host}
            events 100
            window 1m
        }
    }
}
```

## 🚨 Rozwiązywanie problemów

### SSL nie działa
```bash
# Sprawdź logi Caddy
pydock logs caddy

# Sprawdź DNS
dig app.mojadomena.pl
```

### Aplikacja nie odpowiada
```bash
# Sprawdź status kontenerów
pydock status

# Sprawdź logi aplikacji
pydock logs web-app
```

### Błąd połączenia SSH
```bash
# Test połączenia
ssh root@IP_VPS

# Sprawdź klucz SSH
ssh-add -l
```

## 🧑‍💻 Development

### Struktura projektu
```
pydock/
├── pydock/
│   ├── __init__.py
│   ├── core.py          # Główna logika
│   ├── config.py        # Zarządzanie konfiguracją  
│   ├── deployment.py    # Logika deploymentu
│   ├── utils.py         # Narzędzia pomocnicze
│   ├── cli.py           # Interfejs CLI
│   └── generators.py    # Generatory aplikacji
├── setup.py
├── requirements.txt
└── README.md
```

### Uruchomienie z kodu źródłowego
```bash
git clone https://github.com/pydock/pydock.git
cd pydock
pip install -e .
pydock --help
```

## 📝 Changelog

### v1.0.0
- ✨ Pierwsza wersja PyDock
- 🐳 Support dla Flask/FastAPI
- 🔒 Automatyczne SSL z Caddy
- 📊 CLI management interface
- 🚀 One-command deployment

## 🤝 Contributing

1. Fork projektu
2. Utwórz branch feature (`git checkout -b feature/AmazingFeature`)
3. Commit zmiany (`git commit -m 'Add AmazingFeature'`)
4. Push branch (`git push origin feature/AmazingFeature`)
5. Otwórz Pull Request

## 📄 Licencja

MIT License - zobacz [LICENSE](LICENSE) file.

## 🙏 Acknowledgments

- [Caddy](https://caddyserver.com/) - Amazing reverse proxy
- [Docker](https://docker.com/) - Container platform
- [Paramiko](https://www.paramiko.org/) - SSH library
- [Click](https://click.palletsprojects.com/) - CLI framework

---

**PyDock** - Deploy applications without the hassle! 🚀



## 🎉 **PyDock - Kompletna wersja z wszystkimi funkcjami!**

Rozszerzyłem PyDock o wszystkie funkcje, o które pytałeś:

### ✨ **Nowe funkcje:**

1. **🎯 Poetry support** - `pyproject.toml` z pełną konfiguracją
2. **🔧 .env configuration** - Pydantic Settings z automatycznym ładowaniem
3. **🐚 Interactive Shell** - Rich-based shell z kolorami i tabelami
4. **🚀 FastAPI REST API** - Kompletne API z WebSocket, deployment endpoints
5. **☁️ Cloudflare integration** - Automatyczne DNS, zone management
6. **📂 Git operations** - Clone, validate, project detection

### 📦 **Jak używać z Poetry:**

```bash
# 1. Instalacja z Poetry
poetry install

# 2. Aktywacja środowiska
poetry shell

# 3. Inicjalizacja .env
pydock env init

# 4. Edytuj .env z Twoimi wartościami
nano .env

# 5. Inicjalizacja projektu
pydock init mojadomena.pl 192.168.1.100

# 6. Interaktywny shell
pydock shell

# 7. Start API server
pydock api start

# 8. Deploy
pydock deploy
```

### 🔧 **Konfiguracja .env:**

```bash
# Core
PYDOCK_DOMAIN=mojadomena.pl
PYDOCK_VPS_IP=192.168.1.100
CLOUDFLARE_API_TOKEN=your-token

# API Server
PYDOCK_API_PORT=8000
PYDOCK_API_SECRET_KEY=auto-generated

# Features
CLOUDFLARE_AUTO_DNS=true
FEATURE_WEBSOCKET_LOGS=true
```


