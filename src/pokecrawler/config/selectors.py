from typing import Any

type Op = tuple[str, *tuple[Any, ...]]
type Pipeline = list[Op]
type Spec = dict[str, Pipeline]

_INFOBOX: Op = ("find", "table", {"class": "infobox"})

POKEMON_SPEC: Spec = {
    "name": [
        ("find", "h1", {"id": "firstHeading"}),
        ("text",),
    ],
    "national_number": [
        _INFOBOX,
        ("find", "a", {"title": "List of Pokémon by National Pokédex number"}),
        ("find", "span"),
        ("text",),
    ],
    "category": [
        _INFOBOX,
        ("find_where_attr_contains", "a", "title", "category"),
        ("find", "span"),
        ("text",),
    ],
    "types": [
        _INFOBOX,
        ("select", "td[width='45px'] > a > span > b"),
        ("text_all",),
    ],
    "image_url": [
        _INFOBOX,
        ("find", "img"),
        ("attr", "src"),
    ],
}
