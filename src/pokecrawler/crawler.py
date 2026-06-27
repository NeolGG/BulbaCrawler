import asyncio
import logging
import sqlite3
import re
from pathlib import Path

from bs4 import BeautifulSoup

from pokecrawler.database import upsert_pokemon
from pokecrawler.exceptions import FetchError, NormalizationError
from pokecrawler.exporter import write_json
from pokecrawler.http_client import BASE_URL, fetch
from pokecrawler.image_store import store_image
from pokecrawler.models.pokemon import Pokemon
from pokecrawler.normalizer import to_pokemon
from pokecrawler.pagination import next_pokemon_url
from pokecrawler.parser.engine import parse_page
from pokecrawler.sanitizer.html_cleaner import clean
from pokecrawler.urls import build_pokemon_url

logger = logging.getLogger(__name__)

FIRST_POKEMON_URL = f"{BASE_URL}/wiki/Bulbasaur_(Pok%C3%A9mon)"
FIRST_PAGE = f"{BASE_URL}/wiki/Category:Pok%C3%A9mon"

async def _process_one(
    url: str,
    html: str,
    conn: sqlite3.Connection,
    sem: asyncio.Semaphore,
    *,
    image_dir: Path,
    skip_images: bool,
) -> Pokemon | None:
    async with sem:
        soup = BeautifulSoup(html, "html.parser")
        clean(soup)

        try:
            raw = parse_page(soup)
            pokemon = to_pokemon(raw)
        except NormalizationError as exc:
            logger.error("normalization failed for %s, skipping: %s", url, exc)
            return None

        image_url = raw.get("image_url")
        if not skip_images and isinstance(image_url, str):
            try:
                path = await store_image(
                    image_url,
                    pokemon.national_number,
                    pokemon.name,
                    output_dir=image_dir,
                )
                pokemon = pokemon.model_copy(update={"image_local": path})
            except FetchError as exc:
                logger.warning("image download failed for %s: %s", pokemon.name, exc)

        upsert_pokemon(conn, pokemon)
        logger.info("saved %s (#%03d)", pokemon.name, pokemon.national_number)
        return pokemon

async def _collect_via_pagination(
    concurrency: int
) -> list[tuple[str, str]]:
    object_urls= await _get_all_pokemon_urls()
    sem = asyncio.Semaphore(concurrency)
    
    async def fetch_one(object_url: str) -> tuple[str, str] | None:
        async with sem:
            logger.info("fetching %s", object_url)
            try:
                html = await fetch(object_url)
            except FetchError as exc:
                logger.error("skipping %s: %s", object_url, exc)
                return None
            return (object_url, html)

    results = await asyncio.gather(*[fetch_one(n) for n in object_urls])
    ret = [r for r in results if r is not None]
    return ret

async def _collect_from_names(
    names: list[str], concurrency: int
) -> list[tuple[str, str]]:
    sem = asyncio.Semaphore(concurrency)

    async def fetch_one(name: str) -> tuple[str, str] | None:
        url = build_pokemon_url(name)
        async with sem:
            logger.info("fetching %s", url)
            try:
                html = await fetch(url)
            except FetchError as exc:
                logger.error("skipping %s: %s", name, exc)
                return None
            return (url, html)

    results = await asyncio.gather(*[fetch_one(n) for n in names])
    return [r for r in results if r is not None]

def _get_pokemon_on_page(soup: BeautifulSoup) -> tuple[list[str], str | None]:
    urls = []
    h2 = soup.find("h2", string=re.compile(r'Pages in category\s+"Pokémon"'))
    if not h2:
        return (urls, None)
    container = h2.find_parent("div")
    if not container: 
        return (urls, None)
    
    for a in container.find_all("a"):
        text = a.get_text()
        href = a.get("href")
        if text and "(Pokémon)" in text and href:
            urls.append(BASE_URL + href)

    next_link = soup.find("a", string="next page")
    next_url = (BASE_URL + next_link.get("href")) if next_link else None
    return (urls, next_url)

async def _get_all_pokemon_urls() -> list:
    next_url = FIRST_PAGE
    urls = []
    while next_url:
        html = await fetch(next_url)
        soup = BeautifulSoup(html, "html.parser")
        output, next_url = _get_pokemon_on_page(soup)
        urls += output        
    return urls

async def crawl(
    conn: sqlite3.Connection,
    *,
    start_url: str | None = None, # todo: implement
    pokemons: list[str] | None = None,
    limit: int | None = None, # todo: implement?
    concurrency: int = 5,
    json_path: Path = Path("output/pokemons.json"),
    image_dir: Path = Path("output/images"),
    skip_images: bool = False,
) -> list[Pokemon]:
    if pokemons:
        logger.info(
            "phase 1: fetching %d Pokémon by name (concurrent)...", len(pokemons)
        )
        pages = await _collect_from_names(pokemons, concurrency)
    else:
        logger.info(
            "phase 1: collecting pages via pagination (concurrent)..."
        )
        pages = await _collect_via_pagination(concurrency)
        
    logger.info("phase 1 complete — %d pages buffered", len(pages))
    logger.info("phase 2: processing concurrently (concurrency=%d)...", concurrency)
    sem = asyncio.Semaphore(concurrency)

    results = await asyncio.gather(
        *[
            _process_one(
                url, html, conn, sem, image_dir=image_dir, skip_images=skip_images
            )
            for url, html in pages
        ]
    )

    pokemons_result = sorted(
        [p for p in results if p is not None],
        key=lambda p: p.national_number,
    )

    write_json(pokemons_result, json_path)
    logger.info("crawl complete — %d Pokémon saved", len(pokemons_result))
    return pokemons_result
