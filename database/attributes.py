"""Column (field) definitions for a relational table.

An Attribute maps to one column in a CREATE TABLE statement. Tables are built
from a list of Attributes; each Attribute describes name, type, and column-level
rules before any rows exist.

Example from Animal.sql — the Pets table columns:

    id      = Attribute("id", "INT", nullable=False, auto_increment=True)
    name    = Attribute("name", "VARCHAR(20)", nullable=False)
    owner   = Attribute("owner", "VARCHAR(20)")          # nullable by default
    species = Attribute("species", "VARCHAR(20)")
    sex     = Attribute("sex", "CHAR(1)")
    birth   = Attribute("birth", "DATE")
    death   = Attribute("death", "DATE")

Populate by mirroring each column in CREATE TABLE: name, SQL type, NOT NULL,
DEFAULT, and AUTO_INCREMENT flags.
"""


class Attribute:
    """One column in a table schema.

    Should contain:
        name: Column identifier (e.g. "name", "email", "created_on").
        data_type: SQL type string (e.g. "INT", "VARCHAR(20)", "DATE", "TEXT").
        nullable: False when the column is NOT NULL.
        default: Literal or expression (e.g. None, "CURRENT_TIMESTAMP").
        auto_increment: True for AUTO_INCREMENT integer keys.

    Does not hold row values — use Record for actual data.
    """

    def __init__(
        self,
        name: str,
        data_type: str,
        *,
        nullable: bool = True,
        default=None,
        auto_increment: bool = False,
    ):
        self.name = name
        self.data_type = data_type
        self.nullable = nullable
        self.default = default
        self.auto_increment = auto_increment
