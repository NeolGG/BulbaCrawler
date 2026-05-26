from pokecrawler.http_client import BASE_URL
from pokecrawler.urls import build_pokemon_url


class TestBuildPokemonUrl:
    def test_simple_name(self):
        assert (
            build_pokemon_url("Bulbasaur")
            == f"{BASE_URL}/wiki/Bulbasaur_(Pok%C3%A9mon)"
        )

    def test_name_with_apostrophe(self):
        url = build_pokemon_url("Farfetch'd")
        assert url == f"{BASE_URL}/wiki/Farfetch%27d_(Pok%C3%A9mon)"

    def test_name_with_space(self):
        url = build_pokemon_url("Mr. Mime")
        assert url == f"{BASE_URL}/wiki/Mr.%20Mime_(Pok%C3%A9mon)"

    def test_name_with_unicode(self):
        url = build_pokemon_url("Nidoran♀")
        assert "Nidoran" in url
        assert url.endswith("_(Pok%C3%A9mon)")

    def test_name_with_hyphen(self):
        url = build_pokemon_url("Ho-Oh")
        assert url == f"{BASE_URL}/wiki/Ho-Oh_(Pok%C3%A9mon)"
