from bs4 import BeautifulSoup, Tag

_STAGE_ORDER: dict[str, int] = {
    "unevolved": 0,
    "first evolution": 1,
    "second evolution": 2,
    "third evolution": 3,
}


def _normalize(name: str) -> str:
    return name.replace(" (Pokémon)", "").strip()


def _find_evolution_container(soup: BeautifulSoup) -> Tag | None:
    headline = soup.find("span", {"id": "Evolution"})
    if not isinstance(headline, Tag):
        return None

    for tag in headline.find_all_next(["div", "table", "h2", "h3"]):
        if not isinstance(tag, Tag):
            continue
        if tag.name in ("h2", "h3"):
            break
        has_sprite = tag.find("img") is not None
        has_link = (
            tag.find("a", title=lambda t: isinstance(t, str) and "(Pokémon)" in t)
            is not None
        )
        if has_sprite and has_link:
            return tag

    return None


def _get_stage(table: Tag) -> int:
    for s in table.find_all("small"):
        if not s.find("a"):
            label = s.get_text(strip=True).lower()
            return _STAGE_ORDER.get(label, -1)
    return -1


def _extract_entry(table: Tag) -> tuple[str | None, bool, int] | None:
    if table.find("table"):
        return None
    if not table.find("img"):
        return None
    if not any(not s.find("a") for s in table.find_all("small")):
        return None

    stage = _get_stage(table)

    if table.find("a", class_="mw-selflink"):
        return (None, True, stage)

    link = table.find("a", title=lambda t: isinstance(t, str) and "(Pokémon)" in t)
    if isinstance(link, Tag):
        title = link.get("title")
        if isinstance(title, str):
            return (_normalize(title), False, stage)

    return None


def extract_evolution_chain(
    soup: BeautifulSoup, current_name: str
) -> dict[str, list[str]]:
    current_name = _normalize(current_name)

    container = _find_evolution_container(soup)
    if container is None:
        return {"predecessors": [], "successors": []}

    entries: list[tuple[str | None, bool, int]] = []
    seen: set[str] = set()

    for table in container.find_all("table"):
        entry = _extract_entry(table)
        if entry is None:
            continue
        name, is_current, stage = entry
        key = "__current__" if is_current else (name or "")
        if key and key not in seen:
            seen.add(key)
            entries.append(entry)

    pivot = next(
        (i for i, (_, is_current, _) in enumerate(entries) if is_current), None
    )

    if pivot is None:
        return {
            "predecessors": [],
            "successors": [n for n, _, _ in entries if n],
        }

    selflink_stage = entries[pivot][2]

    predecessors: list[str] = []
    successors: list[str] = []

    for name, _, stage in entries[:pivot]:
        if name:
            if stage < selflink_stage:
                predecessors.append(name)
            else:
                successors.append(name)

    for name, _, _ in entries[pivot + 1 :]:
        if name:
            successors.append(name)

    return {"predecessors": predecessors, "successors": successors}
