import asyncio
import time

from curl_cffi.requests import AsyncSession
from DrissionPage import ChromiumPage, ChromiumOptions

from pokecrawler.exceptions import FetchError

BASE_URL = "https://bulbapedia.bulbagarden.net"
_ARCHIVES_URL = "https://archives.bulbagarden.net"

_TIMEOUT = 30          # seconds per request
_RETRIES = 3
_BACKOFF = 1.0         # seconds × attempt number
_CHALLENGE_WAIT = 6    # seconds to wait for Turnstile to auto-resolve

_WARMUP_URLS = [
    BASE_URL,
    f"{_ARCHIVES_URL}/media/upload/thumb/f/fb/0001Bulbasaur.png/250px-0001Bulbasaur.png",
]

_SESSION: AsyncSession | None = None
_SESSION_LOCK = asyncio.Lock()


def _is_challenge(text: str) -> bool:
    snippet = text[:2000].lower()
    return "cloudflare" in snippet and ("momento" in snippet or "just a moment" in snippet)


def _collect_cookies_sync() -> tuple[list[dict], str]:
    page = ChromiumPage(addr_or_opts=ChromiumOptions())
    try:
        for url in _WARMUP_URLS:
            page.get(url)
            time.sleep(_CHALLENGE_WAIT)
        cookies = list(page.cookies())
        user_agent: str = page.run_js("return navigator.userAgent")
    finally:
        page.quit()
    return cookies, user_agent


async def _harvest_cookies() -> None:
    global _SESSION
    cookies, user_agent = await asyncio.to_thread(_collect_cookies_sync)
    session = AsyncSession(impersonate="chrome")
    session.headers["User-Agent"] = user_agent
    for c in cookies:
        session.cookies.set(
            c["name"],
            c["value"],
            domain=c.get("domain", ""),
            path=c.get("path", "/"),
        )
    _SESSION = session


async def get_session() -> AsyncSession:
    """Return the shared AsyncSession, harvesting cookies first if needed."""
    if _SESSION is None:
        async with _SESSION_LOCK:
            if _SESSION is None:
                await _harvest_cookies()
    assert _SESSION is not None
    return _SESSION


async def fetch(url: str) -> str:
    session = await get_session()
    last_exc: Exception | None = None

    for attempt in range(1, _RETRIES + 1):
        try:
            resp = await session.get(url, timeout=_TIMEOUT)

            if _is_challenge(resp.text) or resp.status_code in {403, 503}:
                if attempt < _RETRIES:
                    async with _SESSION_LOCK:
                        await _harvest_cookies()
                    session = await get_session()
                    continue
                raise Exception(f"Cloudflare challenge not resolved after {_RETRIES} attempts")

            resp.raise_for_status()
            return resp.text

        except FetchError:
            raise
        except Exception as exc:
            last_exc = exc
            if attempt < _RETRIES:
                await asyncio.sleep(_BACKOFF * attempt)

    raise FetchError(url, last_exc) from last_exc
