"""Stored procedure metadata."""


class Procedure:
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
