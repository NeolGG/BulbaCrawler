from bs4 import BeautifulSoup, Tag


def clean(soup: BeautifulSoup) -> BeautifulSoup:
    to_remove: list[Tag] = []

    for tag in soup.find_all(style=True):
        if not isinstance(tag, Tag):
            continue
        style = tag.get("style", "")
        if isinstance(style, str) and "display:none" in style.replace(" ", "").lower():
            to_remove.append(tag)

    for tag in to_remove:
        tag.decompose()

    return soup
