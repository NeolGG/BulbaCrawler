from pathlib import Path

import pytest

_FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def bulbasaur_html():
    return (_FIXTURES / "bulbasaur.html").read_text(encoding="utf-8")


@pytest.fixture
def eevee_html():
    return (_FIXTURES / "eevee.html").read_text(encoding="utf-8")


@pytest.fixture
def gyarados_html():
    return (_FIXTURES / "gyarados.html").read_text(encoding="utf-8")
