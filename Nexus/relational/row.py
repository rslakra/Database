"""SQL row — one INSERT tuple."""


class Row:
    def __init__(self, *, table, values: dict):
        self.table = table
        self.values = values


# Backward-compatible alias
Record = Row
