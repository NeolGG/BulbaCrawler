import asyncio
import logging
import sqlite3
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

logger = logging.getLogger(__name__)

FIRST_POKEMON_URL = f"{BASE_URL}/wiki/Bulbasaur_(Pok%C3%A9mon)"


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


async def crawl(
    start_url: str,
    conn: sqlite3.Connection,
    *,
    limit: int | None = None,
    concurrency: int = 5,
    json_path: Path = Path("output/pokemons.json"),
    image_dir: Path = Path("output/images"),
    skip_images: bool = False,
) -> list[Pokemon]:
    logger.info("phase 1: collecting pages (sequential)...")
    pages: list[tuple[str, str]] = []
    url: str | None = start_url

    while url is not None:
        if limit is not None and len(pages) >= limit:
            break

        logger.info("[%d] fetching %s", len(pages) + 1, url)
        try:
            html = await fetch(url)
        except FetchError as exc:
            logger.error("fetch failed, stopping crawl: %s", exc)
            break

        soup = BeautifulSoup(html, "html.parser")
        next_url = next_pokemon_url(soup)
        pages.append((url, html))
        url = next_url

    logger.info("phase 1 complete — %d pages buffered", len(pages))

    logger.info("phase 2: processing concurrently (concurrency=%d)...", concurrency)
    sem = asyncio.Semaphore(concurrency)

    results = await asyncio.gather(
        *[
            _process_one(url, html, conn, sem, image_dir=image_dir, skip_images=skip_images)
            for url, html in pages
        ]
    )

    pokemons = sorted(
        [p for p in results if p is not None],
        key=lambda p: p.national_number,
    )

    write_json(pokemons, json_path)
    logger.info("crawl complete — %d Pokémon saved", len(pokemons))
    return pokemons
