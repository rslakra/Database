"""Secondary access paths for faster lookups on a table.

A PRIMARY KEY creates an index automatically; Index models additional indexes
(KEY, INDEX, UNIQUE INDEX) you add for query performance.

Should contain:
    name: Optional index name (MySQL may auto-generate if omitted).
    table_name: Table the index belongs to.
    columns: Ordered list of indexed column names.
    unique: True for UNIQUE INDEX / UNIQUE KEY.

Example — speed up lookups by owner on Pets:

    Index("idx_pets_owner", table_name="Pets", columns=["owner"])

Example — enforce uniqueness on email (Library.sql Users table):

    Index("idx_users_email", table_name="Users", columns=["email"], unique=True)

Populate from CREATE INDEX, or INDEX/KEY clauses inside CREATE TABLE.
"""


class Index:
    """Non-primary index on one or more columns."""

    def __init__(
        self,
        name: str,
        *,
        table_name: str,
        columns: list[str],
        unique: bool = False,
    ):
        self.name = name
        self.table_name = table_name
        self.columns = columns
        self.unique = unique
