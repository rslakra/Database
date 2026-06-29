"""Users, roles, and privileges — who may do what on which objects.

Access models GRANT/REVOKE and CREATE USER from scripts like GrantPermissions.sql.
It does not store table data; it controls connection and operation rights.

Should contain:
    principal: User or role (e.g. "username@localhost").
    privilege: Operation allowed — SELECT, INSERT, UPDATE, DELETE, ALL, etc.
    object_type: Scope — "database", "table", "procedure", or global "*".
    object_name: Qualified name (e.g. "Animal.Pets", "Library.*") or "*" for all.
    grant_option: True if the principal may grant this privilege to others.

Example — full access for a local user (GrantPermissions.sql):

    Access(
        principal="username@localhost",
        privilege="ALL",
        object_type="global",
        object_name="*.*",
    )

Example — read-only on one table:

    Access(
        principal="reader@localhost",
        privilege="SELECT",
        object_type="table",
        object_name="Animal.Pets",
    )

Populate from CREATE USER, GRANT, and REVOKE statements; flush or reload
privileges after changes in a live server.
"""


class Access:
    """One grant of a privilege to a principal on a database object."""

    def __init__(
        self,
        *,
        principal: str,
        privilege: str,
        object_type: str,
        object_name: str,
        grant_option: bool = False,
    ):
        self.principal = principal
        self.privilege = privilege
        self.object_type = object_type
        self.object_name = object_name
        self.grant_option = grant_option
