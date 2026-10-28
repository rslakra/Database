# PostgreSQL (Docker)

Local **PostgreSQL 18** with persistent bind-mounted data and **pgweb** (web UI) via Docker Compose.

## Project layout

| File / path           | Purpose |
| --------------------- | ------- |
| `docker-compose.yml`  | `postgresql` + `postgres-admin` (pgweb) services, `postgres-network` |
| `Makefile`            | `make start`, `make psql`, `make health-ui`, etc. — mirrors compose |
| `README.md`           | This guide |
| `.gitignore`          | Ignores `data/` (database files stay local, not in git) |
| `data/`               | Default bind mount for PostgreSQL 18 PGDATA (`./data/18/docker/`) — created by `make start` |

## Quick start

From this directory:

```bash
make start          # starts postgresql + postgres-admin; waits until DB is healthy
make status
make health         # verify PostgreSQL accepts TCP connections
make health-ui      # verify pgweb at http://localhost:8080
make ui             # print web UI URL
make stop           # stops both services; data stays on disk
make restart
```

Custom persistence path or port:

```bash
make start DATA_DIR=$HOME/postgres-data
make restart DATA_DIR=/Volumes/backup/postgres POSTGRES_PORT=5433
```

Other targets: `make psql`, `make shell`, `make url`, `make logs`, `make logs-ui`, `make data-dir`, `make help`, `make clean` (destructive). Legacy aliases: `make adminer` → `make ui`, `make health-adminer` → `make health-ui`, `make logs-adminer` → `make logs-ui`.

Raw Compose (equivalent to `make start`; Makefile adds `--wait`):

```bash
export POSTGRES_DATA_DIR=./data
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=postgres
export POSTGRES_DB=dummy
export POSTGRES_PORT=5432
mkdir -p "$POSTGRES_DATA_DIR"
docker compose up -d --wait
```

Stop and **delete all data** (destructive):

```bash
make clean
```



## Connection details



### PostgreSQL


| Setting  | Default                  |
| -------- | ------------------------ |
| Host     | `localhost`              |
| Port     | `5432` (`POSTGRES_PORT`) |
| User     | `postgres`               |
| Password | `postgres`               |
| Database | `dummy` (`POSTGRES_DB`)  |


Print the URL:

```bash
make url
# postgresql://postgres:postgres@localhost:5432/dummy
```

**psql from your machine** (requires client installed):

```bash
psql "postgresql://postgres:postgres@localhost:5432/dummy"
```

**psql inside the container:**

```bash
make psql
# or: docker exec -it postgres psql -U postgres -d dummy
```



### Web UI (pgweb)

pgweb connects automatically via `PGWEB_DATABASE_URL` — **no login form**, no driver dropdown, no `localhost` confusion.

After `make start`:

```bash
make health     # PostgreSQL TCP ready
make health-ui  # pgweb serving and connected
make ui         # print URL
```

Open **[http://localhost:8080](http://localhost:8080)** — you should land directly on the `dummy` database with tables visible.

Browse tables, run SQL in the query panel, and export data. Same database your `make psql` session uses.

To work on another database on the same server, use pgweb’s **database dropdown** in the top bar (see Step 7 below). Do **not** enable `PGWEB_SESSIONS=1` — it disables auto-connect and forces a manual login form (where `localhost` fails from inside Docker).

## Multiple databases and per-app users

One PostgreSQL **container** runs one PostgreSQL **cluster**. That cluster can hold **many databases**. Each app connects to the same host and port but uses a **different database name** (and ideally its own username/password).

`POSTGRES_DB=dummy` only creates the **first** database when the data directory is empty. All other databases are created with SQL.

### Where database files live (important)

PostgreSQL does **not** store each database as its own folder under `./data/my_app/`, `./data/shop/`, etc.

All databases in this container share **one** data directory (PGDATA):


| Location     | Path                             |
| ------------ | -------------------------------- |
| On your Mac  | `./data/18/docker/`              |
| In container | `/var/lib/postgresql/18/docker/` |


PostgreSQL manages files internally inside that directory. You choose separation by **database name** and **user permissions**, not by creating subdirectories under `DATA_DIR`.


| Goal                                       | Approach                                                                                                       |
| ------------------------------------------ | -------------------------------------------------------------------------------------------------------------- |
| Logical isolation (tables, users)          | Multiple databases + dedicated users in **this** container                                                     |
| Physical isolation (separate disk folders) | Run **separate** PostgreSQL containers, each with its own `DATA_DIR` (e.g. `make start DATA_DIR=./data-app-a`) |
| Advanced (single cluster, custom paths)    | PostgreSQL **tablespaces** — rarely needed for local dev                                                       |




### Step 1 — List existing databases

```bash
make psql
```

```sql
\l
-- or
SELECT datname FROM pg_database WHERE datistemplate = false ORDER BY 1;
```



### Step 2 — Create a new database

Database names: up to 63 characters, start with a letter or `_`, use lowercase letters, numbers, and `_` (e.g. `my_app`, `orders_v2`).

```sql
CREATE DATABASE my_app;
CREATE DATABASE shop_api;
```

Confirm:

```sql
\l
```



### Step 3 — Create a dedicated user per database

Connect as superuser (`make psql` uses `postgres`). Example: one user per app, each with its own password.

```sql
-- App A
CREATE USER my_app_user WITH PASSWORD 'change_me_app_a';

-- App B
CREATE USER shop_api_user WITH PASSWORD 'change_me_shop_b';
```



### Step 4 — Grant access (user → database only)

Grant each user access **only** to its database:

```sql
-- my_app
GRANT CONNECT ON DATABASE my_app TO my_app_user;
\c my_app
GRANT USAGE, CREATE ON SCHEMA public TO my_app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO my_app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO my_app_user;

-- shop_api
\c postgres
GRANT CONNECT ON DATABASE shop_api TO shop_api_user;
\c shop_api
GRANT USAGE, CREATE ON SCHEMA public TO shop_api_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO shop_api_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO shop_api_user;
```

Return to the default database:

```sql
\c dummy
\q
```

`postgres` superuser can still access every database (useful for admin and pgweb).

### Step 5 — Verify each user can connect

From your Mac (replace password and database):

```bash
psql "postgresql://my_app_user:change_me_app_a@localhost:5432/my_app" -c "SELECT current_user, current_database();"
psql "postgresql://shop_api_user:change_me_shop_b@localhost:5432/shop_api" -c "SELECT current_user, current_database();"
```

Inside the container:

```bash
docker exec -it postgres psql -U my_app_user -d my_app -c "SELECT current_user, current_database();"
```



### Step 6 — Connect different apps to different databases

Same PostgreSQL instance — only the **database name** and **credentials** change.


| App             | Connection string (from your Mac)                                     |
| --------------- | --------------------------------------------------------------------- |
| App A           | `postgresql://my_app_user:change_me_app_a@localhost:5432/my_app`      |
| App B           | `postgresql://shop_api_user:change_me_shop_b@localhost:5432/shop_api` |
| Admin / default | `postgresql://postgres:postgres@localhost:5432/dummy`                 |


**From another Docker service on** `postgres-network` (use compose service name, not `localhost`):

```text
postgresql://my_app_user:change_me_app_a@postgresql:5432/my_app
postgresql://shop_api_user:change_me_shop_b@postgresql:5432/shop_api
```

Example `docker-compose.yml` snippet for an app on the same network:

```yaml
services:
  my-app:
    image: my-app:latest
    environment:
      DATABASE_URL: postgresql://my_app_user:change_me_app_a@postgresql:5432/my_app
    networks:
      - postgres-network

networks:
  postgres-network:
    external: true
    name: postgresql_postgres-network   # find yours: docker network ls | grep postgres-network
```

Easiest option: add your app as another service in the same `docker-compose.yml` so it joins `postgres-network` automatically.

**From Docker but not on** `postgres-network`**:** use `host.docker.internal:5432` as the host.

### Step 7 — Manage all databases in pgweb

1. Open [http://localhost:8080](http://localhost:8080) — auto-connects to `dummy`.
2. In the **top bar**, open the **database dropdown** (current database name).
3. Select another database (e.g. `my_app`, `shop_api`) — pgweb switches on the same PostgreSQL server.
4. Run SQL (including `CREATE DATABASE …`) as the connected user.

If you need to test an app-specific user, connect with `psql` (Step 5) or temporarily change `PGWEB_DATABASE_URL` in compose and run `make restart`.

**Do not use `PGWEB_SESSIONS=1`.** In pgweb 0.16.x it ignores `PGWEB_DATABASE_URL` and shows a connect form instead. From inside the pgweb container, `localhost` is wrong — use hostname `postgresql` if connecting manually.



### Quick reference


| Question                                   | Answer                                                                  |
| ------------------------------------------ | ----------------------------------------------------------------------- |
| Multiple DBs in one container?             | Yes — `CREATE DATABASE name;`                                           |
| Any database name?                         | Yes, within PostgreSQL naming rules                                     |
| Separate username/password per DB?         | Yes — `CREATE USER …` + `GRANT` on that database                        |
| Separate subfolder per DB under `./data/`? | **No** — one shared PGDATA dir; use multiple DBs or multiple containers |
| Same web UI for all DBs?                   | Yes — database dropdown in pgweb (same server, switch `dbname`)         |
| Same port for all apps?                    | Yes — `5432`; apps differ by `dbname` and user                          |




## What `docker-compose.yml` does



### `postgresql` service


| Setting               | Value                                                                                                         |
| --------------------- | ------------------------------------------------------------------------------------------------------------- |
| `services.postgresql` | Compose **service name** — used by `make logs`, pgweb connection URL, etc.                                    |
| `image`               | `postgres:18`                                                                                                 |
| `container_name`      | `postgres` — runtime name for `docker exec` (`make psql`, `make shell`)                                       |
| `restart`             | `always` — Docker restarts after crash or host reboot                                                         |
| `ports`               | `${POSTGRES_PORT:-5432}:5432`                                                                                 |
| `environment`         | `POSTGRES_USER` (`postgres`), `POSTGRES_PASSWORD` (`postgres`), `POSTGRES_DB` (`dummy`) — **first boot only** |
| `command`             | `postgres -c listen_addresses=*` — ensures TCP from other containers on `postgres-network`                        |
| `volumes`             | `${POSTGRES_DATA_DIR}:/var/lib/postgresql` — required for **PostgreSQL 18+**                                  |
| `networks`            | `postgres-network` with aliases `db`, `postgres`                                                                  |
| `healthcheck`         | `pg_isready -h 127.0.0.1 -p 5432 -U postgres -d dummy` — `postgres-admin` starts only after this passes |


Commented options in the file (`shm_size`, `tmpfs` on `/dev/shm`) can be enabled for heavy workloads that need more shared memory.

### `postgres-admin` service


| Setting       | Value                                                                                     |
| ------------- | ----------------------------------------------------------------------------------------- |
| `image`       | `sosedoff/pgweb:0.16.2` — PostgreSQL web UI (auto-connects, no login form)                |
| `restart`     | `always`                                                                                  |
| `depends_on`  | `postgresql` with `condition: service_healthy`                                            |
| `environment` | `PGWEB_DATABASE_URL` — auto-connect on startup; use UI database dropdown to switch DBs    |
| `networks`    | `postgres-network` — shared bridge with `postgresql` service                                  |
| `ports`       | `8080:8081` — [http://localhost:8080](http://localhost:8080) (host 8080 → container 8081) |


### Networks

Both services join a user-defined bridge network keyed **`postgres-network`** in compose. The name is arbitrary — you can rename it (e.g. `backend`) as long as every service that must talk to PostgreSQL uses the same key.

| Name | Role |
| ---- | ---- |
| Compose network key | `postgres-network` — wiring in `docker-compose.yml` |
| Docker network on host | `{project}_postgres-network` — find with `docker network ls \| grep postgres-network` |
| Service hostname for apps | `postgresql` — use in connection URLs from other containers (not the network key) |
| Network aliases | `db`, `postgres` — optional alternates for `postgresql` |

The Makefile exports `POSTGRES_DATA_DIR` from `DATA_DIR` (default `./data`), sets `SERVICE=postgresql`, `UI_SERVICE=postgres-admin`, and `CONTAINER=postgres` to match compose.

---



### 💡 Core Rules for PostgreSQL in Docker



#### 1. The magic path (where data lives)

This stack uses `postgres:18`. The official image changed where data is stored — mounting the wrong path causes a crash loop (`unused mount/volume` in logs).


|                                | PostgreSQL 18+ (this repo)                   | PostgreSQL 17 and earlier                       |
| ------------------------------ | -------------------------------------------- | ----------------------------------------------- |
| **Compose mount**              | `${POSTGRES_DATA_DIR}:/var/lib/postgresql`   | `${POSTGRES_DATA_DIR}:/var/lib/postgresql/data` |
| **Inside container**           | `/var/lib/postgresql/18/docker/` (versioned) | `/var/lib/postgresql/data/` (flat)              |
| **On your Mac (**`./data`**)** | `./data/18/docker/`                          | files directly in `./data/`                     |


```
Host (DATA_DIR)              Container (postgres:18)
./data/                  →   /var/lib/postgresql/
  └── 18/docker/         →     └── 18/docker/   ← actual PGDATA
```

**Rule:** Always map the **host data folder** to `/var/lib/postgresql` for PG 18 — never to `/var/lib/postgresql/data`.

If you previously started with the old mount, wipe and re-init: `make clean` then `make start` (back up `./data` first if needed).

#### 2. The restart policy

`restart: always` on both services tells Docker to bring containers back after a crash or host reboot. PostgreSQL data survives because it lives on the bind-mounted host directory, not inside the container filesystem.

#### 3. Environment variables (first boot only)

`POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB` run **only when the data directory is empty** — on first initialization. After that:

- Restarting the container → existing files are reused; env vars are ignored.
- Changing password in compose → no effect until you `make clean` and init a fresh data dir.
- Upgrading major versions → use `pg_upgrade` or dump/restore; do not only swap the image tag on an incompatible data layout.

---



## Verify persistence

Goal: prove data survives `make stop` / `make start` because it lives on the host at `./data`, not inside the container.

### 1. Start PostgreSQL

```bash
make start
make health
```



### 2. Open `psql` and create test data

```bash
make psql
```

At the `dummy=#` prompt, run **in this order**:

```sql
-- smoke test (optional)
SELECT version();
SELECT 2 + 2;

-- create table
CREATE TABLE IF NOT EXISTS objects (
  id   serial PRIMARY KEY,
  note text
);

-- insert a row
INSERT INTO objects (note) VALUES ('still here after rebuild');

-- list tables in this database
\dt

-- describe the table columns
\d objects

-- list all records (baseline before rebuild — expect 1 row)
SELECT * FROM objects;
```

Exit `psql`:

```text
\q
```



### 3. Recreate the containers (data on disk is kept)

```bash
make stop
make start
make health
```



### 4. Re-open `psql` and verify data persisted

```bash
make psql
```

```sql
-- list tables — objects should still exist
\dt

-- list records — should still show 'still here after rebuild'
SELECT * FROM objects;
```

```text
\q
```

If the table or row is missing, data was not persisted to `./data`.

### 5. Optional — inspect files on the host

```bash
make data-dir
ls -la ./data/18/docker/
```



### Handy `psql` commands

In `make psql`, commands that start with `\` are **meta-commands** — they do not need a semicolon at the end.


| Command | Purpose |
| ------- | ------- |
| `\l` | List all databases on the server |
| `\c database_name` | Connect to a different database (e.g. `\c dummy`, `\c my_app`) |
| `\dt` | List tables in the current database |
| `\d table_name` | Describe a table (columns, types, keys) — e.g. `\d objects` |
| `\x` | Toggle expanded display — vertical layout for wide rows |
| `\h` | Help for SQL commands (e.g. `\h CREATE TABLE`) |
| `\q` | Quit `psql` |


Same SQL works in **pgweb** ([http://localhost:8080](http://localhost:8080)) — use the query panel after `make ui`.

## Change credentials or database name (first run only)

`POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB` apply only on **first initialization** of an empty data directory. To change them:

1. Back up anything you need.
2. Wipe data: `make clean`
3. Edit `docker-compose.yml` or pass vars: `make start POSTGRES_PASSWORD=newsecret POSTGRES_DB=mydb`
4. Start again: `make start`



## Makefile reference

### Targets

| Target | Description |
| ------ | ----------- |
| `make start` | Create `DATA_DIR`, `docker compose up -d --wait` for `postgresql` + `postgres-admin` |
| `make stop` | `docker compose down` — data on disk kept |
| `make restart` | `make stop` then `make start` |
| `make status` | `docker compose ps` |
| `make health` | `pg_isready` on TCP `127.0.0.1:5432` inside container `postgres` |
| `make health-ui` | HTTP check on `http://localhost:8080/api/info` |
| `make logs` | Follow logs for service `postgresql` |
| `make logs-ui` | Follow logs for service `postgres-admin` (pgweb) |
| `make psql` | Interactive psql as `POSTGRES_USER` on `POSTGRES_DB` |
| `make shell` | Bash in container `postgres` |
| `make url` | Print `postgresql://…@localhost:PORT/DB` |
| `make ui` | Print pgweb URL and default database |
| `make data-dir` | Create / list `DATA_DIR` |
| `make clean` | Stop containers and delete all files in `DATA_DIR` (destructive) |
| `make help` | List targets and variables |

Aliases (backwards compat): `make adminer`, `make health-adminer`, `make logs-adminer`.

### Variables

| Variable | Default | Maps to |
| -------- | ------- | ------- |
| `DATA_DIR` | `./data` | `POSTGRES_DATA_DIR` in compose volume mount |
| `POSTGRES_USER` | `postgres` | Compose `POSTGRES_USER`, pgweb URL |
| `POSTGRES_PASSWORD` | `postgres` | Compose `POSTGRES_PASSWORD`, pgweb URL |
| `POSTGRES_DB` | `dummy` | Compose `POSTGRES_DB`, pgweb URL, `make psql` database |
| `POSTGRES_PORT` | `5432` | Host port published for PostgreSQL |
| `UI_PORT` | `8080` | Documented host port for pgweb (`8080:8081` in compose) |

Example: `make start DATA_DIR=$HOME/postgres-data POSTGRES_PORT=5433`




## Troubleshooting


| Issue                                                      | What to try                                                                         |
| ---------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| `unused mount/volume` / `pg_ctlcluster` error on PG 18     | Old mount layout in `./data`. `make clean` then `make start` (back up first).       |
| Port 5432 already in use                                   | `make start POSTGRES_PORT=5433`                                                     |
| Port 8080 already in use                                   | Change `8080:8081` host side in `docker-compose.yml` for pgweb                      |
| [http://localhost:8080](http://localhost:8080) not loading | `make logs-ui` then `make restart`. Check `postgres-admin` is Up, not restarting.   |
| Web UI empty / connection error                            | `make health` then `make health-ui`. If health passes but UI fails, `make restart`. |
| Connect error after enabling `PGWEB_SESSIONS=1`            | Remove it from compose — sessions mode disables auto-connect. Use the **database dropdown** to switch DBs instead. |
| Container exits immediately                                | `make logs` — wrong mount path or permissions on `DATA_DIR`                         |
| App login fails after changing env vars in compose         | `POSTGRES_*` apply on first boot only; existing data keeps old credentials — `make clean` or `ALTER USER` in SQL |
| Forgot data location                                       | Default `./data` (live files under `./data/18/docker/`), or `DATA_DIR` you passed   |




## Next steps

1. **Test persistence** — steps above; ask for a scripted version.
2. **Automate daily backups** — `pg_dump` from inside Docker on a schedule.
3. **Other GUI tools** — DBeaver/pgAdmin to `localhost:5432`, or use built-in pgweb at `:8080`.



## Reference

- [postgres (Docker)](https://hub.docker.com/_/postgres)
- [pgweb](https://github.com/sosedoff/pgweb) — image `sosedoff/pgweb:0.16.2`
- [pgweb Usage wiki](https://github.com/sosedoff/pgweb/wiki/Usage)



## Author

- Rohtash Lakra

