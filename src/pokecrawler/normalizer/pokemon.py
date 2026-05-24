from typing import Any

from pokecrawler.exceptions import NormalizationError
from pokecrawler.models.pokemon import Evolution, Pokemon, Stats
from pokecrawler.normalizer.primitives import clean_str, to_int, to_list

_POKEMON_SUFFIX = " (Pokémon)"


def _normalize_name(raw: Any) -> str:
    if not isinstance(raw, str) or not raw.strip():
        raise NormalizationError("name", raw)
    return raw.replace(_POKEMON_SUFFIX, "").strip()


def _normalize_national_number(raw: Any) -> int:
    value = to_int(raw)
    if value is None:
        raise NormalizationError("national_number", raw)
    return value


def _normalize_stats(raw: Any) -> Stats:
    data: dict[str, Any] = raw if isinstance(raw, dict) else {}
    return Stats(
        hp=to_int(data.get("hp")) or 0,
        attack=to_int(data.get("attack")) or 0,
        defense=to_int(data.get("defense")) or 0,
        sp_atk=to_int(data.get("sp_atk")) or 0,
        sp_def=to_int(data.get("sp_def")) or 0,
        speed=to_int(data.get("speed")) or 0,
    )


def _normalize_evolution(raw: Any) -> Evolution:
    data: dict[str, Any] = raw if isinstance(raw, dict) else {}
    return Evolution(
        predecessors=to_list(data.get("predecessors")),
        successors=to_list(data.get("successors")),
    )


def to_pokemon(raw: dict[str, Any]) -> Pokemon:
    return Pokemon(
        name=_normalize_name(raw.get("name")),
        national_number=_normalize_national_number(raw.get("national_number")),
        category=clean_str(raw.get("category")) or "",
        types=list(dict.fromkeys(to_list(raw.get("types"), drop=("Unknown",)))),
        stats=_normalize_stats(raw.get("stats")),
        evolution=_normalize_evolution(raw.get("evolution")),
        image_local=None,  # set later by image_store
    )
