import pytest

from pokecrawler.exceptions import NormalizationError
from pokecrawler.normalizer.pokemon import to_pokemon

_VALID_RAW: dict = {
    "name": "Bulbasaur (Pokémon)",
    "national_number": "1",
    "category": "Seed Pokémon",
    "types": ["Grass", "Poison"],
    "stats": {
        "hp": "45",
        "attack": "49",
        "defense": "49",
        "sp_atk": "65",
        "sp_def": "65",
        "speed": "45",
    },
    "abilities": [
        {"name": "Overgrow", "is_hidden": False},
        {"name": "Chlorophyll", "is_hidden": True},
    ],
    "evolution": {"predecessors": [], "successors": ["Ivysaur", "Venusaur"]},
}


class TestToPokemon:
    def test_name_strips_suffix(self):
        p = to_pokemon(_VALID_RAW)
        assert p.name == "Bulbasaur"

    def test_national_number(self):
        p = to_pokemon(_VALID_RAW)
        assert p.national_number == 1

    def test_types(self):
        p = to_pokemon(_VALID_RAW)
        assert p.types == ["Grass", "Poison"]

    def test_deduplicates_types(self):
        raw = {**_VALID_RAW, "types": ["Grass", "Grass", "Poison"]}
        p = to_pokemon(raw)
        assert p.types == ["Grass", "Poison"]

    def test_drops_unknown_type(self):
        raw = {**_VALID_RAW, "types": ["Grass", "Unknown"]}
        p = to_pokemon(raw)
        assert "Unknown" not in p.types

    def test_stats(self):
        p = to_pokemon(_VALID_RAW)
        assert p.stats.hp == 45
        assert p.stats.attack == 49
        assert p.stats.speed == 45

    def test_abilities_count(self):
        p = to_pokemon(_VALID_RAW)
        assert len(p.abilities) == 2

    def test_ability_hidden_flag(self):
        p = to_pokemon(_VALID_RAW)
        assert p.abilities[0].is_hidden is False
        assert p.abilities[1].is_hidden is True

    def test_evolution_successors(self):
        p = to_pokemon(_VALID_RAW)
        assert p.evolution.successors == ["Ivysaur", "Venusaur"]
        assert p.evolution.predecessors == []

    def test_missing_name_raises(self):
        with pytest.raises(NormalizationError):
            to_pokemon({**_VALID_RAW, "name": None})

    def test_empty_name_raises(self):
        with pytest.raises(NormalizationError):
            to_pokemon({**_VALID_RAW, "name": "  "})

    def test_missing_number_raises(self):
        with pytest.raises(NormalizationError):
            to_pokemon({**_VALID_RAW, "national_number": None})

    def test_invalid_number_raises(self):
        with pytest.raises(NormalizationError):
            to_pokemon({**_VALID_RAW, "national_number": "abc"})

    def test_missing_abilities_defaults_to_empty(self):
        raw = {**_VALID_RAW, "abilities": None}
        p = to_pokemon(raw)
        assert p.abilities == []

    def test_ability_without_name_skipped(self):
        raw = {**_VALID_RAW, "abilities": [{"name": "", "is_hidden": False}]}
        p = to_pokemon(raw)
        assert p.abilities == []
