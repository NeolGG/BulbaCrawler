from bs4 import BeautifulSoup

from pokecrawler.normalizer.pokemon import to_pokemon
from pokecrawler.parser.engine import parse_page
from pokecrawler.sanitizer.html_cleaner import clean


def _pipeline(html: str):
    soup = BeautifulSoup(html, "html.parser")
    clean(soup)
    raw = parse_page(soup)
    return to_pokemon(raw)


# --- Bulbasaur ---


def test_bulbasaur_name_and_number(bulbasaur_html):
    p = _pipeline(bulbasaur_html)
    assert p.name == "Bulbasaur"
    assert p.national_number == 1


def test_bulbasaur_types(bulbasaur_html):
    p = _pipeline(bulbasaur_html)
    assert p.types == ["Grass", "Poison"]


def test_bulbasaur_stats(bulbasaur_html):
    p = _pipeline(bulbasaur_html)
    assert p.stats.hp == 45
    assert p.stats.attack == 49
    assert p.stats.defense == 49
    assert p.stats.sp_atk == 65
    assert p.stats.sp_def == 65
    assert p.stats.speed == 45


def test_bulbasaur_abilities(bulbasaur_html):
    p = _pipeline(bulbasaur_html)
    names = [a.name for a in p.abilities]
    assert "Overgrow" in names
    assert "Chlorophyll" in names


def test_bulbasaur_hidden_ability(bulbasaur_html):
    p = _pipeline(bulbasaur_html)
    hidden = [a for a in p.abilities if a.is_hidden]
    assert len(hidden) == 1
    assert hidden[0].name == "Chlorophyll"


def test_bulbasaur_evolution(bulbasaur_html):
    p = _pipeline(bulbasaur_html)
    assert p.evolution.predecessors == []
    assert "Ivysaur" in p.evolution.successors


# --- Eevee ---


def test_eevee_name_and_number(eevee_html):
    p = _pipeline(eevee_html)
    assert p.name == "Eevee"
    assert p.national_number == 133


def test_eevee_abilities(eevee_html):
    p = _pipeline(eevee_html)
    names = [a.name for a in p.abilities]
    assert "Run Away" in names
    assert "Adaptability" in names
    assert "Anticipation" in names


def test_eevee_hidden_ability(eevee_html):
    p = _pipeline(eevee_html)
    hidden = [a for a in p.abilities if a.is_hidden]
    assert len(hidden) == 1
    assert hidden[0].name == "Anticipation"


def test_eevee_many_successors(eevee_html):
    p = _pipeline(eevee_html)
    assert len(p.evolution.successors) >= 8


# --- Gyarados ---


def test_gyarados_name_and_number(gyarados_html):
    p = _pipeline(gyarados_html)
    assert p.name == "Gyarados"
    assert p.national_number == 130


def test_gyarados_types(gyarados_html):
    p = _pipeline(gyarados_html)
    assert "Water" in p.types
    assert "Flying" in p.types


def test_gyarados_stats(gyarados_html):
    p = _pipeline(gyarados_html)
    assert p.stats.hp == 95
    assert p.stats.attack == 125
    assert p.stats.speed == 81


def test_gyarados_hidden_ability(gyarados_html):
    p = _pipeline(gyarados_html)
    hidden = [a for a in p.abilities if a.is_hidden]
    assert len(hidden) == 1
    assert hidden[0].name == "Moxie"


def test_gyarados_evolves_from_magikarp(gyarados_html):
    p = _pipeline(gyarados_html)
    assert "Magikarp" in p.evolution.predecessors
