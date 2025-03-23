import logging
import os
from os import path
from random import randint
from urllib import parse

from pydantic_settings import BaseSettings, SettingsConfigDict


class GlobalSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    # App Settings
    ALLOWED_ORIGINS: str = os.getenv(
        "ALLOWED_ORIGINS", "http://127.0.0.1:3000,http://localhost:3000"
    )

    #################################### logging ####################################
    LOG_LEVEL: int = os.getenv("LOG_LEVEL", logging.DEBUG)
    #################################### logging ####################################

    #################################### sentry ####################################
    SENTRY_DSN: str = os.getenv("SENTRY_DSN", "")
    #################################### sentry ####################################

    #################################### static files ####################################
    STATIC_HOST: str = os.getenv("STATIC_HOST", "http://localhost:8001")
    DEFAULT_STATIC_DIR: str = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), os.path.join("../static")
    )
    STATIC_DIR: str = os.getenv("STATIC_DIR", DEFAULT_STATIC_DIR)
    TEMPLATE_DIR: str = os.getenv("TEMPLATE_DIR", path.join(STATIC_DIR, "templates"))
    #################################### static files ####################################

    #################################### DATABASE RELATED ####################################
    DATABASE_USER: str = os.getenv("DATABASE_USER", "uncle_k8ith")
    DATABASE_PASSWORD: str = os.getenv("DATABASE_PASSWORD", "05Chloeee")
    DATABASE_HOST: str = os.getenv("DATABASE_HOST", "localhost")
    DATABASE_PORT: str = os.getenv("DATABASE_PORT", "5432")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "KSMS")
    DATABASE_SCHEMA: str = os.getenv("DATABASE_SCHEMA", "KSMS")
    DATABASE_ENGINE_POOL_SIZE: int = os.getenv("DATABASE_ENGINE_POOL_SIZE", 20)
    DATABASE_ENGINE_MAX_OVERFLOW: int = os.getenv("DATABASE_ENGINE_MAX_OVERFLOW", 0)
    # Deal with DB disconnects
    # https://docs.sqlalchemy.org/en/20/core/pooling.html#pool-disconnects
    DATABASE_ENGINE_POOL_PING: bool = os.getenv("DATABASE_ENGINE_POOL_PING", False)
    # this will support special chars for credentials
    _QUOTED_DATABASE_PASSWORD: str = parse.quote(str(DATABASE_PASSWORD))
    # specify a single database URL
    DATABASE_URL: str = "sqlite+aiosqlite:///./KSMS.db"
    # DATABASE_URL: str = f"sqlite:///./backend/src/database/{DATABASE_NAME}.db"
    ############## redis for caching ################
    REDIS_CACHE_ENABLED: bool = os.getenv("REDIS_CACHE_ENABLED", True)
    REDIS_HOST: str = os.getenv("REDIS_HOST", "auth-redis")
    REDIS_PORT: str | int = os.getenv("REDIS_PORT", 6379)
    REDIS_PASSWORD: str | None = os.getenv("REDIS_PASSWORD", None)
    REDIS_CACHE_EXPIRATION_SECONDS: int = os.getenv(
        "REDIS_CACHE_EXPIRATION_SECONDS", 60 * 30
    )
    REDIS_DB: int = os.getenv("REDIS_DB", 0)
    ############## redis for caching ###############
    #################################### DATABASE RELATED ####################################

    #################################### auth related ####################################
    JWT_ACCESS_SECRET_KEY: str = os.getenv(
        "JWT_ACCESS_SECRET_KEY", "9d9bc4d77ac3a6fce1869ec8222729d2"
    )
    ENCRYPTION_ALGORITHM: str = os.getenv("ENCRYPTION_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)
    NEW_ACCESS_TOKEN_EXPIRE_MINUTES: int = os.getenv(
        "NEW_ACCESS_TOKEN_EXPIRE_MINUTES", 120
    )
    REFRESH_TOKEN_EXPIRE_MINUTES: int = os.getenv(
        "REFRESH_TOKEN_EXPIRE_MINUTES", 60 * 24
    )
    # Google Auth
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_USERINFO_URL: str = os.getenv(
        "GOOGLE_USERINFO_URL", "https://www.googleapis.com/oauth2/v3/userinfo"
    )
    GOOGLE_AUTH_URL: str = os.getenv(
        "GOOGLE_AUTH_URL", "https://accounts.google.com/o/oauth2/auth"
    )
    GOOGLE_TOKEN_URL: str = os.getenv(
        "GOOGLE_TOKEN_URL", "https://oauth2.googleapis.com/token"
    )
    REDIRECT_URI: str = os.getenv(
        "REDIRECT_URI", "http://localhost:8000/api/v1/auth/callback"
    )
    # openapi
    # OPENAPI_PROJECT_SECRET_KEY: str
    #################################### auth related ####################################

    #################################### admin ####################################
    ADMIN_SECRET_KEY: str = os.getenv(
        "ADMIN_SECRET_KEY", "Hv9LGqARc473ceBUYDw1FR0QaXOA3Ky4"
    )
    #################################### admin ####################################


class TestSettings(GlobalSettings):
    DATABASE_SCHEMA: str = f"test_{randint(1, 100)}"


class DevelopmentSettings(GlobalSettings):
    pass


class ProductionSettings(GlobalSettings):
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION_NAME: str = ""
    AWS_IMAGES_BUCKET: str = ""

    LOG_LEVEL: int = logging.INFO


def get_settings():
    env = os.environ.get("ENVIRONMENT", "development")
    if env == "test":
        return TestSettings()
    elif env == "development":
        return DevelopmentSettings()
    elif env == "production":
        return ProductionSettings()

    return GlobalSettings()


settings = get_settings()


LOGGING_CONFIG: dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
    },
    "handlers": {
        "default": {
            "level": settings.LOG_LEVEL,
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",  # Default is stderr
        },
    },
    "loggers": {
        "": {"handlers": ["default"], "level": settings.LOG_LEVEL, "propagate": False},
        "uvicorn": {
            "handlers": ["default"],
            "level": logging.ERROR,
            "propagate": False,
        },
    },
}
