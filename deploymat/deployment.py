import os
import time
import socket
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
import paramiko
from .utils import Logger


class Deployment:
    """Klasa zarządzająca deploymentem na VPS"""

    def __init__(self, config: Dict, logger: Logger):
        """
        Inicjalizuje deployment

        Args:
            config: Konfiguracja projektu
            logger: Logger do wyświetlania komunikatów
        """
        self.config = config
        self.logger = logger
        self.ssh_client = None
        self.project_name = "pydock-app"

    def test_connection(self):
        """Testuje połączenie SSH z VPS"""
        self.logger.info("🔌 Testowanie połączenia z VPS...")

        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Próbuj różne metody uwierzytelniania
            vps_ip = self.config['vps_ip']
            ssh_key_path = self.config.get('ssh_key_path')

            if ssh_key_path and os.path.exists(ssh_key_path):
                # Uwierzytelnianie kluczem SSH
                self.ssh_client.connect(
                    hostname=vps_ip,
                    username='root',
                    key_filename=ssh_key_path,
                    timeout=10
                )
            else:
                # Uwierzytelnianie hasłem (poprosi o hasło)
                password = input(f"Podaj hasło dla root@{vps_ip}: ")
                self.ssh_client.connect(
                    hostname=vps_ip,
                    username='root',
                    password=password,
                    timeout=10
                )

            self.logger.success("✅ Połączenie z VPS nawiązane")

        except Exception as e:
            self.logger.error(f"❌ Nie można połączyć się z VPS: {str(e)}")
            raise

    def check_dns(self):
        """Sprawdza konfigurację DNS"""
        self.logger.info("🌐 Sprawdzanie konfiguracji DNS...")

        domain = self.config['domain']
        vps_ip = self.config['vps_ip']

        subdomains = ['app', 'site', 'api', 'www']
        dns_ok = True

        for subdomain in subdomains:
            full_domain = f"{subdomain}.{domain}"

            try:
                resolved_ip = socket.gethostbyname(full_domain)
                if resolved_ip == vps_ip:
                    self.logger.success(f"✅ {full_domain} → {resolved_ip}")
                else:
                    self.logger.warning(f"⚠️  {full_domain} → {resolved_ip} (oczekiwano {vps_ip})")
                    dns_ok = False
            except socket.gaierror:
                self.logger.warning(f"⚠️  {full_domain} → nie rozwiązano")
                dns_ok = False

        # Sprawdź główną domenę
        try:
            resolved_ip = socket.gethostbyname(domain)
            if resolved_ip == vps_ip:
                self.logger.success(f"✅ {domain} → {resolved_ip}")
            else:
                self.logger.warning(f"⚠️  {domain} → {resolved_ip} (oczekiwano {vps_ip})")
                dns_ok = False
        except socket.gaierror:
            self.logger.warning(f"⚠️  {domain} → nie rozwiązano")
            dns_ok = False

        if not dns_ok:
            self.logger.warning("⚠️  Niektóre domeny nie wskazują na VPS. Deployment może nie działać poprawnie.")
            response = input("Czy chcesz kontynuować? (y/N): ")
            if response.lower() != 'y':
                raise Exception("Deployment anulowany przez użytkownika")

    def prepare_vps(self):
        """Przygotowuje VPS do deploymentu"""
        self.logger.info("🔧 Przygotowywanie VPS...")

        # Instaluj Docker jeśli nie ma
        self._run_command("which docker || curl -fsSL https://get.docker.com | sh")
        self._run_command(
            "which docker-compose || curl -L \"https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)\" -o /usr/local/bin/docker-compose && chmod +x /usr/local/bin/docker-compose")

        # Utwórz katalog projektu
        self._run_command(f"mkdir -p /opt/{self.project_name}")

        # Prześlij pliki
        self._upload_files()

        # Wygeneruj .env z hasłami
        self._generate_env_file()

        self.logger.success("✅ VPS przygotowany")

    def deploy_containers(self):
        """Uruchamia kontenery Docker na VPS"""
        self.logger.info("🚀 Uruchamianie kontenerów...")

        project_dir = f"/opt/{self.project_name}"

        # Zatrzymaj stare kontenery
        self._run_command(f"cd {project_dir} && docker-compose -f docker-compose.prod.yml down || true")

        # Uruchom nowe
        self._run_command(f"cd {project_dir} && docker-compose -f docker-compose.prod.yml up -d --build")

        # Poczekaj na uruchomienie
        time.sleep(10)

        self.logger.success("✅ Kontenery uruchomione")

    def verify_deployment(self):
        """Weryfikuje czy deployment się powiódł"""
        self.logger.info("🔍 Weryfikacja deploymentu...")

        project_dir = f"/opt/{self.project_name}"

        # Sprawdź status kontenerów
        stdout, stderr = self._run_command(f"cd {project_dir} && docker-compose -f docker-compose.prod.yml ps")

        self.logger.info("📊 Status kontenerów:")
        print(stdout)

        # Sprawdź logi Caddy
        stdout, stderr = self._run_command(
            f"cd {project_dir} && docker-compose -f docker-compose.prod.yml logs caddy | tail -5")

        if "certificate obtained successfully" in stdout.lower() or "serving" in stdout.lower():
            self.logger.success("✅ SSL certyfikaty wygenerowane")
        else:
            self.logger.warning("⚠️  SSL certyfikaty mogą być jeszcze generowane...")

        # Pokaż dostępne adresy
        domain = self.config['domain']
        self.logger.info("🌐 Twoja aplikacja jest dostępna pod adresami:")
        self.logger.info(f"   Główna strona:    https://{domain}")
        self.logger.info(f"   Aplikacja:        https://app.{domain}")
        self.logger.info(f"   Strona statyczna: https://site.{domain}")
        self.logger.info(f"   API:              https://api.{domain}")

    def show_status(self):
        """Pokazuje aktualny status aplikacji"""
        project_dir = f"/opt/{self.project_name}"

        self.logger.info("📊 Status aplikacji:")
        stdout, stderr = self._run_command(f"cd {project_dir} && docker-compose -f docker-compose.prod.yml ps")
        print(stdout)

    def show_logs(self, service: str = None, follow: bool = False):
        """
        Pokazuje logi aplikacji

        Args:
            service: Nazwa usługi
            follow: Czy śledzić logi na żywo
        """
        project_dir = f"/opt/{self.project_name}"

        if service:
            cmd = f"cd {project_dir} && docker-compose -f docker-compose.prod.yml logs {service}"
        else:
            cmd = f"cd {project_dir} && docker-compose -f docker-compose.prod.yml logs"

        if follow:
            cmd += " -f"

        stdout, stderr = self._run_command(cmd)
        print(stdout)

    def stop_containers(self):
        """Zatrzymuje kontenery"""
        project_dir = f"/opt/{self.project_name}"
        self._run_command(f"cd {project_dir} && docker-compose -f docker-compose.prod.yml down")

    def _run_command(self, command: str) -> tuple:
        """
        Wykonuje komendę na VPS przez SSH

        Args:
            command: Komenda do wykonania

        Returns:
            Tuple (stdout, stderr)
        """
        if not self.ssh_client:
            raise Exception("Brak połączenia SSH")

        stdin, stdout, stderr = self.ssh_client.exec_command(command)
        stdout_text = stdout.read().decode('utf-8')
        stderr_text = stderr.read().decode('utf-8')

        if stderr_text and "warning" not in stderr_text.lower():
            self.logger.debug(f"Command: {command}")
            self.logger.debug(f"STDERR: {stderr_text}")

        return stdout_text, stderr_text

    def _upload_files(self):
        """Przesyła pliki projektu na VPS"""
        self.logger.info("📁 Przesyłanie plików...")

        sftp = self.ssh_client.open_sftp()
        project_dir = f"/opt/{self.project_name}"

        # Lista plików do przesłania
        files_to_upload = [
            "docker-compose.prod.yml",
            "Caddyfile.prod",
        ]

        # Przesyłaj pliki
        for file_path in files_to_upload:
            if os.path.exists(file_path):
                remote_path = f"{project_dir}/{file_path}"
                sftp.put(file_path, remote_path)
                self.logger.debug(f"Przesłano: {file_path}")

        # Przesyłaj katalogi
        directories_to_upload = ["web-app", "static-site"]

        for directory in directories_to_upload:
            if os.path.exists(directory):
                self._upload_directory(sftp, directory, f"{project_dir}/{directory}")

        sftp.close()
        self.logger.success("✅ Pliki przesłane")

    def _upload_directory(self, sftp, local_dir: str, remote_dir: str):
        """Przesyła katalog rekurencyjnie"""
        try:
            sftp.mkdir(remote_dir)
        except:
            pass  # Katalog już istnieje

        for item in os.listdir(local_dir):
            local_path = os.path.join(local_dir, item)
            remote_path = f"{remote_dir}/{item}"

            if os.path.isfile(local_path):
                sftp.put(local_path, remote_path)
            elif os.path.isdir(local_path):
                self._upload_directory(sftp, local_path, remote_path)

    def _generate_env_file(self):
        """Generuje plik .env z bezpiecznymi hasłami"""
        import secrets
        import string

        # Wygeneruj bezpieczne hasło
        alphabet = string.ascii_letters + string.digits
        db_password = ''.join(secrets.choice(alphabet) for _ in range(32))

        env_content = f"""# Wygenerowane automatycznie przez PyDock
DOMAIN={self.config['domain']}
DB_PASSWORD={db_password}
FLASK_ENV=production
"""

        project_dir = f"/opt/{self.project_name}"

        # Utwórz plik .env na VPS
        stdin, stdout, stderr = self.ssh_client.exec_command(f"cat > {project_dir}/.env << 'EOF'\n{env_content}\nEOF")

        self.logger.success("✅ Plik .env wygenerowany")

    def __del__(self):
        """Zamyka połączenie SSH"""
        if self.ssh_client:
            self.ssh_client.close()