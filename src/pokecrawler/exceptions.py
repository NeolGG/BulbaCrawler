from typing import Any


class PokeCrawlerError(Exception):
    pass


class NormalizationError(PokeCrawlerError):
    def __init__(self, field: str, value: Any = None) -> None:
        super().__init__(f"Failed to normalize required field '{field}': {value!r}")
        self.field = field
        self.value = value
