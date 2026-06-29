# Database object model

Python classes that represent the main building blocks of a relational database. Each module maps to a SQL concept and includes docstrings with examples drawn from the scripts in [`../Schemas/`](../Schemas/).

## Modules

| Module | Class | SQL equivalent |
|--------|-------|----------------|
| `attributes.py` | `Attribute` | Column definition (`name`, type, `NOT NULL`, `DEFAULT`, `AUTO_INCREMENT`) |
| `constraints.py` | `Constraint` | `PRIMARY KEY`, `FOREIGN KEY`, `UNIQUE`, `CHECK` |
| `indexes.py` | `Index` | `CREATE INDEX`, `KEY`, `UNIQUE INDEX` |
| `tables.py` | `Table` | `CREATE TABLE` (columns + constraints + indexes) |
| `records.py` | `Record` | `INSERT INTO … VALUES` (one row) |
| `procedures.py` | `Procedure` | `CREATE PROCEDURE` / `CREATE FUNCTION` |
| `access.py` | `Access` | `CREATE USER`, `GRANT`, `REVOKE` |
| `metadata.py` | `Metadata` | Database catalog (name, charset, tables, grants) — stub |

## Object relationships

```
Table
├── attributes: list[Attribute]     # schema / columns
├── constraints: list[Constraint]   # PK, FK, unique, check
├── indexes: list[Index]            # secondary indexes
└── (rows) → Record                 # data, keyed by column name

Access                              # per-user privileges on objects
Procedure                           # stored routines
Metadata                            # whole-database description (planned)
```

## Populate from SQL

### Schema (`Animal.sql` → `Pets`)

```python
from database.attributes import Attribute
from database.constraints import Constraint
from database.tables import Table

pets = Table(
    name="Pets",
    attributes=[
        Attribute("id", "INT", nullable=False, auto_increment=True),
        Attribute("name", "VARCHAR(20)", nullable=False),
        Attribute("owner", "VARCHAR(20)"),
        Attribute("species", "VARCHAR(20)"),
        Attribute("sex", "CHAR(1)"),
        Attribute("birth", "DATE"),
        Attribute("death", "DATE"),
    ],
    constraints=[Constraint("primary_key", columns=["id"])],
)
```

### Data (first `INSERT` in `Animal.sql`)

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

### Foreign key (`Blog.sql` → `Comments`)

```python
from database.constraints import Constraint

Constraint(
    "foreign_key",
    columns=["post_id"],
    references_table="Posts",
    references_columns=["id"],
)
```

### Access (`GrantPermissions.sql`)

```python
from database.access import Access

Access(
    principal="username@localhost",
    privilege="ALL",
    object_type="global",
    object_name="*.*",
)
```

## Conventions

- **Attributes** describe structure; **Records** hold values. Do not store row data on `Attribute`.
- Model `NOT NULL` with `Attribute(nullable=False)`. Model keys and relationships with `Constraint`.
- Omit auto-increment columns from `Record.values` when the server should assign `id`.
- Use `None` for SQL `NULL`.

## Import

From the repository root:

```bash
python3 -c "from database.tables import Table; print('ok')"
```
