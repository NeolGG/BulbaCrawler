from bs4 import BeautifulSoup, Tag

from pokecrawler.http_client import BASE_URL


def next_pokemon_url(soup: BeautifulSoup) -> str | None:
    for a in soup.find_all("a"):
        if not isinstance(a, Tag):
            continue
        if a.get_text(strip=True) != "→":
            continue
        title = a.get("title")
        if not isinstance(title, str) or "(Pokémon)" not in title:
            continue
        href = a.get("href")
        if not isinstance(href, str):
            continue
        return BASE_URL + href if href.startswith("/") else href
    return None
