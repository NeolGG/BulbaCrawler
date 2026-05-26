import json
from pathlib import Path

from pokecrawler.exporter import write_json
from pokecrawler.models.pokemon import Evolution, Pokemon, Stats


def _make_pokemon(number: int, name: str) -> Pokemon:
    return Pokemon(
        name=name,
        national_number=number,
        category="Test",
        types=["Normal"],
        stats=Stats(hp=1, attack=1, defense=1, sp_atk=1, sp_def=1, speed=1),
        evolution=Evolution(),
    )


class TestWriteJson:
    def test_creates_file(self, tmp_path: Path):
        out = tmp_path / "pokemons.json"
        write_json([_make_pokemon(1, "Bulbasaur")], out)
        assert out.exists()

    def test_output_is_valid_json_array(self, tmp_path: Path):
        out = tmp_path / "pokemons.json"
        write_json([_make_pokemon(1, "Bulbasaur"), _make_pokemon(2, "Ivysaur")], out)
        data = json.loads(out.read_text(encoding="utf-8"))
        assert isinstance(data, list)
        assert len(data) == 2

    def test_fields_are_serialized(self, tmp_path: Path):
        out = tmp_path / "pokemons.json"
        write_json([_make_pokemon(1, "Bulbasaur")], out)
        data = json.loads(out.read_text(encoding="utf-8"))
        assert data[0]["name"] == "Bulbasaur"
        assert data[0]["national_number"] == 1

    def test_utf8_characters_not_escaped(self, tmp_path: Path):
        out = tmp_path / "pokemons.json"
        write_json([_make_pokemon(29, "Nidoran♀")], out)
        content = out.read_text(encoding="utf-8")
        assert "Nidoran♀" in content

    def test_creates_parent_directories(self, tmp_path: Path):
        out = tmp_path / "nested" / "dir" / "pokemons.json"
        write_json([_make_pokemon(1, "Bulbasaur")], out)
        assert out.exists()

    def test_empty_list(self, tmp_path: Path):
        out = tmp_path / "pokemons.json"
        write_json([], out)
        data = json.loads(out.read_text(encoding="utf-8"))
        assert data == []
