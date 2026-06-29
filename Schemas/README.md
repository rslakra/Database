# SQL schemas

MySQL-style scripts for creating databases, tables, seed data, and user privileges. These are the source scripts used for testing; the Python objects in [`../database/`](../database/) mirror the same concepts.

## Scripts

### `Animal.sql`

- **Database:** `Animal` (script uses `USE Animals` — verify name matches your server)
- **Table:** `Pets` — pet registry with `id`, `name`, `owner`, `species`, `sex`, `birth`, `death`
- **Constraints:** `PRIMARY KEY (id)`, `AUTO_INCREMENT` on `id`
- **Data:** 9 sample pets

### `Blog.sql`

- **Database:** `Blog`
- **Tables:**
  - `Posts` — `id`, `title`, `body`, `email`, `created_on`
  - `Comments` — `id`, `post_id`, `title` with `FOREIGN KEY (post_id) REFERENCES Posts(id)`
- **Data:** Sample posts and comments

### `Library.sql`

- **Database:** `Library`
- **Tables:** `Users`, `Departments`, `Employees`, `Orders`
- **Data:** Users, departments, employees, and order rows for a small library scenario

### `GrantPermissions.sql`

- Shell-oriented notes for connecting as `root`
- `CREATE USER` and `GRANT ALL PRIVILEGES` example
- Maps to [`../database/access.py`](../database/access.py) `Access` objects

## Running a script

```bash
mysql -u root -p < Schemas/Animal.sql
mysql -u root -p < Schemas/Blog.sql
mysql -u root -p < Schemas/Library.sql
```

For grants, run the SQL statements inside `GrantPermissions.sql` interactively or paste them into a client session (the first line is a shell command, not SQL).

## Mapping to Python objects

| SQL | Python |
|-----|--------|
| Column in `CREATE TABLE` | `Attribute` |
| `PRIMARY KEY`, `FOREIGN KEY` | `Constraint` |
| `CREATE INDEX` / `KEY` | `Index` |
| Full `CREATE TABLE` | `Table` |
| `INSERT INTO` | `Record` |
| `CREATE PROCEDURE` | `Procedure` |
| `GRANT` / `CREATE USER` | `Access` |

See [`../database/README.md`](../database/README.md) for population examples.
