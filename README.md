# Databases

Sample relational database scripts and **Nexus** — a Python multi-model database that handles both SQL tables and NoSQL documents. Used for learning, testing, and exploring hybrid RDBMS architecture.

## Repository layout

| Path | Purpose |
|------|---------|
| [`Schemas/`](Schemas/) | SQL scripts — `CREATE DATABASE`, tables, inserts, grants |
| [`Nexus/`](Nexus/) | Multi-model database engine (SQL + NoSQL) and object model |
| [`Data/`](Data/) | Row data exports or seed files (optional; inserts live in `Schemas/` today) |
| [`Metadata/`](Metadata/) | Database catalog / introspection artifacts (reserved) |
| [`MySQL/`](MySQL/) | Client configuration (`my.cnf`) |

## Quick start

### MySQL scripts (external server)

1. Configure credentials — see [`MySQL/README.md`](MySQL/README.md).
2. Run a schema script:

   ```bash
   mysql -u root -p < Schemas/Animal.sql
   ```

### Nexus (in-process multi-model engine)

```bash
cd Nexus
python3 examples/demo.py
python3 examples/connectors_demo.py
```

See [`Nexus/README.md`](Nexus/README.md) for full architecture and package map.

## Sample databases

| Script | Database | Tables |
|--------|----------|--------|
| `Schemas/Animal.sql` | Animal | Pets |
| `Schemas/Blog.sql` | Blog | Posts, Comments (FK) |
| `Schemas/Library.sql` | Library | Users, Departments, Employees, Orders |
| `Schemas/GrantPermissions.sql` | — | `CREATE USER` / `GRANT` examples |

## How the pieces fit together

```
Schemas/*.sql     →  DDL/DML on MySQL (production-style testing)
       ↓
Nexus/            →  multi-model engine (SQL + NoSQL, shared storage)
       ↓
Data/             →  optional exports or bulk seed files
Metadata/         →  optional catalog snapshots
```

- **Schemas/** — reference SQL for a traditional RDBMS.
- **Nexus/** — build your own hybrid database: unified storage, dual query engines, WAL, MVCC, schema manager.

## Requirements

- MySQL (or compatible server) for running `Schemas/` scripts
- Python 3.10+ for Nexus
