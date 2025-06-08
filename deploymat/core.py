import os
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional
import paramiko
from .config import Config
from .deployment import Deployment
from .utils import Logger


class PyDockManager:
    """Główna klasa zarządzająca deploymentem Docker Compose na VPS"""

    def __init__(self, config_file: str = "pydock.json"):
        """
        Inicjalizuje PyDock Manager

        Args:
            config_file: Ścieżka do pliku konfiguracyjnego
        """
        self.logger = Logger()
        self.config = Config(config_file)
        self.deployment = None

    def init_project(self, domain: str, vps_ip: str, ssh_key_path: str = None):
        """
        Inicjalizuje nowy projekt PyDock

        Args:
            domain: Domena główna (np. mojadomena.pl)
            vps_ip: IP adres VPS
            ssh_key_path: Ścieżka do klucza SSH (opcjonalne)
        """
        self.logger.info("🚀 Inicjalizacja nowego projektu PyDock...")

        # Utwórz strukturę katalogów
        self._create_project_structure()

        # Generuj konfigurację
        config_data = {
            "domain": domain,
            "vps_ip": vps_ip,
            "ssh_key_path": ssh_key_path,
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
                    "internal": True,
                    "port": 5432,
                    "image": "postgres:15-alpine"
                }
            },
            "caddy": {
                "auto_ssl": True,
                "email": f"admin@{domain}"
            }
        }

        # Zapisz konfigurację
        self.config.save(config_data)

        # Generuj pliki Docker Compose
        self._generate_docker_files()

        self.logger.success(f"✅ Projekt zainicjalizowany dla domeny: {domain}")

    def deploy(self, environment: str = "production"):
        """
        Wykonuje deployment na VPS

        Args:
            environment: Środowisko docelowe (production/staging)
        """
        self.logger.info(f"🚀 Rozpoczynam deployment na {environment}...")

        if not self.config.exists():
            raise Exception("❌ Nie znaleziono konfiguracji. Uruchom najpierw 'pydock init'")

        config_data = self.config.load()
        self.deployment = Deployment(config_data, self.logger)

        try:
            # 1. Sprawdź połączenie VPS
            self.deployment.test_connection()

            # 2. Sprawdź DNS
            self.deployment.check_dns()

            # 3. Przygotuj pliki na VPS
            self.deployment.prepare_vps()

            # 4. Uruchom Docker Compose
            self.deployment.deploy_containers()

            # 5. Sprawdź status
            self.deployment.verify_deployment()

            self.logger.success("🎉 Deployment zakończony pomyślnie!")

        except Exception as e:
            self.logger.error(f"❌ Błąd podczas deploymentu: {str(e)}")
            raise

    def status(self):
        """Sprawdza status aplikacji na VPS"""
        if not self.config.exists():
            self.logger.error("❌ Brak konfiguracji projektu")
            return

        config_data = self.config.load()
        self.deployment = Deployment(config_data, self.logger)

        try:
            self.deployment.show_status()
        except Exception as e:
            self.logger.error(f"❌ Nie można sprawdzić statusu: {str(e)}")

    def logs(self, service: str = None, follow: bool = False):
        """
        Pokazuje logi z VPS

        Args:
            service: Nazwa usługi (opcjonalne)
            follow: Czy śledzić logi na żywo
        """
        if not self.config.exists():
            self.logger.error("❌ Brak konfiguracji projektu")
            return

        config_data = self.config.load()
        self.deployment = Deployment(config_data, self.logger)

        try:
            self.deployment.show_logs(service, follow)
        except Exception as e:
            self.logger.error(f"❌ Nie można pobrać logów: {str(e)}")

    def stop(self):
        """Zatrzymuje aplikację na VPS"""
        if not self.config.exists():
            self.logger.error("❌ Brak konfiguracji projektu")
            return

        config_data = self.config.load()
        self.deployment = Deployment(config_data, self.logger)

        try:
            self.deployment.stop_containers()
            self.logger.success("✅ Aplikacja zatrzymana")
        except Exception as e:
            self.logger.error(f"❌ Błąd podczas zatrzymywania: {str(e)}")

    def _create_project_structure(self):
        """Tworzy strukturę katalogów projektu"""
        directories = [
            "web-app",
            "static-site",
            "configs",
            "deployments",
            ".pydock"
        ]

        for directory in directories:
            Path(directory).mkdir(exist_ok=True)

        self.logger.info("📁 Utworzono strukturę katalogów")

    def _generate_docker_files(self):
        """Generuje pliki Docker Compose i Caddyfile"""
        config_data = self.config.load()

        # Generuj docker-compose.prod.yml
        compose_content = self._generate_compose_file(config_data)

        with open("docker-compose.prod.yml", "w") as f:
            f.write(compose_content)

        # Generuj Caddyfile
        caddyfile_content = self._generate_caddyfile(config_data)

        with open("Caddyfile.prod", "w") as f:
            f.write(caddyfile_content)

        self.logger.info("📝 Wygenerowano pliki Docker Compose")

    def _generate_compose_file(self, config: Dict) -> str:
        """Generuje zawartość docker-compose.prod.yml"""
        return f"""version: '3.8'

services:
  # Caddy Reverse Proxy z automatycznym SSL
  caddy:
    image: caddy:2-alpine
    container_name: caddy
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile.prod:/etc/caddy/Caddyfile
      - caddy_data:/data
      - caddy_config:/config
    networks:
      - app-network
    depends_on:
      - web-app
      - static-site

  # Web Application
  web-app:
    build: ./web-app
    container_name: web-app
    hostname: web-app
    restart: unless-stopped
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://admin:${{DB_PASSWORD}}@database:5432/myapp
    networks:
      - app-network
    depends_on:
      - database

  # Static Site
  static-site:
    image: nginx:alpine
    container_name: static-site
    hostname: static-site
    restart: unless-stopped
    volumes:
      - ./static-site:/usr/share/nginx/html:ro
    networks:
      - app-network

  # Database
  database:
    image: postgres:15-alpine
    container_name: database
    hostname: database
    restart: unless-stopped
    environment:
      - POSTGRES_DB=myapp
      - POSTGRES_USER=admin
      - POSTGRES_PASSWORD=${{DB_PASSWORD}}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app-network

networks:
  app-network:
    driver: bridge

volumes:
  postgres_data:
  caddy_data:
  caddy_config:
"""

    def _generate_caddyfile(self, config: Dict) -> str:
        """Generuje zawartość Caddyfile.prod"""
        domain = config['domain']

        return f"""# Caddyfile dla domeny: {domain}
# Automatyczne SSL certificates przez Let's Encrypt

# Web Application
app.{domain} {{
    reverse_proxy web-app:5000

    log {{
        output file /var/log/caddy/app.log
    }}
}}

# Static Site
site.{domain} {{
    reverse_proxy static-site:80

    log {{
        output file /var/log/caddy/site.log
    }}
}}

# API Endpoint
api.{domain} {{
    reverse_proxy web-app:5000/api

    # Rate limiting
    rate_limit {{
        zone api {{
            key {{remote_host}}
            events 100
            window 1m
        }}
    }}
}}

# Main domain redirect
{domain} {{
    redir https://site.{domain}{{uri}} permanent
}}

# WWW redirect
www.{domain} {{
    redir https://{domain}{{uri}} permanent
}}
"""