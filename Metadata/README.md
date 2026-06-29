# Metadata

Reserved for database-level catalog information: what exists on the server beyond individual tables and rows.

## Intended contents

Metadata describes the database as a whole, for example:

| Field | Example | Source |
|-------|---------|--------|
| Database name | `Animal`, `Blog`, `Library` | `CREATE DATABASE` |
| Charset / collation | `utf8mb4`, `utf8mb4_unicode_ci` | `CREATE DATABASE` options |
| Table list | `["Pets"]`, `["Posts", "Comments"]` | `information_schema` or parsed DDL |
| Version / engine | MySQL 8.x, InnoDB | Server introspection |
| Grants summary | Users and privileges | `mysql.user`, `SHOW GRANTS` |

## Python model

A stub lives in [`../database/metadata.py`](../database/metadata.py):

```python
class Metadata:
    pass
```

Planned shape (not implemented yet):

```python
Metadata(
    name="Animal",
    tables=[pets_table],           # list[Table]
    access_rules=[...],            # list[Access]
    charset="utf8mb4",
)
```

## Populating metadata

1. **From SQL scripts** — Parse `Schemas/*.sql` for database name and `CREATE TABLE` blocks.
2. **From a live server** — Query `information_schema` or use `SHOW CREATE TABLE`.
3. **By hand** — Assemble `Table`, `Access`, and catalog fields after building objects per [`../database/README.md`](../database/README.md).

## Related

- Schema DDL: [`../Schemas/README.md`](../Schemas/README.md)
- Object model: [`../database/README.md`](../database/README.md)
- Row data (not catalog): [`../Data/README.md`](../Data/README.md)
