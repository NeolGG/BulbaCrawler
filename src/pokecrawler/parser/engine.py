from typing import Any

from bs4 import BeautifulSoup, Tag

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


def _find_stats_table(headline: Tag) -> Tag | None:
    for table in headline.find_all_next("table"):
        if not isinstance(table, Tag):
            continue
        for row in table.find_all("tr"):
            th = row.find("th")
            if not isinstance(th, Tag):
                continue
            divs = th.find_all("div", recursive=False)
            if len(divs) >= 2 and divs[0].find("a"):
                return table
    return None


def parse_stats(soup: BeautifulSoup) -> dict[str, str]:
    headline = soup.find("span", {"id": "Base_stats"})
    if not isinstance(headline, Tag):
        return {}

    table = _find_stats_table(headline)
    if table is None:
        return {}

    stats: dict[str, str] = {}
    for row in table.find_all("tr"):
        th = row.find("th")
        if not isinstance(th, Tag):
            continue
        divs = th.find_all("div", recursive=False)
        if len(divs) < 2:
            continue
        link = divs[0].find("a")
        if not isinstance(link, Tag):
            continue
        stat_name = link.get_text(strip=True)
        canonical = STAT_LABELS.get(stat_name)
        if not canonical:
            continue
        value = divs[1].get_text(strip=True)
        if value.isdigit():
            stats[canonical] = value
    return stats


def parse_page(soup: BeautifulSoup) -> dict[str, Any]:
    data = run_spec(soup)
    data["stats"] = parse_stats(soup)
    data["evolution"] = extract_evolution_chain(soup, data.get("name") or "")
    return data
