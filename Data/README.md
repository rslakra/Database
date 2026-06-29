# Data

Place for row-level data separate from DDL in [`../Schemas/`](../Schemas/). Today, sample rows are embedded as `INSERT` statements inside the schema scripts; this folder is for exports, bulk seeds, or fixtures as the project grows.

## What belongs here

| Format | Use case |
|--------|----------|
| `.sql` | Bulk `INSERT` or `LOAD DATA` scripts |
| `.csv` / `.tsv` | Table dumps for import |
| `.json` | API or app fixtures mapped to `Record` objects |

## What does not belong here

- `CREATE TABLE` and constraints → [`../Schemas/`](../Schemas/)
- Column definitions and types → [`../database/attributes.py`](../database/attributes.py)
- User grants → [`../Schemas/GrantPermissions.sql`](../Schemas/GrantPermissions.sql) or [`../database/access.py`](../database/access.py)

## Current sample data (in Schemas)

| Database | Table(s) | Script |
|----------|----------|--------|
| Animal | Pets (9 rows) | `Schemas/Animal.sql` |
| Blog | Posts, Comments | `Schemas/Blog.sql` |
| Library | Users, Departments, Employees, Orders | `Schemas/Library.sql` |

## Representing rows in Python

Each `INSERT` maps to a `Record`:

```python
from database.records import Record

Record(
    table=pets,
    values={
        "name": "Puffball",
        "owner": "Diane",
        "species": "hamster",
        "sex": "f",
        "birth": "1999-03-30",
        "death": None,
    },
)
```

Rules:

- Keys must match `Table.attributes` names.
- Use `None` for SQL `NULL`.
- Skip `AUTO_INCREMENT` columns unless supplying explicit ids.

## Suggested layout (optional)

```
Data/
  Animal/
    pets.csv
  Blog/
    posts.csv
    comments.csv
  Library/
    users.csv
    ...
```

Import with MySQL `LOAD DATA LOCAL INFILE` or a small script that builds `Record` lists and emits SQL.

## Related

- Object model: [`../database/README.md`](../database/README.md)
- Schema scripts: [`../Schemas/README.md`](../Schemas/README.md)
