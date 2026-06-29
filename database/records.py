"""Row-level data — one tuple of values for a table.

A Record is the in-memory counterpart of INSERT INTO ... VALUES (...). Values
are keyed by column name and must match the parent Table's Attribute definitions
(types, nullability, defaults).

Should contain:
    table: Table this row belongs to (defines valid column names).
    values: dict mapping column name -> Python/SQL value.

Rules when populating:
    - Include every NOT NULL column without a DEFAULT (unless DB assigns one).
    - Omit AUTO_INCREMENT keys (e.g. id) so the database generates them.
    - Use None for SQL NULL (e.g. death when the pet is still alive).
    - Respect foreign keys: post_id must exist in Posts.id (Blog.sql).

Example — one Pets row (Animal.sql):

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

Example — Posts row (Blog.sql):

    Record(
        table=posts,
        values={
            "title": "Java",
            "body": "Java is an object oriented language",
            "email": "diana@gmail.com",
        },
    )

Bulk load: build a list of Record objects from each INSERT in a .sql script.
"""


class Record:
    """One row of data for a given Table."""

    def __init__(self, *, table, values: dict):
        self.table = table
        self.values = values
