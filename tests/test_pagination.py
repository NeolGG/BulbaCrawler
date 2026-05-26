from bs4 import BeautifulSoup

from pokecrawler.http_client import BASE_URL
from pokecrawler.pagination import next_pokemon_url


class TestNextPokemonUrl:
    def test_finds_next_url(self):
        html = '<a title="Ivysaur (Pokémon)" href="/wiki/Ivysaur_(Pok%C3%A9mon)">→</a>'
        soup = BeautifulSoup(html, "html.parser")
        url = next_pokemon_url(soup)
        assert url == f"{BASE_URL}/wiki/Ivysaur_(Pok%C3%A9mon)"

    def test_returns_none_when_no_arrow(self):
        soup = BeautifulSoup('<a title="Something">←</a>', "html.parser")
        assert next_pokemon_url(soup) is None

    def test_returns_none_when_no_pokemon_title(self):
        soup = BeautifulSoup('<a title="Some other page">→</a>', "html.parser")
        assert next_pokemon_url(soup) is None

    def test_absolute_href_returned_as_is(self):
        url = "https://bulbapedia.bulbagarden.net/wiki/Ivysaur_(Pok%C3%A9mon)"
        html = f'<a title="Ivysaur (Pokémon)" href="{url}">→</a>'
        soup = BeautifulSoup(html, "html.parser")
        assert next_pokemon_url(soup) == url

    def test_takes_first_matching_arrow(self):
        html = """
        <a title="Ivysaur (Pokémon)" href="/wiki/Ivysaur_(Pok%C3%A9mon)">→</a>
        <a title="Venusaur (Pokémon)" href="/wiki/Venusaur_(Pok%C3%A9mon)">→</a>
        """
        soup = BeautifulSoup(html, "html.parser")
        url = next_pokemon_url(soup)
        assert url is not None and "Ivysaur" in url
