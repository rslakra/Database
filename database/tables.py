"""Table definitions — the structural unit of a database schema.

A Table groups column definitions (Attribute), integrity rules (Constraint),
and optional indexes (Index). Records (rows) belong to a Table once data is
inserted.

Should contain:
    name: Table identifier (e.g. "Pets", "Users", "Posts").
    attributes: Ordered list of Attribute instances (schema / columns).
    constraints: List of Constraint instances (PK, FK, unique, check).
    indexes: List of Index instances (secondary indexes only; PK is a constraint).

Populate from CREATE TABLE by parsing column lines into Attributes and trailing
clauses into Constraints. Attach Indexes from separate CREATE INDEX statements
or inline KEY definitions.

Example — Pets table (Animal.sql):

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
        constraints=[
            Constraint("primary_key", columns=["id"]),
        ],
    )

Cross-table links: put FOREIGN KEY constraints on the child table (e.g. Comments
in Blog.sql references Posts).
"""

from database.attributes import Attribute
from database.constraints import Constraint
from database.indexes import Index


class Table:
    """Named collection of columns and rules; rows are Record instances."""

    def __init__(
        self,
        name: str,
        *,
        attributes: list[Attribute] | None = None,
        constraints: list[Constraint] | None = None,
        indexes: list[Index] | None = None,
    ):
        self.name = name
        self.attributes = attributes or []
        self.constraints = constraints or []
        self.indexes = indexes or []
