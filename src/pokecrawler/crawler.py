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


async def crawl(
    start_url: str,
    conn: sqlite3.Connection,
    *,
    limit: int | None = None,
    json_path: Path = Path("output/pokemons.json"),
    image_dir: Path = Path("output/images"),
) -> list[Pokemon]:
    pokemons: list[Pokemon] = []
    url: str | None = start_url
    count = 0

    while url is not None:
        if limit is not None and count >= limit:
            break

        logger.info("[%d] fetching %s", count + 1, url)

        try:
            html = await fetch(url)
        except FetchError as exc:
            logger.error("fetch failed, stopping crawl: %s", exc)
            break

        soup = BeautifulSoup(html, "html.parser")
        clean(soup)

        next_url = next_pokemon_url(soup)

        try:
            raw = parse_page(soup)
            pokemon = to_pokemon(raw)
        except NormalizationError as exc:
            logger.error("normalization failed for %s, skipping: %s", url, exc)
            url = next_url
            continue

        image_url = raw.get("image_url")
        if isinstance(image_url, str):
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
        pokemons.append(pokemon)
        count += 1

        logger.info(
            "saved %s (#%03d) — %d total", pokemon.name, pokemon.national_number, count
        )

        url = next_url

    write_json(pokemons, json_path)
    logger.info("crawl complete — %d Pokémon saved", len(pokemons))
    return pokemons
