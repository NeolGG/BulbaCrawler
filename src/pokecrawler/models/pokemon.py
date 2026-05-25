from pathlib import Path

from pydantic import BaseModel, Field


class Stats(BaseModel):
    hp: int = Field(ge=0)
    attack: int = Field(ge=0)
    defense: int = Field(ge=0)
    sp_atk: int = Field(ge=0)
    sp_def: int = Field(ge=0)
    speed: int = Field(ge=0)


class Ability(BaseModel):
    name: str
    is_hidden: bool = False


class Evolution(BaseModel):
    predecessors: list[str] = Field(default_factory=list)
    successors: list[str] = Field(default_factory=list)


class Pokemon(BaseModel):
    name: str
    national_number: int = Field(gt=0)
    category: str
    types: list[str] = Field(min_length=1)
    stats: Stats
    abilities: list[Ability] = Field(default_factory=list)
    evolution: Evolution
    image_local: Path | None = None
