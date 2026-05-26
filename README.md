# pokecrawler

Crawls Pokémon data from [Bulbapedia](https://bulbapedia.bulbagarden.net) and stores it locally as JSON, SQLite and images.

## Requirements

- Python 3.12+
- Docker (optional)

## Running locally

Install the package:

```bash
pip install -e .
```

Run the crawler:

```bash
python -m pokecrawler
```

### CLI options

| Option | Default | Description |
|---|---|---|
| `--pokemon NAME [NAME ...]` | — | Crawl specific Pokémon by name (skips pagination). When provided, `--start-url` and `--limit` are ignored. |
| `--start-url URL` | Bulbasaur | Starting Pokémon page (used in pagination mode) |
| `--limit N` | no limit | Maximum number of Pokémon to crawl (used in pagination mode) |
| `--output DIR` | `output/` | Directory for all output files |
| `--concurrency N` | `5` | Parallel workers |
| `--no-images` | — | Skip image downloads |

Examples:

```bash
# crawl the first 10 Pokémon (pagination mode)
python -m pokecrawler --limit 10

# crawl specific Pokémon by name
python -m pokecrawler --pokemon Bulbasaur Eevee Gyarados

# crawl without downloading images, output to a custom directory
python -m pokecrawler --no-images --output data/
```

## Running with Docker

```bash
docker compose run pokecrawler
```

Output files are written to `./output/` on the host via volume mount.

Pass CLI options after the service name:

```bash
docker compose run pokecrawler --limit 10 --no-images
```

## Output

All files are written to the output directory (`output/` by default):

| File | Description |
|---|---|
| `pokemons.json` | All crawled Pokémon as a JSON array, sorted by national number |
| `pokedex.db` | SQLite database with the same data |
| `images/` | Pokémon images named `{number}_{name}.png` |

### JSON structure

```json
{
  "name": "Bulbasaur",
  "national_number": 1,
  "category": "Seed Pokémon",
  "types": ["Grass", "Poison"],
  "stats": {
    "hp": 45,
    "attack": 49,
    "defense": 49,
    "sp_atk": 65,
    "sp_def": 65,
    "speed": 45
  },
  "abilities": [
    {"name": "Overgrow", "is_hidden": false},
    {"name": "Chlorophyll", "is_hidden": true}
  ],
  "evolution": {
    "predecessors": [],
    "successors": ["Ivysaur", "Venusaur"]
  },
  "image_local": "output/images/0001_bulbasaur.png"
}
```

## Development

Install with dev dependencies:

```bash
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

Lint and format:

```bash
ruff check --fix .
ruff format .
```

## Architecture

### Two-phase crawl

The crawler runs in two phases:

1. **Phase 1 — page collection**: fetches the HTML for each Pokémon and buffers it in memory. Two strategies:
    - **Pagination mode** (default): sequentially follows `Next` links from a starting page.
    - **By-name mode** (`--pokemon`): fetches the requested pages concurrently, no pagination needed.
2. **Phase 2 — processing**: processes all buffered pages in parallel (controlled by `--concurrency`), parsing, normalizing, downloading images and upserting to the database.

This separation keeps URL discovery deterministic in pagination mode while parallelising the heavier work (image downloads, parsing) in both modes.

### Module overview

| Module | Responsibility |
|---|---|
| `http_client` | Shared `httpx.AsyncClient` with retry logic |
| `crawler` | Orchestrates the two-phase crawl |
| `parser` | Extracts raw data from BeautifulSoup trees |
| `normalizer` | Validates and converts raw data into Pydantic models |
| `sanitizer` | Removes hidden elements from HTML before parsing |
| `pagination` | Finds the next Pokémon URL from a page (pagination mode) |
| `urls` | Builds Pokémon page URLs from names (by-name mode) |
| `image_store` | Downloads and saves Pokémon images |
| `database` | SQLite upsert logic |
| `exporter` | Writes the final JSON file |
| `models` | Pydantic models (`Pokemon`, `Stats`, `Ability`, `Evolution`) |

### Tools

**httpx**: async-native HTTP client with built-in connection pooling, a clean `AsyncClient` lifecycle, and native support for `asyncio`.

**BeautifulSoup4**: HTML parser tolerant of malformed markup, common in real-world pages. Offers a simple and readable traversal API.

**Pydantic v2**: data validation, normalisation and JSON serialisation in a single layer. The models double as serialisers via `model_dump()`, and v2 is rewritten in Rust for high performance.

**SQLite (stdlib)**: embedded database, zero configuration, no service to run. The output is a single portable `.db` file inspectable with any SQLite viewer.

**pytest**: testing framework with powerful fixtures via `conftest.py`, plain function-based tests and a rich plugin ecosystem.

**ruff**: linter and formatter in a single Rust-based tool. Extremely fast and configured entirely in `pyproject.toml`, with no extra config files.

**Docker**: guarantees the project runs identically across environments.
