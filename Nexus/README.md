# Nexus — Multi-Model Database

Nexus is a **learning-oriented multi-model database** that handles both **SQL (relational)** and **NoSQL (document)** workloads in one engine. User-facing query languages differ; storage, indexing, transactions, and execution share the same core.

This project is designed as an **academic / learning** codebase. The architecture mirrors production multi-model systems (PostgreSQL JSONB, ArangoDB, OrientDB) while staying small enough to read and extend in Python.

---

## Architecture overview

Separate **how users query data** from **how data is stored on disk**:

```
┌─────────────────────────────────────────────────────────────┐
│  SQL API (execute_sql)     NoSQL API (execute_nosql)        │
│       │                           │                         │
│       ▼                           ▼                         │
│  SQLParser                  DocumentQuery                   │
│       └──────────┬────────────────┘                         │
│                  ▼                                          │
│            Optimizer                                        │
│                  ▼                                          │
│         LogicalQueryPlan                                    │
│    (Scan → Filter → Project / Insert / Update / Delete)     │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Validator (strict SQL vs schemaless documents)             │
│  IndexRegistry (primary, secondary, hash, inverted)         │
│  MVCC + WriteAheadLog                                       │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  StorageEngine — unified key-value layer                    │
│  Namespace: table:Pets:1  |  collection:posts:<uuid>        │
│  Binary encoding (JSON envelope; swap for BSON / Protobuf)  │
└─────────────────────────────────────────────────────────────┘
```

---

## Five layers to build (and where they live)

### 1. Unified storage engine

**Goal:** One physical layer for structured rows and unstructured documents.

| Concept | Implementation | Production upgrade |
|---------|----------------|-------------------|
| Key-value / LSM foundation | `storage/engine.py` — in-memory dict | RocksDB, LevelDB, custom LSM |
| Binary encoding | `storage/encoding.py` — JSON envelope | BSON, Protocol Buffers, Avro |
| Logical partitioning | `storage/namespace.py` — `table:` vs `collection:` prefixes | Same pattern on disk |

**Keys on disk:**

```
table:Pets:1
collection:posts:b6715eb8-1329-42f8-8f4b-d1d82c66b4f2
```

Both SQL rows and NoSQL documents are encoded with `encode_payload()` before `put`.

**Step-by-step:**

1. Choose a low-level store (start in-memory; plug in RocksDB later).
2. Define a single binary format for rows and documents (`encoding.py`).
3. Prefix every key with namespace kind + name so tables and collections coexist.
4. Implement `put`, `get`, `scan`, `delete` on the engine — nothing SQL/NoSQL-specific above this layer.

---

### 2. Plug-and-play indexing engine

**Goal:** SQL needs B-tree primary/secondary indexes; NoSQL needs hash and inverted indexes on JSON fields.

| Index type | Use case | Module |
|------------|----------|--------|
| Primary (B+ tree) | PK / `_id` → storage location | `index/btree.py`, `index/registry.py` |
| Secondary (B+ tree) | Column or JSON path lookups | `IndexRegistry.register(SECONDARY)` |
| Hash | Equality on hot fields | `IndexRegistry.register(HASH)` |
| Inverted | Full-text on document fields | `index/inverted.py` |

**Step-by-step:**

1. Register a **primary** index when calling `create_table()` or `create_collection()`.
2. Add **secondary** indexes with `db.create_index(..., index_type=IndexType.SECONDARY)`.
3. Add **full-text** with `db.create_text_index(...)` for NoSQL collections.
4. On every write, update all indexes for that namespace in `_write_row` / `_write_document`.

---

### 3. Dual execution engine (compilers)

**Goal:** Two parsers, one shared execution plan.

| Path | Entry | Output |
|------|-------|--------|
| SQL | `parser/sql.py` — `SQLParser` | `LogicalQueryPlan` |
| Document | `parser/document.py` — `DocumentQuery` | `LogicalQueryPlan` |
| Optimizer | `planner/optimizer.py` | Rewritten plan |
| Executor | `executor/runner.py` — `PlanExecutor` | Result rows/documents |

**Logical operators** (`planner/plan.py`):

- `SCAN` — read namespace
- `FILTER` — SQL `WHERE` or NoSQL `filter` dict
- `PROJECT` — column/field projection
- `INSERT` / `UPDATE` / `DELETE` — mutations

**Step-by-step:**

1. Parse user input into an AST (learning impl: regex SQL; production: ANTLR).
2. Validate against `Validator` (tables, columns, types for SQL).
3. Build a `LogicalQueryPlan` — never execute SQL and documents on separate storage paths.
4. Run `Optimizer.optimize()` then `PlanExecutor.execute()`.

**SQL example:**

```python
db.execute_sql("SELECT name, owner FROM Pets WHERE species = 'hamster'")
```

**NoSQL example:**

```python
db.execute_nosql(db.documents.find("posts", filter={"title": "Nexus"}))
# alias: db.nosql.find(...)
```

---

### 4. Transaction and concurrency manager

**Goal:** ACID-friendly writes for SQL; fast non-blocking reads for NoSQL via MVCC.

| Component | Role | Module |
|-----------|------|--------|
| Write-Ahead Log | Log every write before applying | `transaction/wal.py` |
| MVCC | Versioned reads; snapshot isolation | `transaction/mvcc.py` |
| Recovery | Replay WAL after crash | `MultiModelDatabase.recover()` |

**Step-by-step:**

1. On every insert/update/delete, append to WAL first (`wal.append(...)`).
2. Bump MVCC version (`mvcc.write(...)`).
3. Apply to `StorageEngine`.
4. On startup, call `db.recover()` to replay unapplied WAL entries.

Production systems add lock managers, deadlock detection, and distributed consensus; MVCC + WAL is the foundation.

---

### 5. Validator

**Goal:** Fixed structure (SQL) vs dynamic structure (documents).

| Mode | Namespace | Behavior | Module |
|------|-----------|----------|--------|
| Strict | SQL `Table` | Reject invalid types, NOT NULL, missing columns | `validator/manager.py` |
| Schemaless | NoSQL `Collection` | Accept any JSON; validate on read if needed | `SchemaMode.SCHEMALESS` |
| Strict docs | NoSQL `Collection` | Require `required_fields` only | `SchemaMode.STRICT` |

**Step-by-step:**

1. Register SQL tables with `create_table(Table(...))` — mirrors `CREATE TABLE`.
2. Register collections with `create_collection(Collection(...))`.
3. All writes go through `validate_row()` or `validate_document()` before storage.
4. Optional: schema-on-read for NoSQL by skipping validation and interpreting fields at query time.

---

## Project root and imports

**Nexus is the project root.** All imports are relative to this folder — there is no `Nexus.` package prefix.

```
Nexus/                    ← cd here; this is the root
├── engine.py             from engine import MultiModelDatabase
├── database.py           backward-compatible re-export
├── catalog/              DDL: Table, Column, Constraint
├── document/             Collection, Document
├── examples/
├── pyproject.toml
└── requirements.txt
```

### Import conventions

| Import | Use for |
|--------|---------|
| `from engine import MultiModelDatabase` | Main entry point (preferred) |
| `from database import MultiModelDatabase` | Backward-compatible alias |
| `from catalog import Table, Column, Constraint` | SQL DDL catalog |
| `from document import Collection, Document` | Document store |
| `from relational import Row` | SQL row inserts |
| `from datatype import DataType, DataFormat` | Types and file formats |
| `from dataio import DataPort` | File import/export |
| `from parser import SQLParser, DocumentQuery` | Query parsers |
| `from validator import Validator` | Write validation |

Legacy shims still work: `nosql`, `schema`, `connectors`, `indexing`, `execution`.

### Setup

```bash
cd Nexus

# Option A — run examples directly (bootstrap adds root to sys.path)
python3 examples/demo.py
python3 examples/connectors_demo.py

# Option B — editable install
pip install -e ".[excel]"
python3 -c "from engine import MultiModelDatabase; print('ok')"
```

---

## Package layout

```
Nexus/
├── engine.py                # MultiModelDatabase — main entry point
├── database.py              # backward-compatible re-export
├── catalog/                 # DDL metadata (Table, Column, Constraint, IndexMeta)
├── relational/              # Row (SQL insert tuple)
├── document/                # Collection, Document
├── datatype/                # DataType, DataFormat, SqlDataType
├── storage/                 # Layer 1 — engine, encoding, namespaces
├── index/                   # Layer 2 — B+ tree, inverted, IndexRegistry
├── parser/                  # Layer 3a — SQLParser, DocumentQuery
├── planner/                 # Layer 3b — LogicalQueryPlan, Optimizer
├── executor/                # Layer 3c — PlanExecutor
├── transaction/             # Layer 4 — WAL, MVCC
├── validator/               # Layer 5 — strict vs schemaless writes
├── dataio/                  # Layer 6 — CSV, JSON, JSONL, Excel I/O
├── connectors/              # shim → dataio
├── nosql/                   # shim → document
├── schema/                  # shim → validator
├── indexing/                # shim → index
├── execution/               # shim → parser + planner
└── examples/
```

---

## Data connectors (import / export)

Connectors decouple **file formats** from the storage engine. All formats produce or consume `list[dict]` rows, which Nexus loads into SQL tables or NoSQL collections.

### Supported formats

| Format | Class | Extensions | Dependency |
|--------|-------|------------|------------|
| CSV / TSV | `CSVConnector` | `.csv`, `.tsv` | stdlib |
| JSON | `JSONConnector` | `.json` | stdlib |
| JSONL / NDJSON | `JSONLConnector` | `.jsonl`, `.ndjson` | stdlib |
| Excel | `ExcelConnector` | `.xlsx`, `.xlsm` | `openpyxl` (optional) |

### Import into SQL table

```python
from engine import MultiModelDatabase
from catalog import Column, Constraint, Table

db = MultiModelDatabase("Animal")
db.create_table(Table(
    name="Pets",
    attributes=[
        Column("id", "INT", nullable=False, auto_increment=True),
        Column("name", "VARCHAR(20)", nullable=False),
        Column("owner", "VARCHAR(20)"),
        Column("species", "VARCHAR(20)"),
    ],
    constraints=[Constraint("primary_key", columns=["id"])],
))

count = db.data.import_table("pets.csv", "Pets")
print(f"Imported {count} rows")
```

### Export from SQL table

```python
db.data.export_table("output/pets.csv", "Pets")
db.data.export_table("output/pets.json", "Pets", fmt="json")
```

### Import / export NoSQL collections

```python
from document import Collection
from datatype.data_formats import DataFormat

db.create_collection(Collection("events"))
db.data.import_collection("events.json", "events", fmt=DataFormat.JSON)
db.data.export_collection("events.jsonl", "events", fmt=DataFormat.JSONL)
```

### Auto-detect format from extension

```python
from dataio import get_connector_for_path

connector = get_connector_for_path("data/report.xlsx")  # ExcelConnector
rows = connector.read("data/report.xlsx", sheet_name="Sheet1")
```

### Custom connector (plug-and-play)

```python
from dataio import DataConnector, register_connector
from datatype.data_formats import RowList

class ParquetConnector(DataConnector):
    format_name = "parquet"
    file_extensions = ("parquet",)
    def read(self, path, **options): ...
    def write(self, path, rows: RowList, **options): ...

register_connector(ParquetConnector())
```

### Connector options

| Connector | Options |
|-----------|---------|
| CSV | `delimiter`, `encoding`, `fieldnames` (write) |
| JSON | `root_key` (wrap/unwrap array), `indent`, `encoding` |
| JSONL | `encoding` |
| Excel | `sheet_name`, `data_only`, `fieldnames` (write) |

Install Excel support: `pip install openpyxl` or `pip install -e ".[excel]"`.

---

## Data types (SQL and NoSQL)

`datatype/data_types.py` defines the types Nexus can store, validate, and coerce.


### SQL column types (`SqlDataType`)

| Category | Types |
|----------|-------|
| Integers | `INT`, `BIGINT`, `SMALLINT`, `TINYINT` (`INTEGER` → alias for `INT`) |
| Floats | `FLOAT`, `DECIMAL` (`DOUBLE` / `NUMERIC` are aliases) |
| Strings | `VARCHAR(n)`, `CHAR(n)`, `TEXT` |
| Date/time | `DATE`, `TIME`, `DATETIME`, `TIMESTAMP` |
| Other | `BOOLEAN` (`BOOL` alias), `JSON`, `BLOB`, `BINARY` |

```python
from datatype import DataType, SqlDataType

# Instance API — parse once, coerce many
name_type = DataType("VARCHAR(20)")
name_type.coerce("Diane")

# Or from enum
DataType(SqlDataType.INT).coerce("42")

# Class methods (same as module-level helpers)
DataType.parse_sql("INTEGER")       # TypeSpec(base=INT)
DataType.coerce_sql("42", "INT")    # 42
DataType.infer_nosql({"a": 1})      # NoSqlDataType.OBJECT
```

### NoSQL document types (`NoSqlDataType`)

| Type | Python values |
|------|----------------|
| `string` | `str` |
| `number` | `float` |
| `integer` | `int` |
| `boolean` | `bool` |
| `array` | `list` |
| `object` | `dict` |
| `null` | `None` |
| `date` | `date`, `datetime`, ISO strings |
| `binary` | `bytes` |

```python
from datatype import DataType, NoSqlDataType

DataType.infer_nosql({"a": 1})
DataType.validate_nosql(42, NoSqlDataType.INTEGER)
```

Strict SQL tables use `coerce_sql_value()` in `SchemaManager.validate_row()`. Schemaless collections accept any JSON-compatible value; use `infer_nosql_type()` for schema-on-read.

---

## Quick start

From the **Nexus** directory:

```bash
python3 examples/demo.py
python3 examples/connectors_demo.py
```

Expected output:

```
SQL: [{'name': 'Puffball', 'owner': 'Diane', 'species': 'hamster'}]
NoSQL: [{'_id': '...', 'title': 'Nexus', 'body': '...', 'tags': [...]}]
Search: [...]
```

### Programmatic setup

```python
from engine import MultiModelDatabase
from catalog import Column, Constraint, Table
from document import Collection, Document

db = MultiModelDatabase("Animal", data_dir="./data/animal")

# SQL — strict table
pets = Table(
    name="Pets",
    attributes=[
        Column("id", "INT", nullable=False, auto_increment=True),
        Column("name", "VARCHAR(20)", nullable=False),
        Column("owner", "VARCHAR(20)"),
        Column("species", "VARCHAR(20)"),
    ],
    constraints=[Constraint("primary_key", columns=["id"])],
)
db.create_table(pets)
db.execute_sql("INSERT INTO Pets (name, owner, species) VALUES ('Puffball', 'Diane', 'hamster')")

# NoSQL — schemaless collection
posts = Collection("posts")
db.create_collection(posts)
db.create_text_index("idx_posts_body", collection="posts", field="body")
db.insert_document(Document(collection=posts, data={"title": "Hello", "body": "world"}))
```

### Map sample SQL scripts

Scripts in [`../Schemas/`](../Schemas/) can be modeled in Nexus:

| Script | SQL in Nexus | NoSQL extension |
|--------|--------------|-----------------|
| `Animal.sql` | `Pets` table + INSERT | `Collection("pet_profiles")` for flexible metadata |
| `Blog.sql` | `Posts`, `Comments` + FK | `Collection("post_drafts")` schemaless drafts |
| `Library.sql` | Users, Departments, … | Event logs as documents |

MySQL scripts remain useful for testing against a real server; Nexus is the in-process multi-model engine.

---

## Building your own — detailed roadmap

### Phase 1 — Storage (week 1)

1. Read `storage/engine.py` and `storage/encoding.py`.
2. Replace the in-memory `_data` dict with append-only files or RocksDB.
3. Implement `flush()` and load snapshot on startup.

### Phase 2 — Indexes (week 2)

1. Study `indexing/btree.py` — replace with a real B+ tree if needed.
2. Wire secondary indexes for SQL columns used in `WHERE`.
3. Add inverted indexes for NoSQL text search fields.

### Phase 3 — Query engines (week 3)

1. Extend `SQLParser` or integrate ANTLR for richer SQL.
2. Add REST/GraphQL wrapper around `NoSQLQuery` for HTTP clients.
3. Expand `Optimizer` (predicate pushdown, index selection).

### Phase 4 — Transactions (week 4)

1. Harden WAL with fsync and checkpointing.
2. Expose `BEGIN` / `COMMIT` / `ROLLBACK` on `MultiModelDatabase`.
3. Use MVCC snapshot version for consistent reads during writes.

### Phase 5 — Schema and ops (week 5)

1. Foreign-key enforcement in `SchemaManager` for SQL.
2. Optional JSON Schema validation for strict collections.
3. Metrics, backup, and replication (out of scope for v0.1).

### Phase 6 — Data connectors (week 6)

1. Use `db.data.import_table` / `export_table` for SQL pipelines.
2. Use `db.data.import_collection` for document ingestion (logs, API dumps).
3. Add custom connectors via `register_connector()` (Parquet, Avro, XML).

---

## Real-world inspiration

| System | What to study |
|--------|----------------|
| **PostgreSQL** | `JSONB` type + GIN indexes — SQL engine with document columns |
| **ArangoDB / OrientDB** | Native multi-model (document + graph + SQL-like AQL) |
| **MongoDB** | Document wire protocol; compare with `nosql_engine.py` |
| **RocksDB** | LSM storage backend to swap into `StorageEngine` |

---

## Core SQL objects (relational model)

| Module | Class | SQL equivalent |
|--------|-------|----------------|
| `catalog/column.py` | `Column` | Column definition (`Attribute` alias) |
| `catalog/constraint.py` | `Constraint` | PRIMARY KEY, FOREIGN KEY, … |
| `catalog/index.py` | `IndexMeta` | CREATE INDEX metadata (`Index` alias) |
| `catalog/table.py` | `Table` | CREATE TABLE |
| `relational/row.py` | `Row` | INSERT row (`Record` alias) |
| `catalog/access.py` | `Access` | GRANT / user privileges |
| `catalog/procedure.py` | `Procedure` | Stored procedures |
| `catalog/metadata.py` | `Metadata` | Database catalog |

## Document models

| Module | Class | Role |
|--------|-------|------|
| `document/document.py` | `Document` | One JSON document |
| `document/collection.py` | `Collection` | Named document bucket |

## Data I/O modules

| Module | Class | Role |
|--------|-------|------|
| `dataio/base.py` | `DataConnector` | Connector protocol |
| `dataio/csv_connector.py` | `CSVConnector` | CSV / TSV files |
| `dataio/json_connector.py` | `JSONConnector`, `JSONLConnector` | JSON / JSONL |
| `dataio/excel_connector.py` | `ExcelConnector` | Excel workbooks |
| `dataio/service.py` | `DataPort` | `db.data.import_*` / `export_*` |
| `dataio/registry.py` | `get_connector` | Resolve format by name or extension |

---

## Requirements

- Python 3.10+
- Run from the `Nexus/` directory, or `pip install -e .`
- Optional: `openpyxl` for Excel (`pip install -e ".[excel]"`)

---

## Project stance

Nexus is an **academic / learning** project: architecture and interfaces match production multi-model databases, but durability, networking, and full SQL compatibility are intentionally simplified. Use it to understand the layers; swap components (RocksDB, ANTLR, Raft) as you grow toward production.
