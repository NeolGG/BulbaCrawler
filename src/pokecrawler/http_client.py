import time

from curl_cffi.requests import Session
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

_SESSION: Session | None = None
_USER_AGENT: str = ""


def _is_challenge(text: str) -> bool:
    snippet = text[:2000].lower()
    return "cloudflare" in snippet and ("momento" in snippet or "just a moment" in snippet)


def _harvest_cookies() -> None:
    global _SESSION, _USER_AGENT

    page = ChromiumPage(addr_or_opts=ChromiumOptions())
    try:
        for url in _WARMUP_URLS:
            page.get(url)
            time.sleep(_CHALLENGE_WAIT)  # wait for Turnstile to auto-resolve

        all_cookies = page.cookies()
        _USER_AGENT = page.run_js("return navigator.userAgent")
    finally:
        page.quit()

    session = Session(impersonate="chrome")
    session.headers["User-Agent"] = _USER_AGENT
    for c in all_cookies:
        session.cookies.set(
            c["name"],
            c["value"],
            domain=c.get("domain", ""),
            path=c.get("path", "/"),
        )
    _SESSION = session


def get_session() -> Session:
    if _SESSION is None:
        _harvest_cookies()
    assert _SESSION is not None
    return _SESSION


def fetch(url: str) -> str:
    session = get_session()
    last_exc: Exception | None = None

    for attempt in range(1, _RETRIES + 1):
        try:
            resp = session.get(url, timeout=_TIMEOUT)

            if _is_challenge(resp.text) or resp.status_code in {403, 503}:
                if attempt < _RETRIES:
                    _harvest_cookies()
                    session = get_session()
                    continue
                raise Exception(f"Cloudflare challenge not resolved after {_RETRIES} attempts")

            resp.raise_for_status()
            return resp.text

        except FetchError:
            raise
        except Exception as exc:
            last_exc = exc
            if attempt < _RETRIES:
                time.sleep(_BACKOFF * attempt)

    raise FetchError(url, last_exc) from last_exc
