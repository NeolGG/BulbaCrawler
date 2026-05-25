import json
from pathlib import Path

from pokecrawler.models.pokemon import Pokemon

_OUTPUT_FILE = Path("output/pokemons.json")


def write_json(pokemons: list[Pokemon], path: Path = _OUTPUT_FILE) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [p.model_dump(mode="json") for p in pokemons]
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
