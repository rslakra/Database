# Dynamic Multi-DB Backend

FastAPI app that picks its database **per request**. It connects to a PostgreSQL server on an **external host** (for the local Docker stack, see `../LocalDockerConnection`). It can also route requests to Databricks, which is optional.

## Layout

| Path                | Purpose |
| ------------------- | ------- |
| `.env` / `.env.sample` | Connection settings (`.env` is git-ignored) |
| `app/__init__.py`   | Package marker (run the app as `app.main:app` from this directory) |
| `app/configs.py`    | Loads `.env`, builds the SQLAlchemy URLs |
| `app/database.py`   | Engines, session factories, `get_db_route` dependency |
| `app/main.py`       | FastAPI app (`/`, `/db-health`, `/query-data`) |
| `Makefile`          | `install`, `run`, `check`, `clean` |
| `requirements.txt`  | Python dependencies |
| `.venv/`            | Local virtual environment, created by `make install` (git-ignored) |

## Setup

Run all commands from this directory (`Database/PostgreSQL/DynamicMultiDBBackend`).

```bash
cp .env.sample .env     # then edit the values
make install
make check              # prints (user, database) if the connection works
make run                # http://127.0.0.1:8000/docs
```

## Configuration (`.env`)

| Variable | Description |
| -------- | ----------- |
| `POSTGRES_HOST`, `POSTGRES_PORT` | External host and port (default port `5432`) |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` | Database and credentials |
| `POSTGRES_SSLMODE` | `prefer` by default; use `require` for most hosted databases |
| `DATABRICKS_SERVER_HOSTNAME`, `DATABRICKS_HTTP_PATH`, `DATABRICKS_TOKEN` | Optional. All three enable the `databricks` target (also `pip install databricks-sqlalchemy`) |
| `DATABRICKS_CATALOG`, `DATABRICKS_SCHEMA` | Optional Databricks defaults |
| `SAMPLE_TABLE` | Table read by `/query-data` (default `sample_table`) |

## Endpoints

Select the database with `?target=postgres|databricks` or the `X-Database-Target` header (the header wins). Default is `postgres`.

### Browser

```bash
http://127.0.0.1:8000
http://127.0.0.1:8000/docs
```

### CURL Commands

```bash
curl http://127.0.0.1:8000/db-health
curl http://127.0.0.1:8000/query-data
curl -H "X-Database-Target: databricks" http://127.0.0.1:8000/query-data
```

## Troubleshooting

| Issue | What to try |
| ----- | ----------- |
| `could not translate host name "host"` | `.env` still has placeholder values |
| Timeout / connection refused | Check VPN, firewall / allow-list and `POSTGRES_PORT` |
| `no pg_hba.conf entry ... no encryption` | Set `POSTGRES_SSLMODE=require` |
| `503 Databricks is not configured` | Fill in the three required `DATABRICKS_*` values |

## Author

- Rohtash Lakra
