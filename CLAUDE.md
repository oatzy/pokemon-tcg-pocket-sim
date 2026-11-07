# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Monte Carlo simulator estimating how many Pokemon TCG Pocket booster packs it takes to complete an expansion (or a "mission" subset of it). Pure Python 3.11+, no runtime dependencies, managed with `uv`.

## Commands

```bash
uv run pytest                                   # all tests (fast, <1s)
uv run pytest tests/unit/test_expansion.py::TestName::test_name   # single test
uv run pokemon-tcg-simulate data/expansions/genetic_apex.json -r 1000        # full set
uv run pokemon-tcg-simulate data/expansions/genetic_apex.json -c             # stop when all common (1-4 diamond) collected
uv run pokemon-tcg-simulate <expansion.json> -m data/missions/<m>.json -i data/collected/<c>.json
```

Other CLI flags: `--no-buy` (never spend pack points), `--max-opened N` (open N packs and report card stats instead of packs-opened), `--json`, `-o FILE` (dump histograms).

No lint config in the repo; code is formatted with `black` and `ruff` (run manually).

## Architecture

Code is in `src/pokemon_tcg_simulate/`. One run = build a fresh `Collection`, call `simulate()`, feed the result to statistics objects; `main.py` repeats this `--runs` times.

- **`expansion.py`** — `Rarity` and `Expansion` dataclasses loaded from `data/expansions/*.json`. Handles pack opening: picks a booster type from `booster_rates` (`regular`, `rare`, `plus_one`, `themed_rare`, plus `guaranteed_four_diamond` substituted for `regular` once `guarantee_counter` reaches `guaranteed_after`), then picks a rarity per slot using precomputed cumulative `offering_rate`s. `Rarity.__post_init__` normalises a lot of shorthand (int `counts`, scalar `offering_rate` for plus-one, scalar `guaranteed_rate`, inferred `common`/`guaranteed`), so read it before changing the JSON format. Rarities are sorted by descending cost on load.
- **Card identity** is `(rarity_name, (variant, index))`. `ANY = "_any_"` means a card that appears in every variant; `counts` maps variant → number of variant-exclusive cards. Rarity names are arbitrary strings but must match across expansion, mission and collection files.
- **`collection.py`** — tracks what's been pulled/bought per rarity and variant. `MissionRarityCollection` restricts the target to a mission's cards (counts can be lists to require multiple copies of a card). `Collection.load_initial_state` applies a `data/collected/*.json` file.
- **`simulation.py`** — the main loop. Cycles through variants round-robin (`VariantIterator`), dropping completed ones. Each pack gives 5 pack points; buys all remaining cards as soon as points cover them; at the 2,500 point cap buys the rarest remaining card. Note `simulate()` mutates the `Expansion` too (`guarantee_counter`).
- **`output.py`** — `OpenedStatistics` / `CardStatistics` / `BoughtStatistics` aggregate per-run results; `format_markdown` prints them.

`scripts/simulate_mission.py` is a standalone, older, hardcoded simulation (Space-Time Smackdown Sinnoh mission); it doesn't use the package.

## Data files

Formats are documented in `data/expansions/format.md`, `data/missions/format.md`, `data/collected/format.md`, including how special booster types (plus-one, themed rare, guaranteed 4-diamond) are modelled. Read the relevant one before editing data or the loaders.

Adding a new expansion is the most common change: add `data/expansions/<name>.json` (offering rates and counts come from the game) and add a row to the Series results table in `README.md` with the simulated Common (`-c`) and Complete averages. Only touch code if the expansion introduces a new booster mechanic.
