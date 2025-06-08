#!/usr/bin/env python3
"""
Przykład użycia PyDock - Python Docker Deployment Manager

Ten skrypt pokazuje jak używać PyDock programmatycznie
oraz demonstruje wszystkie główne funkcje.
"""

import sys
import os
from pathlib import Path

# Dodaj PyDock do ścieżki (jeśli nie zainstalowany przez pip)
sys.path.insert(0, str(Path(__file__).parent))

from pydock import PyDockManager, Logger


def main():
    """Główna funkcja demonstracyjna"""

    # Inicjalizuj logger
    logger = Logger(verbose=True)
    logger.header("🐳 PyDock - Przykład użycia")

    # Konfiguracja
    DOMAIN = "example.com"  # 🔧 ZMIEŃ NA SWOJĄ DOMENĘ
    VPS_IP = "192.168.1.100"  # 🔧 ZMIEŃ NA IP SWOJEGO VPS
    SSH_KEY = "~/.ssh/id_rsa"  # 🔧 ZMIEŃ NA ŚCIEŻKĘ DO KLUCZA SSH

    try:
        # === KROK 1: Inicjalizacja projektu ===
        logger.info("📋 Krok 1: Inicjalizacja nowego projektu PyDock")

        manager = PyDockManager("example-pydock.json")

        # Sprawdź czy projekt już istnieje
        if manager.config.exists():
            logger.warning("⚠️  Projekt już istnieje. Używam istniejącej konfiguracji.")
        else:
            logger.info(f"🚀 Tworzę nowy projekt dla domeny: {DOMAIN}")
            manager.init_project(
                domain=DOMAIN,
                vps_ip=VPS_IP,
                ssh_key_path=SSH_KEY
            )
            logger.success("✅ Projekt zainicjalizowany!")

        # === KROK 2: Generowanie przykładowych aplikacji ===
        logger.info("📋 Krok 2: Generowanie przykładowych aplikacji")

        from pydock.generators import generate_sample_app

        # Wygeneruj Flask app
        if not Path("web-app").exists():
            logger.info("🐍 Generuję przykładową aplikację Flask...")
            generate_sample_app('flask')
            logger.success("✅ Aplikacja Flask wygenerowana!")

        # Wygeneruj static site
        if not Path("static-site").exists():
            logger.info("📄 Generuję przykładową stronę statyczną...")
            generate_sample_app('static')
            logger.success("✅ Strona statyczna wygenerowana!")

        # === KROK 3: Walidacja konfiguracji ===
        logger.info("📋 Krok 3: Walidacja konfiguracji")

        if manager.config.validate():
            logger.success("✅ Konfiguracja jest poprawna")
        else:
            logger.error("❌ Błędna konfiguracja!")
            return 1

        # Wyświetl konfigurację
        config = manager.config.load()
        logger.info("📄 Aktualna konfiguracja:")
        logger.info(f"   Domena: {config['domain']}")
        logger.info(f"   VPS IP: {config['vps_ip']}")
        logger.info(f"   Usługi: {len(config['services'])}")

        # === KROK 4: Symulacja deploymentu ===
        logger.info("📋 Krok 4: Przygotowanie do deploymentu")

        logger.warning("⚠️  UWAGA: To jest przykład demonstracyjny!")
        logger.warning("   Rzeczywisty deployment wymaga:")
        logger.warning("   1. Działającego VPS z SSH")
        logger.warning("   2. Skonfigurowanego DNS")
        logger.warning("   3. Dostępu do internetu")

        # Sprawdź czy użytkownik chce kontynuować
        try:
            response = input("\n🤔 Czy chcesz kontynuować rzeczywisty deployment? (y/N): ")
            if response.lower() == 'y':
                logger.info("🚀 Rozpoczynam rzeczywisty deployment...")

                # === RZECZYWISTY DEPLOYMENT ===
                manager.deploy()

                logger.success("🎉 Deployment zakończony pomyślnie!")
                logger.info("🌐 Twoje aplikacje są dostępne pod adresami:")
                logger.info(f"   Główna strona:    https://{DOMAIN}")
                logger.info(f"   Aplikacja:        https://app.{DOMAIN}")
                logger.info(f"   Strona statyczna: https://site.{DOMAIN}")
                logger.info(f"   API:              https://api.{DOMAIN}")

            else:
                logger.info("📋 Deployment anulowany. Struktura plików gotowa do użycia.")

        except KeyboardInterrupt:
            logger.warning("\n⚠️  Przerwano przez użytkownika")

        # === KROK 5: Demonstracja zarządzania ===
        logger.info("📋 Krok 5: Dostępne komendy zarządzania")

        commands = [
            ("pydock status", "Sprawdź status aplikacji"),
            ("pydock logs", "Wyświetl logi wszystkich usług"),
            ("pydock logs caddy", "Logi reverse proxy"),
            ("pydock logs web-app", "Logi aplikacji"),
            ("pydock deploy", "Zaktualizuj aplikację"),
            ("pydock stop", "Zatrzymaj wszystkie usługi")
        ]

        logger.info("💻 Możesz teraz używać poniższych komend:")
        for cmd, desc in commands:
            logger.info(f"   {cmd:<20} - {desc}")

        # === PODSUMOWANIE ===
        logger.header("📋 Podsumowanie")

        logger.info("🎯 Struktura projektu została utworzona:")
        logger.info("   ├── example-pydock.json    # Konfiguracja PyDock")
        logger.info("   ├── docker-compose.prod.yml # Docker Compose dla VPS")
        logger.info("   ├── Caddyfile.prod         # Konfiguracja Caddy")
        logger.info("   ├── web-app/               # Aplikacja Flask")
        logger.info("   │   ├── app.py")
        logger.info("   │   ├── requirements.txt")
        logger.info("   │   └── Dockerfile")
        logger.info("   ├── static-site/           # Strona statyczna")
        logger.info("   │   ├── index.html")
        logger.info("   │   └── style.css")
        logger.info("   └── .pydock/               # Pliki wewnętrzne")

        logger.success("✅ Przykład zakończony pomyślnie!")
        logger.info("📖 Więcej informacji: https://github.com/pydock/pydock")

        return 0

    except Exception as e:
        logger.error(f"❌ Błąd podczas wykonywania przykładu: {str(e)}")
        return 1


def demo_programmatic_usage():
    """Demonstracja użycia programistycznego PyDock"""

    logger = Logger()
    logger.header("🐍 Użycie programistyczne PyDock")

    # Utwórz manager
    manager = PyDockManager("demo-config.json")

    # Załaduj lub utwórz konfigurację
    if not manager.config.exists():
        logger.info("📝 Tworzę przykładową konfigurację...")

        config_data = {
            "domain": "demo.example.com",
            "vps_ip": "192.168.1.100",
            "ssh_key_path": "~/.ssh/id_rsa",
            "services": {
                "web-app": {
                    "subdomain": "app",
                    "port": 5000,
                    "build_path": "./web-app"
                },
                "api": {
                    "subdomain": "api",
                    "port": 8000,
                    "build_path": "./api-service"
                },
                "frontend": {
                    "subdomain": "www",
                    "port": 3000,
                    "build_path": "./frontend"
                }
            }
        }

        manager.config.save(config_data)
        logger.success("✅ Konfiguracja utworzona")

    # Operacje na konfiguracji
    config = manager.config.load()
    logger.info(f"📄 Loaded config for domain: {config['domain']}")

    # Aktualizacja konfiguracji
    manager.config.update({
        "updated_at": "2024-01-01T12:00:00Z",
        "version": "1.0.0"
    })

    # Walidacja
    if manager.config.validate():
        logger.success("✅ Konfiguracja poprawna")

    # Lista deploymentów
    deployments = manager.config.list_deployments()
    logger.info(f"📦 Dostępne deploymenty: {deployments}")


def demo_advanced_features():
    """Demonstracja zaawansowanych funkcji"""

    logger = Logger()
    logger.header("🚀 Zaawansowane funkcje PyDock")

    # Import narzędzi
    from pydock.utils import NetworkUtils, SecurityUtils, FileUtils

    # === Narzędzia sieciowe ===
    logger.info("🌐 Test narzędzi sieciowych:")

    # Sprawdź czy domena jest dostępna
    ip = NetworkUtils.resolve_domain("google.com")
    if ip:
        logger.success(f"✅ google.com → {ip}")

    # Sprawdź port
    if NetworkUtils.check_port("google.com", 80):
        logger.success("✅ Port 80 otwarty na google.com")

    # === Narzędzia bezpieczeństwa ===
    logger.info("🔒 Generowanie bezpiecznych haseł:")

    password = SecurityUtils.generate_password(16)
    logger.info(f"🔑 Hasło: {password[:8]}...")

    secret = SecurityUtils.generate_secret_key(32)
    logger.info(f"🗝️  Secret key: {secret[:16]}...")

    # === Narzędzia plikowe ===
    logger.info("📁 Demonstracja narzędzi plikowych:")

    # Struktura katalogów
    test_structure = {
        "test-project": {
            "src": {
                "main.py": "# Main application\nprint('Hello PyDock!')",
                "config.json": '{"test": true}'
            },
            "docs": {
                "README.md": "# Test Project\n\nGenerated by PyDock"
            }
        }
    }

    try:
        FileUtils.create_directory_structure("/tmp", test_structure)
        logger.success("✅ Struktura testowa utworzona w /tmp")
    except Exception as e:
        logger.warning(f"⚠️  Nie można utworzyć struktury: {e}")


def demo_docker_utils():
    """Demonstracja narzędzi Docker"""

    logger = Logger()
    logger.header("🐳 Narzędzia Docker")

    from pydock.utils import DockerUtils

    # Generowanie sekcji service
    service_config = {
        "image": "nginx:alpine",
        "environment": ["ENV=production", "PORT=80"],
        "volumes": ["./html:/usr/share/nginx/html:ro"],
        "depends_on": ["database"]
    }

    service_yaml = DockerUtils.generate_compose_service("web-server", service_config)

    logger.info("📝 Wygenerowana sekcja Docker Compose:")
    print("\n" + service_yaml)


def create_full_example_project():
    """Tworzy kompletny przykładowy projekt"""

    logger = Logger()
    logger.header("📁 Tworzenie kompletnego przykładu")

    # Struktura kompletnego projektu
    project_structure = {
        "my-pydock-project": {
            "pydock.json": """{
  "domain": "myapp.example.com",
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
    "email": "admin@myapp.example.com"
  }
}""",
            "web-app": {
                "app.py": """from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <h1>🐳 PyDock Example App</h1>
    <p>Successfully deployed!</p>
    <p><a href="/api/status">API Status</a></p>
    '''

@app.route('/api/status')
def status():
    return jsonify({
        'service': 'example-app',
        'status': 'running',
        'deployed_by': 'PyDock'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
""",
                "requirements.txt": "Flask==2.3.3\ngunicorn==21.2.0",
                "Dockerfile": """FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app.py .
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
"""
            },
            "static-site": {
                "index.html": """<!DOCTYPE html>
<html>
<head>
    <title>PyDock Example</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; text-align: center; }
        .container { max-width: 600px; margin: 0 auto; }
        h1 { color: #333; }
        .status { color: #28a745; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🐳 PyDock Static Site</h1>
        <p class="status">✅ Successfully deployed with PyDock!</p>
        <p>This static site is served by Nginx with automatic SSL.</p>
    </div>
</body>
</html>
"""
            },
            "README.md": """# PyDock Example Project

This is a complete example project created by PyDock.

## Usage

1. **Configure DNS**: Point your domain to VPS IP
2. **Deploy**: Run `pydock deploy`
3. **Manage**: Use `pydock status`, `pydock logs`, etc.

## Services

- **Web App**: Flask application at https://app.example.com
- **Static Site**: Nginx site at https://site.example.com  
- **Database**: PostgreSQL (internal)

## Commands

```bash
pydock deploy     # Deploy to VPS
pydock status     # Check status
pydock logs       # View logs
pydock stop       # Stop services
```
""",
            "deploy.sh": """#!/bin/bash
# Quick deployment script

echo "🚀 PyDock Example Deployment"
echo "============================="

# Check if pydock is installed
if ! command -v pydock &> /dev/null; then
    echo "❌ PyDock not installed. Install with: pip install pydock"
    exit 1
fi

# Check if config exists
if [ ! -f "pydock.json" ]; then
    echo "❌ No pydock.json found. Run 'pydock init' first."
    exit 1
fi

# Deploy
echo "🚀 Starting deployment..."
pydock deploy

echo "✅ Deployment completed!"
"""
        }
    }

    try:
        from pydock.utils import FileUtils
        FileUtils.create_directory_structure(".", project_structure)

        # Make deploy script executable
        import stat
        os.chmod("my-pydock-project/deploy.sh",
                 os.stat("my-pydock-project/deploy.sh").st_mode | stat.S_IEXEC)

        logger.success("✅ Kompletny przykładowy projekt utworzony w: my-pydock-project/")
        logger.info("📋 Następne kroki:")
        logger.info("   1. cd my-pydock-project")
        logger.info("   2. Edytuj pydock.json (zmień domenę i IP)")
        logger.info("   3. pydock deploy")

    except Exception as e:
        logger.error(f"❌ Błąd tworzenia projektu: {e}")


if __name__ == "__main__":
    """Uruchom wszystkie demonstracje"""

    print("🐳 PyDock - Python Docker Deployment Manager")
    print("=" * 50)
    print()
    print("Wybierz demonstrację:")
    print("1. Kompletny przykład użycia")
    print("2. Użycie programistyczne")
    print("3. Zaawansowane funkcje")
    print("4. Narzędzia Docker")
    print("5. Utwórz przykładowy projekt")
    print("0. Wszystkie demonstracje")
    print()

    try:
        choice = input("Twój wybór (0-5): ").strip()

        if choice == "1":
            sys.exit(main())
        elif choice == "2":
            demo_programmatic_usage()
        elif choice == "3":
            demo_advanced_features()
        elif choice == "4":
            demo_docker_utils()
        elif choice == "5":
            create_full_example_project()
        elif choice == "0":
            main()
            demo_programmatic_usage()
            demo_advanced_features()
            demo_docker_utils()
            create_full_example_project()
        else:
            print("❌ Nieprawidłowy wybór")

    except KeyboardInterrupt:
        print("\n👋 Do widzenia!")
    except Exception as e:
        print(f"❌ Błąd: {e}")
        sys.exit(1)