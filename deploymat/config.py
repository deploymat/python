import json
import os
from pathlib import Path
from typing import Dict, Any


class Config:
    """Klasa zarządzająca konfiguracją PyDock"""

    def __init__(self, config_file: str = "pydock.json"):
        """
        Inicjalizuje zarządzanie konfiguracją

        Args:
            config_file: Nazwa pliku konfiguracyjnego
        """
        self.config_file = Path(config_file)
        self.config_dir = Path(".pydock")
        self.config_dir.mkdir(exist_ok=True)

    def exists(self) -> bool:
        """Sprawdza czy plik konfiguracyjny istnieje"""
        return self.config_file.exists()

    def load(self) -> Dict[str, Any]:
        """
        Ładuje konfigurację z pliku

        Returns:
            Słownik z konfiguracją
        """
        if not self.exists():
            raise FileNotFoundError(f"Plik konfiguracyjny {self.config_file} nie istnieje")

        with open(self.config_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save(self, config_data: Dict[str, Any]):
        """
        Zapisuje konfigurację do pliku

        Args:
            config_data: Dane konfiguracyjne do zapisania
        """
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)

    def update(self, updates: Dict[str, Any]):
        """
        Aktualizuje istniejącą konfigurację

        Args:
            updates: Dane do zaktualizowania
        """
        if self.exists():
            config = self.load()
            config.update(updates)
            self.save(config)
        else:
            self.save(updates)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Pobiera wartość z konfiguracji

        Args:
            key: Klucz konfiguracji
            default: Wartość domyślna

        Returns:
            Wartość z konfiguracji lub wartość domyślna
        """
        try:
            config = self.load()
            return config.get(key, default)
        except FileNotFoundError:
            return default

    def validate(self) -> bool:
        """
        Waliduje poprawność konfiguracji

        Returns:
            True jeśli konfiguracja jest poprawna
        """
        try:
            config = self.load()

            # Sprawdź wymagane pola
            required_fields = ['domain', 'vps_ip', 'services']
            for field in required_fields:
                if field not in config:
                    raise ValueError(f"Brak wymaganego pola: {field}")

            # Sprawdź czy domena jest poprawna
            domain = config['domain']
            if not domain or '.' not in domain:
                raise ValueError("Niepoprawna domena")

            # Sprawdź IP
            vps_ip = config['vps_ip']
            if not vps_ip:
                raise ValueError("Brak IP VPS")

            return True

        except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
            return False

    def create_deployment_config(self, environment: str = "production") -> Dict[str, Any]:
        """
        Tworzy konfigurację dla konkretnego środowiska

        Args:
            environment: Nazwa środowiska

        Returns:
            Konfiguracja dla środowiska
        """
        base_config = self.load()

        # Dodaj specyficzne ustawienia środowiska
        deployment_config = base_config.copy()
        deployment_config['environment'] = environment
        deployment_config['timestamp'] = self._get_timestamp()

        # Zapisz konfigurację deploymentu
        deployment_file = self.config_dir / f"deployment-{environment}.json"
        with open(deployment_file, 'w', encoding='utf-8') as f:
            json.dump(deployment_config, f, indent=2, ensure_ascii=False)

        return deployment_config

    def _get_timestamp(self) -> str:
        """Zwraca aktualny timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()

    def list_deployments(self) -> list:
        """
        Lista wszystkich deploymentów

        Returns:
            Lista plików deploymentów
        """
        deployment_files = list(self.config_dir.glob("deployment-*.json"))
        return [f.stem.replace("deployment-", "") for f in deployment_files]

    def get_deployment_config(self, environment: str) -> Dict[str, Any]:
        """
        Pobiera konfigurację konkretnego deploymentu

        Args:
            environment: Nazwa środowiska

        Returns:
            Konfiguracja deploymentu
        """
        deployment_file = self.config_dir / f"deployment-{environment}.json"

        if not deployment_file.exists():
            raise FileNotFoundError(f"Nie znaleziono konfiguracji dla środowiska: {environment}")

        with open(deployment_file, 'r', encoding='utf-8') as f:
            return json.load(f)