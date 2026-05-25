import re
from pathlib import Path

from pokecrawler.exceptions import FetchError
from pokecrawler.http_client import get_session

_OUTPUT_DIR = Path("output/images")


def _slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def store_image(
    image_url: str,
    national_number: int,
    name: str,
    *,
    output_dir: Path = _OUTPUT_DIR,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)

    slug = _slugify(name)
    ext = Path(image_url.split("?")[0]).suffix or ".png"
    dest = output_dir / f"{national_number:04d}_{slug}{ext}"

    try:
        resp = get_session().get(image_url, timeout=30)
        resp.raise_for_status()
        dest.write_bytes(resp.content)
    except Exception as exc:
        raise FetchError(image_url, exc) from exc

    return dest
