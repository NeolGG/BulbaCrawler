from bs4 import BeautifulSoup, Tag


def _normalize(name: str) -> str:
    return name.replace(" (Pokémon)", "").strip()


def extract_evolution_chain(
    soup: BeautifulSoup, current_name: str
) -> dict[str, list[str]]:

    current_name = _normalize(current_name)
    chain: list[str] = []

    for block in soup.find_all("td"):
        img = block.find("img")
        a = block.find("a", title=True)

        if not img or not a or not isinstance(a, Tag):
            continue

        raw_title = a.get("title")
        if not isinstance(raw_title, str) or not raw_title:
            continue

        if any(skip in raw_title.lower() for skip in ["learnset", "generation", "list of"]):
            continue

        if "(Pokémon)" in raw_title:
            chain.append(_normalize(raw_title))

    chain = list(dict.fromkeys(chain))

    if current_name not in chain:
        return {"predecessors": [], "successors": chain}

    idx = chain.index(current_name)
    return {"predecessors": chain[:idx], "successors": chain[idx + 1:]}
