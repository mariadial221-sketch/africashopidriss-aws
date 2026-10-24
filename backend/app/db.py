import json
from urllib.parse import quote_plus

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import settings


def _resolve_database_url() -> str:
    """En AWS, le mot de passe n'est JAMAIS dans une variable d'environnement :
    on lit le secret géré par RDS (ManageMasterUserPassword) dans AWS Secrets Manager."""
    if settings.db_secret_arn and settings.db_host:
        import boto3

        sm = boto3.client("secretsmanager", region_name=settings.aws_region)
        secret = json.loads(sm.get_secret_value(SecretId=settings.db_secret_arn)["SecretString"])
        user, pwd = secret["username"], quote_plus(secret["password"])
        return (f"postgresql+psycopg://{user}:{pwd}@{settings.db_host}:5432/"
                f"{settings.db_name}?sslmode=require")
    return settings.database_url


DATABASE_URL = _resolve_database_url()
_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=5, max_overflow=10,
                       connect_args=_connect_args) if not DATABASE_URL.startswith("sqlite") \
    else create_engine(DATABASE_URL, connect_args=_connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
