import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pokecrawler",
        description="Crawl Pokémon data from Bulbapedia and store it locally.",
    )
    parser.add_argument(
        "--start-url",
        default=None,
        metavar="URL",
        help="Starting Pokémon page URL (default: Bulbasaur).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        metavar="N",
        help="Maximum number of Pokémon to crawl (default: no limit).",
    )
    parser.add_argument(
        "--output",
        default="output",
        metavar="DIR",
        help="Output directory for JSON, images and database (default: output/).",
    )
    parser.add_argument(
        "--no-images",
        action="store_true",
        help="Skip image downloads.",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=5,
        metavar="N",
        help="Number of Pokémon to process concurrently in phase 2 (default: 5).",
    )
    parser.add_argument(
        "--pokemon",
        nargs="+",
        metavar="NAME",
        help=(
            "Crawl specific Pokémon by name (skips pagination). "
            "Example: --pokemon Bulbasaur Eevee. "
            "When provided, --start-url and --limit are ignored."
        ),
    )
    return parser
