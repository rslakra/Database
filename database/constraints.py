"""Integrity rules that apply across one or more columns or tables.

Constraints enforce valid data and relationships. They are declared on a Table
(or between tables) and are separate from column types (Attribute).

Kinds seen in this repo's SQL scripts:

    PRIMARY KEY (id)
        -> Constraint("primary_key", columns=["id"])

    FOREIGN KEY (post_id) REFERENCES Posts(id)   # Blog.sql
        -> Constraint(
               "foreign_key",
               columns=["post_id"],
               references_table="Posts",
               references_columns=["id"],
           )

    NOT NULL is usually modeled on Attribute.nullable; UNIQUE and CHECK can
    use Constraint("unique", columns=[...]) or Constraint("check", expression=...).

Populate from CREATE TABLE trailing clauses and ALTER TABLE ADD CONSTRAINT.
"""


class Constraint:
    """A schema rule: primary key, foreign key, unique, or check.

    Should contain:
        kind: "primary_key", "foreign_key", "unique", or "check".
        columns: Column name(s) this constraint applies to.
        references_table: For foreign keys — parent table name.
        references_columns: For foreign keys — parent column name(s).
        expression: For check constraints — SQL boolean expression.

    Example — Pets primary key (Animal.sql):

        Constraint("primary_key", columns=["id"])

    Example — Comments → Posts (Blog.sql):

        Constraint(
            "foreign_key",
            columns=["post_id"],
            references_table="Posts",
            references_columns=["id"],
        )
    """

    def __init__(
        self,
        kind: str,
        *,
        columns: list[str] | None = None,
        references_table: str | None = None,
        references_columns: list[str] | None = None,
        expression: str | None = None,
    ):
        self.kind = kind
        self.columns = columns or []
        self.references_table = references_table
        self.references_columns = references_columns or []
        self.expression = expression
