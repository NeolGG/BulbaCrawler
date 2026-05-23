from typing import Any

from bs4 import BeautifulSoup

from pokecrawler.config.selectors import POKEMON_SPEC, Spec
from pokecrawler.config.taxonomy import STAT_LABELS
from pokecrawler.parser import operations as ops
from pokecrawler.parser.evolution import extract_evolution_chain


def _apply_op(ctx: Any, op: tuple) -> Any:
    name, *args = op
    match name:
        case "find":
            return ops.op_find(ctx, *args)
        case "find_all":
            return ops.op_find_all(ctx, *args)
        case "find_where_attr_contains":
            return ops.op_find_where_attr_contains(ctx, *args)
        case "select":
            return ops.op_select(ctx, *args)
        case "attr":
            return ops.op_attr(ctx, *args)
        case "text":
            return ops.op_text(ctx)
        case "text_all":
            return ops.op_text_all(ctx)
        case _:
            raise ValueError(f"Unknown operation: {name!r}")


def run_spec(soup: BeautifulSoup, spec: Spec = POKEMON_SPEC) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for field, pipeline in spec.items():
        ctx: Any = soup
        for op in pipeline:
            ctx = _apply_op(ctx, op)
            if ctx is None:
                break
        result[field] = ctx
    return result


def parse_stats(soup: BeautifulSoup) -> dict[str, str]:
    infobox = soup.find("table", {"class": "infobox"})
    if not infobox:
        return {}

    stats: dict[str, str] = {}

    for row in infobox.find_all("tr"):
        for td in row.find_all("td", class_="roundy"):
            small = td.find("small")
            if not small:
                continue

            label = small.get_text(strip=True)
            canonical = STAT_LABELS.get(label)
            if not canonical:
                continue

            raw_value = td.find(string=True, recursive=False)
            if raw_value and raw_value.strip().isdigit():
                stats[canonical] = raw_value.strip()

    return stats


def parse_page(soup: BeautifulSoup) -> dict[str, Any]:
    data = run_spec(soup)
    data["stats"] = parse_stats(soup)
    data["evolution"] = extract_evolution_chain(soup, data.get("name") or "")
    return data
