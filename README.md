# Databases

Sample relational database scripts and a Python object model for describing schemas, data, access control, and metadata. Used for learning and testing MySQL-style DDL/DML.

## Repository layout

| Path | Purpose |
|------|---------|
| [`Schemas/`](Schemas/) | SQL scripts — `CREATE DATABASE`, tables, inserts, grants |
| [`database/`](database/) | Python classes that mirror RDBMS concepts |
| [`Data/`](Data/) | Row data exports or seed files (optional; inserts live in `Schemas/` today) |
| [`Metadata/`](Metadata/) | Database catalog / introspection artifacts (reserved) |
| [`MySQL/`](MySQL/) | Client configuration (`my.cnf`) |

## Quick start

1. Configure credentials — see [`MySQL/README.md`](MySQL/README.md).
2. Run a schema script against MySQL:

   ```bash
   mysql -u root -p < Schemas/Animal.sql
   ```

3. Explore the Python model — see [`database/README.md`](database/README.md).

## Sample databases

| Script | Database | Tables |
|--------|----------|--------|
| `Schemas/Animal.sql` | Animal | Pets |
| `Schemas/Blog.sql` | Blog | Posts, Comments (FK) |
| `Schemas/Library.sql` | Library | Users, Departments, Employees, Orders |
| `Schemas/GrantPermissions.sql` | — | `CREATE USER` / `GRANT` examples |

## How the pieces fit together

```
Schemas/*.sql          →  DDL/DML on a live server
       ↓
database/*.py          →  in-memory representation (Table, Record, …)
       ↓
Data/                  →  optional exports or bulk seed files
Metadata/              →  optional catalog snapshots (names, types, grants)
```

SQL scripts define the source of truth today. The `database` package documents how each RDBMS concept maps to Python objects and how to populate them from those scripts.

## Requirements

- MySQL (or compatible server) for running `Schemas/` scripts
- Python 3.10+ to import the `database` package
