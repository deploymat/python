from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings
import os
from pathlib import Path


class PyDockSettings(BaseSettings):
    """Konfiguracja PyDock z automatycznym ładowaniem z .env"""

    # Core settings
    project_name: str = Field(default="pydock-project", alias="PYDOCK_PROJECT_NAME")
    environment: str = Field(default="development", alias="PYDOCK_ENVIRONMENT")

    # Domain and VPS
    domain: Optional[str] = Field(default=None, alias="PYDOCK_DOMAIN")
    vps_ip: Optional[str] = Field(default=None, alias="PYDOCK_VPS_IP")
    ssh_user: str = Field(default="root", alias="PYDOCK_SSH_USER")
    ssh_key_path: Optional[str] = Field(default=None, alias="PYDOCK_SSH_KEY_PATH")
    ssh_password: Optional[str] = Field(default=None, alias="PYDOCK_SSH_PASSWORD")

    # API Server
    api_host: str = Field(default="0.0.0.0", alias="PYDOCK_API_HOST")
    api_port: int = Field(default=8000, alias="PYDOCK_API_PORT")
    api_debug: bool = Field(default=False, alias="PYDOCK_API_DEBUG")
    api_reload: bool = Field(default=False, alias="PYDOCK_API_RELOAD")

    # API Security
    api_secret_key: str = Field(default="change-this-secret-key", alias="PYDOCK_API_SECRET_KEY")
    access_token_expire_minutes: int = Field(default=30, alias="PYDOCK_API_ACCESS_TOKEN_EXPIRE_MINUTES")
    allowed_origins: List[str] = Field(default=["*"], alias="PYDOCK_API_ALLOWED_ORIGINS")

    # Cloudflare
    cloudflare_api_token: Optional[str] = Field(default=None, alias="CLOUDFLARE_API_TOKEN")
    cloudflare_email: Optional[str] = Field(default=None, alias="CLOUDFLARE_EMAIL")
    cloudflare_zone_id: Optional[str] = Field(default=None, alias="CLOUDFLARE_ZONE_ID")
    cloudflare_auto_dns: bool = Field(default=True, alias="CLOUDFLARE_AUTO_DNS")
    cloudflare_proxy_enabled: bool = Field(default=True, alias="CLOUDFLARE_PROXY_ENABLED")
    cloudflare_ttl: int = Field(default=300, alias="CLOUDFLARE_TTL")

    # Database
    database_url: str = Field(default="postgresql://admin:password@database:5432/pydock", alias="DATABASE_URL")
    redis_url: str = Field(default="redis://redis:6379/0", alias="REDIS_URL")
    db_password: Optional[str] = Field(default=None, alias="DB_PASSWORD")
    redis_password: Optional[str] = Field(default=None, alias="REDIS_PASSWORD")

    # Docker
    docker_registry: Optional[str] = Field(default=None, alias="DOCKER_REGISTRY")
    docker_username: Optional[str] = Field(default=None, alias="DOCKER_USERNAME")
    docker_password: Optional[str] = Field(default=None, alias="DOCKER_PASSWORD")
    docker_build_args: Optional[str] = Field(default=None, alias="DOCKER_BUILD_ARGS")

    # Container settings
    container_restart_policy: str = Field(default="unless-stopped", alias="CONTAINER_RESTART_POLICY")
    container_memory_limit: str = Field(default="512m", alias="CONTAINER_MEMORY_LIMIT")
    container_cpu_limit: float = Field(default=1.0, alias="CONTAINER_CPU_LIMIT")

    # SSL/TLS
    ssl_email: Optional[str] = Field(default=None, alias="SSL_EMAIL")
    ssl_staging: bool = Field(default=False, alias="SSL_STAGING")
    ssl_auto_https: bool = Field(default=True, alias="SSL_AUTO_HTTPS")
    cert_resolver: str = Field(default="letsencrypt", alias="CERT_RESOLVER")
    cert_storage: str = Field(default="/data/caddy", alias="CERT_STORAGE")

    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_format: str = Field(default="json", alias="LOG_FORMAT")
    log_file: str = Field(default="/var/log/pydock/app.log", alias="LOG_FILE")

    # Monitoring
    monitoring_enabled: bool = Field(default=True, alias="MONITORING_ENABLED")
    metrics_port: int = Field(default=9090, alias="METRICS_PORT")
    health_check_interval: int = Field(default=30, alias="HEALTH_CHECK_INTERVAL")

    # Notifications
    slack_webhook_url: Optional[str] = Field(default=None, alias="SLACK_WEBHOOK_URL")
    slack_channel: str = Field(default="#deployments", alias="SLACK_CHANNEL")
    smtp_host: Optional[str] = Field(default=None, alias="SMTP_HOST")
    smtp_port: int = Field(default=587, alias="SMTP_PORT")
    smtp_username: Optional[str] = Field(default=None, alias="SMTP_USERNAME")
    smtp_password: Optional[str] = Field(default=None, alias="SMTP_PASSWORD")
    notification_email: Optional[str] = Field(default=None, alias="NOTIFICATION_EMAIL")

    # Backup
    backup_enabled: bool = Field(default=True, alias="BACKUP_ENABLED")
    backup_schedule: str = Field(default="0 2 * * *", alias="BACKUP_SCHEDULE")
    backup_retention_days: int = Field(default=30, alias="BACKUP_RETENTION_DAYS")
    backup_s3_bucket: Optional[str] = Field(default=None, alias="BACKUP_S3_BUCKET")
    aws_access_key_id: Optional[str] = Field(default=None, alias="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(default=None, alias="AWS_SECRET_ACCESS_KEY")

    # Development
    hot_reload: bool = Field(default=False, alias="HOT_RELOAD")
    debug_mode: bool = Field(default=False, alias="DEBUG_MODE")
    profiling_enabled: bool = Field(default=False, alias="PROFILING_ENABLED")

    # Testing
    test_database_url: str = Field(default="postgresql://test:test@localhost:5433/pydock_test",
                                   alias="TEST_DATABASE_URL")
    test_cloudflare_zone_id: Optional[str] = Field(default=None, alias="TEST_CLOUDFLARE_ZONE_ID")

    # Rate limiting
    rate_limit_enabled: bool = Field(default=True, alias="RATE_LIMIT_ENABLED")
    rate_limit_requests: int = Field(default=100, alias="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=60, alias="RATE_LIMIT_WINDOW")

    # Cache
    cache_ttl: int = Field(default=3600, alias="CACHE_TTL")
    cache_backend: str = Field(default="redis", alias="CACHE_BACKEND")

    # Workers
    worker_processes: int = Field(default=4, alias="WORKER_PROCESSES")
    worker_timeout: int = Field(default=30, alias="WORKER_TIMEOUT")

    # Security
    security_headers_enabled: bool = Field(default=True, alias="SECURITY_HEADERS_ENABLED")
    cors_enabled: bool = Field(default=True, alias="CORS_ENABLED")

    # Feature flags
    feature_websocket_logs: bool = Field(default=True, alias="FEATURE_WEBSOCKET_LOGS")
    feature_auto_scaling: bool = Field(default=False, alias="FEATURE_AUTO_SCALING")
    feature_blue_green_deploy: bool = Field(default=False, alias="FEATURE_BLUE_GREEN_DEPLOY")
    feature_rollback: bool = Field(default=True, alias="FEATURE_ROLLBACK")
    feature_health_checks: bool = Field(default=True, alias="FEATURE_HEALTH_CHECKS")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._auto_generate_passwords()

    def _auto_generate_passwords(self):
        """Auto-generate secure passwords if not provided"""
        from .utils import SecurityUtils

        if not self.db_password:
            self.db_password = SecurityUtils.generate_password(32)

        if not self.redis_password:
            self.redis_password = SecurityUtils.generate_password(24)

        if self.api_secret_key == "change-this-secret-key":
            self.api_secret_key = SecurityUtils.generate_secret_key(64)

    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment.lower() == "development"

    @property
    def ssh_key_expanded(self) -> Optional[str]:
        """Get expanded SSH key path"""
        if self.ssh_key_path:
            return str(Path(self.ssh_key_path).expanduser())
        return None

    @property
    def ssl_email_or_default(self) -> str:
        """Get SSL email or generate from domain"""
        if self.ssl_email:
            return self.ssl_email
        if self.domain:
            return f"admin@{self.domain}"
        return "admin@example.com"

    def save_env_file(self, path: str = ".env"):
        """Save current settings to .env file"""
        env_content = []

        # Core settings
        env_content.extend([
            "# PyDock Configuration",
            f"PYDOCK_PROJECT_NAME={self.project_name}",
            f"PYDOCK_ENVIRONMENT={self.environment}",
            "",
            "# Domain and VPS",
            f"PYDOCK_DOMAIN={self.domain or ''}",
            f"PYDOCK_VPS_IP={self.vps_ip or ''}",
            f"PYDOCK_SSH_USER={self.ssh_user}",
            f"PYDOCK_SSH_KEY_PATH={self.ssh_key_path or ''}",
            "",
            "# API Server",
            f"PYDOCK_API_HOST={self.api_host}",
            f"PYDOCK_API_PORT={self.api_port}",
            f"PYDOCK_API_DEBUG={self.api_debug}",
            f"PYDOCK_API_SECRET_KEY={self.api_secret_key}",
            "",
            "# Cloudflare",
            f"CLOUDFLARE_API_TOKEN={self.cloudflare_api_token or ''}",
            f"CLOUDFLARE_EMAIL={self.cloudflare_email or ''}",
            f"CLOUDFLARE_ZONE_ID={self.cloudflare_zone_id or ''}",
            f"CLOUDFLARE_AUTO_DNS={self.cloudflare_auto_dns}",
            "",
            "# Database",
            f"DATABASE_URL={self.database_url}",
            f"DB_PASSWORD={self.db_password}",
            "",
            "# SSL",
            f"SSL_EMAIL={self.ssl_email_or_default}",
            f"SSL_STAGING={self.ssl_staging}",
        ])

        with open(path, 'w') as f:
            f.write('\n'.join(env_content))


# Global settings instance
settings = PyDockSettings()


def get_settings() -> PyDockSettings:
    """Get PyDock settings instance"""
    return settings


def reload_settings():
    """Reload settings from environment"""
    global settings
    settings = PyDockSettings()