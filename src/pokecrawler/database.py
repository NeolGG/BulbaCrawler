import json
import sqlite3
from pathlib import Path

from pokecrawler.models.pokemon import Pokemon

_OUTPUT_DB = Path("output/pokedex.db")

_DDL = """
CREATE TABLE IF NOT EXISTS pokemon (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    national_number INTEGER NOT NULL UNIQUE,
    name            TEXT    NOT NULL,
    category        TEXT    NOT NULL,
    image_local     TEXT,
    hp              INTEGER NOT NULL,
    attack          INTEGER NOT NULL,
    defense         INTEGER NOT NULL,
    sp_atk          INTEGER NOT NULL,
    sp_def          INTEGER NOT NULL,
    speed           INTEGER NOT NULL,
    types           TEXT    NOT NULL,
    abilities       TEXT    NOT NULL,
    evolution       TEXT    NOT NULL,
    created_at      TEXT    NOT NULL DEFAULT (CURRENT_TIMESTAMP),
    updated_at      TEXT    NOT NULL DEFAULT (CURRENT_TIMESTAMP)
);
"""


def init_db(path: Path = _OUTPUT_DB) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.executescript(_DDL)
    conn.commit()
    return conn


def upsert_pokemon(conn: sqlite3.Connection, pokemon: Pokemon) -> None:
    conn.execute(
        """
        INSERT INTO pokemon
            (national_number, name, category, image_local,
             hp, attack, defense, sp_atk, sp_def, speed,
             types, abilities, evolution)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(national_number) DO UPDATE SET
            name        = excluded.name,
            category    = excluded.category,
            image_local = excluded.image_local,
            hp          = excluded.hp,
            attack      = excluded.attack,
            defense     = excluded.defense,
            sp_atk      = excluded.sp_atk,
            sp_def      = excluded.sp_def,
            speed       = excluded.speed,
            types       = excluded.types,
            abilities   = excluded.abilities,
            evolution   = excluded.evolution,
            updated_at  = CURRENT_TIMESTAMP
        """,
        (
            pokemon.national_number,
            pokemon.name,
            pokemon.category,
            str(pokemon.image_local) if pokemon.image_local else None,
            pokemon.stats.hp,
            pokemon.stats.attack,
            pokemon.stats.defense,
            pokemon.stats.sp_atk,
            pokemon.stats.sp_def,
            pokemon.stats.speed,
            json.dumps(pokemon.types, ensure_ascii=False),
            json.dumps([a.model_dump() for a in pokemon.abilities], ensure_ascii=False),
            json.dumps(pokemon.evolution.model_dump(), ensure_ascii=False),
        ),
    )
    conn.commit()
