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

Implemented in [`../Nexus/catalog/metadata.py`](../Nexus/catalog/metadata.py) and attached to `MultiModelDatabase.metadata`:

```python
from catalog.metadata import Metadata

Metadata(name="Animal", tables=[...], collections=[...], access_rules=[...])
```

## Populating metadata

1. **From SQL scripts** — Parse `Schemas/*.sql` for database name and `CREATE TABLE` blocks.
2. **From a live server** — Query `information_schema` or use `SHOW CREATE TABLE`.
3. **By hand** — Assemble `Table`, `Access`, and catalog fields after building objects per [`../Nexus/README.md`](../Nexus/README.md).

## Related

- Schema DDL: [`../Schemas/README.md`](../Schemas/README.md)
- Object model: [`../Nexus/README.md`](../Nexus/README.md)
- Row data (not catalog): [`../Data/README.md`](../Data/README.md)
