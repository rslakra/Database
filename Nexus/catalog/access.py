"""User grants and privileges."""


class Access:
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
