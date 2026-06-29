"""Stored procedures and functions — server-side logic in the database.

Not used in the sample .sql files in this repo, but part of a full RDBMS
surface. Procedures encapsulate repeated SQL (reports, batch updates, validation)
and are invoked with CALL procedure_name(...).

Should contain:
    name: Procedure or function identifier.
    parameters: List of dicts or tuples — name, direction (IN/OUT/INOUT), type.
    body: SQL statements executed when the procedure runs.
    returns: For functions — return type; for procedures often None.

Example — count pets by species:

    Procedure(
        name="count_by_species",
        parameters=[
            {"name": "p_species", "direction": "IN", "type": "VARCHAR(20)"},
        ],
        body="""
            SELECT COUNT(*) FROM Pets WHERE species = p_species;
        """,
    )

Populate from CREATE PROCEDURE / CREATE FUNCTION definitions in SQL dumps or
migration scripts.
"""


class Procedure:
    """Named, parameterized SQL routine stored in the database."""

    def __init__(
        self,
        name: str,
        *,
        parameters: list | None = None,
        body: str = "",
        returns: str | None = None,
    ):
        self.name = name
        self.parameters = parameters or []
        self.body = body
        self.returns = returns
