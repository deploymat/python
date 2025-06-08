import sys
import time
from datetime import datetime
from typing import Optional


class Logger:
    """Klasa do kolorowego logowania komunikatów"""

    # Kody kolorów ANSI
    COLORS = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'reset': '\033[0m',
        'bold': '\033[1m'
    }

    def __init__(self, verbose: bool = True):
        """
        Inicjalizuje logger

        Args:
            verbose: Czy wyświetlać szczegółowe komunikaty
        """
        self.verbose = verbose

    def _log(self, level: str, message: str, color: str = 'white'):
        """
        Wewnętrzna metoda logowania

        Args:
            level: Poziom logowania
            message: Wiadomość do wyświetlenia
            color: Kolor tekstu
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        colored_message = f"{self.COLORS[color]}{message}{self.COLORS['reset']}"
        print(f"[{timestamp}] {colored_message}")

    def info(self, message: str):
        """Wyświetla informację"""
        self._log("INFO", message, "blue")

    def success(self, message: str):
        """Wyświetla komunikat o sukcesie"""
        self._log("SUCCESS", message, "green")

    def warning(self, message: str):
        """Wyświetla ostrzeżenie"""
        self._log("WARNING", message, "yellow")

    def error(self, message: str):
        """Wyświetla błąd"""
        self._log("ERROR", message, "red")

    def debug(self, message: str):
        """Wyświetla debug (tylko w trybie verbose)"""
        if self.verbose:
            self._log("DEBUG", message, "magenta")

    def header(self, message: str):
        """Wyświetla nagłówek"""
        separator = "=" * 50
        print(f"\n{self.COLORS['cyan']}{self.COLORS['bold']}{separator}")
        print(f"{message}")
        print(f"{separator}{self.COLORS['reset']}\n")

    def progress(self, message: str, duration: int = 3):
        """
        Wyświetla pasek postępu

        Args:
            message: Wiadomość do wyświetlenia
            duration: Czas trwania w sekundach
        """
        print(f"{message} ", end="")
        for i in range(duration):
            print(".", end="", flush=True)
            time.sleep(1)
        print(" ✅")


class DockerUtils:
    """Narzędzia do pracy z Docker"""

    @staticmethod
    def generate_compose_service(name: str, config: dict) -> str:
        """
        Generuje sekcję service dla docker-compose

        Args:
            name: Nazwa usługi
            config: Konfiguracja usługi

        Returns:
            Tekst YAML dla usługi
        """
        service_yaml = f"  {name}:\n"

        if 'image' in config:
            service_yaml += f"    image: {config['image']}\n"
        elif 'build' in config:
            service_yaml += f"    build: {config['build']}\n"

        service_yaml += f"    container_name: {name}\n"
        service_yaml += f"    hostname: {name}\n"
        service_yaml += "    restart: unless-stopped\n"

        if 'environment' in config:
            service_yaml += "    environment:\n"
            for env_var in config['environment']:
                service_yaml += f"      - {env_var}\n"

        if 'volumes' in config:
            service_yaml += "    volumes:\n"
            for volume in config['volumes']:
                service_yaml += f"      - {volume}\n"

        if 'depends_on' in config:
            service_yaml += "    depends_on:\n"
            for dep in config['depends_on']:
                service_yaml += f"      - {dep}\n"

        service_yaml += "    networks:\n      - app-network\n"

        return service_yaml

    @staticmethod
    def validate_compose_file(file_path: str) -> bool:
        """
        Waliduje plik docker-compose

        Args:
            file_path: Ścieżka do pliku

        Returns:
            True jeśli plik jest poprawny
        """
        try:
            import yaml
            with open(file_path, 'r') as f:
                yaml.safe_load(f)
            return True
        except Exception:
            return False


class NetworkUtils:
    """Narzędzia sieciowe"""

    @staticmethod
    def check_port(host: str, port: int, timeout: int = 5) -> bool:
        """
        Sprawdza czy port jest otwarty

        Args:
            host: Adres hosta
            port: Numer portu
            timeout: Timeout w sekundach

        Returns:
            True jeśli port jest otwarty
        """
        import socket

        try:
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except (socket.timeout, ConnectionRefusedError):
            return False

    @staticmethod
    def resolve_domain(domain: str) -> Optional[str]:
        """
        Rozwiązuje domenę na IP

        Args:
            domain: Nazwa domeny

        Returns:
            Adres IP lub None jeśli nie można rozwiązać
        """
        import socket

        try:
            return socket.gethostbyname(domain)
        except socket.gaierror:
            return None

    @staticmethod
    def ping_host(host: str, count: int = 1) -> bool:
        """
        Pinguje hosta

        Args:
            host: Adres hosta
            count: Liczba pingów

        Returns:
            True jeśli host odpowiada
        """
        import subprocess
        import platform

        param = '-n' if platform.system().lower() == 'windows' else '-c'

        try:
            result = subprocess.run(
                ['ping', param, str(count), host],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            return False


class FileUtils:
    """Narzędzia do pracy z plikami"""

    @staticmethod
    def create_directory_structure(base_path: str, structure: dict):
        """
        Tworzy strukturę katalogów

        Args:
            base_path: Ścieżka bazowa
            structure: Słownik opisujący strukturę
        """
        from pathlib import Path

        base = Path(base_path)
        base.mkdir(exist_ok=True)

        for name, content in structure.items():
            path = base / name

            if isinstance(content, dict):
                # To jest katalog
                FileUtils.create_directory_structure(str(path), content)
            else:
                # To jest plik
                path.parent.mkdir(parents=True, exist_ok=True)
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)

    @staticmethod
    def backup_file(file_path: str) -> str:
        """
        Tworzy kopię zapasową pliku

        Args:
            file_path: Ścieżka do pliku

        Returns:
            Ścieżka do kopii zapasowej
        """
        from pathlib import Path
        import shutil

        original = Path(file_path)
        if not original.exists():
            raise FileNotFoundError(f"Plik {file_path} nie istnieje")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{file_path}.backup.{timestamp}"

        shutil.copy2(original, backup_path)
        return backup_path

    @staticmethod
    def template_replace(template_content: str, variables: dict) -> str:
        """
        Zastępuje zmienne w szablonie

        Args:
            template_content: Zawartość szablonu
            variables: Słownik zmiennych do zastąpienia

        Returns:
            Przetworzona zawartość
        """
        result = template_content

        for key, value in variables.items():
            placeholder = f"{{{key}}}"
            result = result.replace(placeholder, str(value))

        return result


class SecurityUtils:
    """Narzędzia bezpieczeństwa"""

    @staticmethod
    def generate_password(length: int = 32) -> str:
        """
        Generuje bezpieczne hasło

        Args:
            length: Długość hasła

        Returns:
            Wygenerowane hasło
        """
        import secrets
        import string

        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    @staticmethod
    def generate_secret_key(length: int = 64) -> str:
        """
        Generuje klucz tajny

        Args:
            length: Długość klucza

        Returns:
            Klucz w formacie hex
        """
        import secrets
        return secrets.token_hex(length // 2)

    @staticmethod
    def validate_ssh_key(key_path: str) -> bool:
        """
        Waliduje klucz SSH

        Args:
            key_path: Ścieżka do klucza

        Returns:
            True jeśli klucz jest poprawny
        """
        from pathlib import Path

        key_file = Path(key_path)

        if not key_file.exists():
            return False

        try:
            with open(key_file, 'r') as f:
                content = f.read()

            # Sprawdź czy to klucz SSH
            valid_headers = [
                '-----BEGIN RSA PRIVATE KEY-----',
                '-----BEGIN OPENSSH PRIVATE KEY-----',
                '-----BEGIN DSA PRIVATE KEY-----',
                '-----BEGIN EC PRIVATE KEY-----'
            ]

            return any(header in content for header in valid_headers)

        except Exception:
            return False