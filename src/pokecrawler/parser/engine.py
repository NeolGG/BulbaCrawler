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


def parse_abilities(soup: BeautifulSoup) -> list[dict[str, Any]]:
    infobox = soup.find("table", {"class": "infobox"})
    if not isinstance(infobox, Tag):
        return []

    abilities_container: Tag | None = None
    for td in infobox.find_all("td", class_="roundy"):
        if not isinstance(td, Tag):
            continue
        if td.find("a", title="Ability"):
            abilities_container = td
            break

    if abilities_container is None:
        return []

    seen: set[str] = set()
    result: list[dict[str, Any]] = []

    for cell in abilities_container.find_all("td"):
        if not isinstance(cell, Tag):
            continue
        small = cell.find("small")
        is_hidden = (
            isinstance(small, Tag)
            and "hidden ability" in small.get_text(strip=True).lower()
        )
        for link in cell.find_all(
            "a", title=lambda t: isinstance(t, str) and "(Ability)" in t
        ):
            raw_title = link.get("title")
            if not isinstance(raw_title, str):
                continue
            name = raw_title.replace(" (Ability)", "").strip()
            if not name or name in seen:
                continue
            seen.add(name)
            result.append({"name": name, "is_hidden": is_hidden})

    return result


def parse_page(soup: BeautifulSoup) -> dict[str, Any]:
    data = run_spec(soup)
    data["stats"] = parse_stats(soup)
    data["abilities"] = parse_abilities(soup)
    data["evolution"] = extract_evolution_chain(soup, data.get("name") or "")
    return data
