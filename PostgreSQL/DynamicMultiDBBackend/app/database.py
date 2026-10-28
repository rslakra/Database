# database.py - engines, session factories and the routing dependency
from typing import Generator

from fastapi import HTTPException, Query, Request
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.configs import settings

# 1. PostgreSQL (engines connect lazily, so importing this module never needs the DB)
postgres_engine = create_engine(settings.postgres_url, pool_pre_ping=True)
PostgresSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=postgres_engine)

# 2. Databricks (optional - only built when configured)
databricks_engine = None
DatabricksSessionLocal = None
if settings.databricks_url is not None:
    databricks_engine = create_engine(settings.databricks_url, pool_pre_ping=True)
    DatabricksSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=databricks_engine)


def get_db_route(
    request: Request,
    # Option A: query parameter (e.g. ?target=databricks)
    target: str = Query("postgres", description="Database target: 'postgres' or 'databricks'"),
) -> Generator[Session, None, None]:
    # Option B: custom header (e.g. X-Database-Target) takes precedence
    db_target = (request.headers.get("X-Database-Target") or target).lower()

    if db_target == "postgres":
        db = PostgresSessionLocal()
    elif db_target == "databricks":
        if DatabricksSessionLocal is None:
            raise HTTPException(status_code=503, detail="Databricks is not configured.")
        db = DatabricksSessionLocal()
    else:
        raise HTTPException(status_code=400, detail="Invalid database target specified.")

    try:
        yield db
    finally:
        db.close()
