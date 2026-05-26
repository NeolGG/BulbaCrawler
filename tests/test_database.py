from pathlib import Path

from pokecrawler.database import init_db, upsert_pokemon
from pokecrawler.models.pokemon import Ability, Evolution, Pokemon, Stats


def _make_pokemon(number: int = 1, name: str = "Bulbasaur") -> Pokemon:
    return Pokemon(
        name=name,
        national_number=number,
        category="Seed Pokémon",
        types=["Grass", "Poison"],
        stats=Stats(hp=45, attack=49, defense=49, sp_atk=65, sp_def=65, speed=45),
        abilities=[
            Ability(name="Overgrow"),
            Ability(name="Chlorophyll", is_hidden=True),
        ],
        evolution=Evolution(successors=["Ivysaur", "Venusaur"]),
    )


class TestInitDb:
    def test_creates_pokemon_table(self, tmp_path: Path):
        conn = init_db(tmp_path / "test.db")
        tables = {
            r[0]
            for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
        assert "pokemon" in tables
        conn.close()

    def test_creates_parent_directories(self, tmp_path: Path):
        db_path = tmp_path / "nested" / "test.db"
        conn = init_db(db_path)
        assert db_path.exists()
        conn.close()

    def test_idempotent(self, tmp_path: Path):
        path = tmp_path / "test.db"
        conn = init_db(path)
        conn.close()
        conn = init_db(path)  # should not raise
        conn.close()


class TestUpsertPokemon:
    def test_inserts_row(self, tmp_path: Path):
        conn = init_db(tmp_path / "test.db")
        upsert_pokemon(conn, _make_pokemon())
        row = conn.execute("SELECT name, national_number FROM pokemon").fetchone()
        assert row[0] == "Bulbasaur"
        assert row[1] == 1
        conn.close()

    def test_update_does_not_duplicate(self, tmp_path: Path):
        conn = init_db(tmp_path / "test.db")
        upsert_pokemon(conn, _make_pokemon(1, "Bulbasaur"))
        upsert_pokemon(conn, _make_pokemon(1, "BulbasaurV2"))
        count = conn.execute(
            "SELECT COUNT(*) FROM pokemon WHERE national_number = 1"
        ).fetchone()[0]
        assert count == 1
        conn.close()

    def test_update_changes_name(self, tmp_path: Path):
        conn = init_db(tmp_path / "test.db")
        upsert_pokemon(conn, _make_pokemon(1, "Bulbasaur"))
        upsert_pokemon(conn, _make_pokemon(1, "BulbasaurV2"))
        name = conn.execute(
            "SELECT name FROM pokemon WHERE national_number = 1"
        ).fetchone()[0]
        assert name == "BulbasaurV2"
        conn.close()

    def test_preserves_id_on_update(self, tmp_path: Path):
        conn = init_db(tmp_path / "test.db")
        upsert_pokemon(conn, _make_pokemon())
        id_before = conn.execute("SELECT id FROM pokemon").fetchone()[0]
        upsert_pokemon(conn, _make_pokemon(1, "Updated"))
        id_after = conn.execute("SELECT id FROM pokemon").fetchone()[0]
        assert id_before == id_after
        conn.close()

    def test_preserves_created_at_on_update(self, tmp_path: Path):
        conn = init_db(tmp_path / "test.db")
        upsert_pokemon(conn, _make_pokemon())
        created_before = conn.execute("SELECT created_at FROM pokemon").fetchone()[0]
        upsert_pokemon(conn, _make_pokemon(1, "Updated"))
        created_after = conn.execute("SELECT created_at FROM pokemon").fetchone()[0]
        assert created_before == created_after
        conn.close()

    def test_multiple_pokemon(self, tmp_path: Path):
        conn = init_db(tmp_path / "test.db")
        upsert_pokemon(conn, _make_pokemon(1, "Bulbasaur"))
        upsert_pokemon(conn, _make_pokemon(2, "Ivysaur"))
        count = conn.execute("SELECT COUNT(*) FROM pokemon").fetchone()[0]
        assert count == 2
        conn.close()
