import asyncio
import logging
import time
from pathlib import Path

from pokecrawler.cli import build_parser
from pokecrawler.crawler import crawl
from pokecrawler.database import init_db
from pokecrawler.http_client import get_client


def _setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )


async def _main() -> None:
    args = build_parser().parse_args()

    _setup_logging()

    output = Path(args.output)

    conn = init_db(output / "pokedex.db")

    start = time.perf_counter()
    pokemons = await crawl(
        conn,
        start_url=args.start_url,
        object_list=args.pokemon,
        limit=args.limit,
        concurrency=args.concurrency,
        json_path=output / "pokemons.json",
        image_dir=output / "images",
        skip_images=args.no_images,
        object_type=args.type
    )
    elapsed = time.perf_counter() - start

    conn.close()
    client = await get_client()
    await client.aclose()

    count = len(pokemons)
    per_pokemon = elapsed / count if count else 0
    print(f"\nCrawled {count} Pokémon in {elapsed:.1f}s ({per_pokemon:.2f}s/Pokémon).")


def main() -> None:
    asyncio.run(_main())


if __name__ == "__main__":
    main()
