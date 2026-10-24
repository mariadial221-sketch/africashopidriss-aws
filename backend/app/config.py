"""Configuration 12-factor : tout passe par des variables d'environnement.

Chaque capacité AWS s'active en changeant une variable, pas le code :
  - DB_SECRET_ARN + DB_HOST : SQLite (local) -> Amazon RDS PostgreSQL
  - STORAGE_MODE=s3         : upload direct des photos vers S3 par URL pré-signée
  - EVENTS_MODE=sns         : publication des événements commande sur Amazon SNS
  - AUTH_MODE=cognito       : vérification des JWT Amazon Cognito sur les routes vendeur
"""
import os
from dataclasses import dataclass, field


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


@dataclass(frozen=True)
class Settings:
    app_name: str = "AfricaShop API"
    env: str = field(default_factory=lambda: _env("APP_ENV", "local"))
    aws_region: str = field(default_factory=lambda: _env("AWS_REGION", "us-east-1"))

    database_url: str = field(default_factory=lambda: _env("DATABASE_URL", "sqlite:///./africashop.db"))
    db_secret_arn: str = field(default_factory=lambda: _env("DB_SECRET_ARN"))
    db_host: str = field(default_factory=lambda: _env("DB_HOST"))
    db_name: str = field(default_factory=lambda: _env("DB_NAME", "africashop"))

    storage_mode: str = field(default_factory=lambda: _env("STORAGE_MODE", "local"))  # local | s3
    media_bucket: str = field(default_factory=lambda: _env("MEDIA_BUCKET"))
    media_public_base: str = field(default_factory=lambda: _env("MEDIA_PUBLIC_BASE", "/media"))
    local_media_dir: str = field(default_factory=lambda: _env("LOCAL_MEDIA_DIR", "./media"))

    events_mode: str = field(default_factory=lambda: _env("EVENTS_MODE", "log"))  # log | sns
    sns_topic_arn: str = field(default_factory=lambda: _env("SNS_TOPIC_ARN"))

    auth_mode: str = field(default_factory=lambda: _env("AUTH_MODE", "none"))  # none | cognito
    cognito_user_pool_id: str = field(default_factory=lambda: _env("COGNITO_USER_POOL_ID"))
    cognito_client_id: str = field(default_factory=lambda: _env("COGNITO_CLIENT_ID"))

    # Simulation PSP : en local on confirme le paiement depuis le front. En prod : webhook signé du PSP.
    psp_mode: str = field(default_factory=lambda: _env("PSP_MODE", "simulated"))
    psp_webhook_secret: str = field(default_factory=lambda: _env("PSP_WEBHOOK_SECRET", "dev-secret"))

    serve_frontend: bool = field(default_factory=lambda: _env("SERVE_FRONTEND", "true").lower() == "true")
    frontend_dir: str = field(default_factory=lambda: _env("FRONTEND_DIR"))

    cors_origins: str = field(default_factory=lambda: _env("CORS_ORIGINS", "*"))


settings = Settings()
