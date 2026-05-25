from typing import Any


class PokeCrawlerError(Exception):
    pass


class NormalizationError(PokeCrawlerError):
    def __init__(self, field: str, value: Any = None) -> None:
        super().__init__(f"Failed to normalize required field '{field}': {value!r}")
        self.field = field
        self.value = value


class FetchError(PokeCrawlerError):
    def __init__(self, url: str, cause: Exception | None = None) -> None:
        msg = f"Failed to fetch {url!r}"
        if cause:
            msg += f": {cause}"
        super().__init__(msg)
        self.url = url
