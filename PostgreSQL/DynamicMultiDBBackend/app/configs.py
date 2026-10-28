# configs.py - settings loaded from environment / .env
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from sqlalchemy.engine import URL

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


@dataclass(frozen=True)
class Settings:
    postgres_host: str = _env("POSTGRES_HOST", "localhost")
    postgres_port: int = int(_env("POSTGRES_PORT", "5432"))
    postgres_db: str = _env("POSTGRES_DB", "postgres")
    postgres_user: str = _env("POSTGRES_USER", "postgres")
    postgres_password: str = _env("POSTGRES_PASSWORD")
    postgres_sslmode: str = _env("POSTGRES_SSLMODE", "prefer")

    databricks_server_hostname: str = _env("DATABRICKS_SERVER_HOSTNAME")
    databricks_http_path: str = _env("DATABRICKS_HTTP_PATH")
    databricks_token: str = _env("DATABRICKS_TOKEN")
    databricks_catalog: str = _env("DATABRICKS_CATALOG")
    databricks_schema: str = _env("DATABRICKS_SCHEMA")

    sample_table: str = _env("SAMPLE_TABLE", "sample_table")

    @property
    def postgres_url(self) -> URL:
        # URL.create escapes special characters in the password safely.
        return URL.create(
            "postgresql+psycopg2",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
            database=self.postgres_db,
            query={"sslmode": self.postgres_sslmode},
        )

    @property
    def databricks_url(self) -> Optional[URL]:
        """Returns None when Databricks is not configured."""
        if not (self.databricks_server_hostname and self.databricks_http_path and self.databricks_token):
            return None
        query = {"http_path": self.databricks_http_path}
        if self.databricks_catalog:
            query["catalog"] = self.databricks_catalog
        if self.databricks_schema:
            query["schema"] = self.databricks_schema
        return URL.create(
            "databricks",
            username="token",
            password=self.databricks_token,
            host=self.databricks_server_hostname,
            query=query,
        )


settings = Settings()
