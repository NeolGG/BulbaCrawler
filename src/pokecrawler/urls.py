from urllib.parse import quote

from pokecrawler.http_client import BASE_URL


def build_pokemon_url(name: str) -> str:
    return f"{BASE_URL}/wiki/{quote(name)}_(Pok%C3%A9mon)"

def build_trainer_url(name: str) -> str:
    return f"{BASE_URL}/wiki/{quote(name)}"