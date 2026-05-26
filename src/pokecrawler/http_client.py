import asyncio

import httpx

from pokecrawler.exceptions import FetchError

BASE_URL = "https://bulbapedia.bulbagarden.net"

_TIMEOUT = 30  # seconds per request
_RETRIES = 3
_BACKOFF = 1.0  # seconds × attempt number

_CLIENT: httpx.AsyncClient | None = None
_CLIENT_LOCK = asyncio.Lock()


async def get_client() -> httpx.AsyncClient:
    global _CLIENT
    if _CLIENT is None:
        async with _CLIENT_LOCK:
            if _CLIENT is None:
                _CLIENT = httpx.AsyncClient(
                    headers={"User-Agent": "Mozilla/5.0 (compatible; pokecrawler/0.1)"},
                    follow_redirects=True,
                    timeout=_TIMEOUT,
                )
    assert _CLIENT is not None
    return _CLIENT


async def fetch(url: str) -> str:
    client = await get_client()
    last_exc: Exception | None = None

    for attempt in range(1, _RETRIES + 1):
        try:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.text
        except FetchError:
            raise
        except Exception as exc:
            last_exc = exc
            if attempt < _RETRIES:
                await asyncio.sleep(_BACKOFF * attempt)

    raise FetchError(url, last_exc) from last_exc
