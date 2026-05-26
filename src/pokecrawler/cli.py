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
    return parser
