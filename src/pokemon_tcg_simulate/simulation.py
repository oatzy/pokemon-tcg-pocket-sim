import random
from dataclasses import dataclass
from itertools import cycle

from pokemon_tcg_simulate.collection import Collection, MissionCollection


# max pack points that can be held at a time
MAX_PACK_POINTS = 2_500

# % prob of pulling a rare booster pack
RARE_PROBABILITY = 0.050


@dataclass
class SimulationResult:
    collected: dict[str, Collection]
    opened: int = 0
    all_common_at: int | None = None


def rare_booster():
    return 100 * random.random() <= RARE_PROBABILITY


def _pick_from_remaining(collection, key):
    for rarity, collected in sorted(collection.items(), key=key):
        if collected.remaining() > 0:
            return rarity, next(collected.iter_missing())


def pick_most_expensive(collection):
    cost = lambda x: x[1].rarity.cost
    return _pick_from_remaining(collection, cost)


def pick_rarest(collection, variant):
    # the individual card you're least likely to pull
    prob_per_card = lambda x: max(x[1].rarity.offering_rate) / x[1].rarity.count(
        variant
    )
    return _pick_from_remaining(collection, prob_per_card)


def buy_remaining(collection, pack_points, opened):
    for rarity, collected in collection.items():
        for missing in collected.iter_missing():
            if pack_points < collected.rarity.cost:
                # likely a programming error
                raise RuntimeError("Ran out of points")

            collected.buy(missing, opened)
            pack_points -= collected.rarity.cost


def required_pack_points(collection):
    return sum(c.remaining_cost() for c in collection.values())


def completed_all(collection):
    return all(v.completed_at is not None for v in collection.values())


def completed_common(collection):
    return all(
        v.completed_at is not None for v in collection.values() if not v.rarity.rare
    )


def completed_variant(collection, variant):
    # TODO: how?
    return False


# === Simulation ===


def simulate(expansion, initial_state=None, mission=None, stop_at_all_common=False):
    if mission:
        collected = {
            x.name: MissionCollection(x, mission=mission.get(x.name))
            for x in expansion.rarities
            if x.name in mission
        }
    else:
        collected = {x.name: Collection(x) for x in expansion.rarities}

    pack_points = 0

    if initial_state:
        pack_points = initial_state.get("pack_points", 0)
        for rarity, counts in initial_state["collected"].items():
            collected[rarity].load_initial_state(counts)

    opened = 0
    all_common_at = None

    # repeatedly cycle though all variants
    # TODO: stop opening variant when completed
    for variant in cycle(expansion.variants):
        if rare_booster():
            pulled = expansion.open_rare(variant)
        else:
            pulled = expansion.open_regular(variant)

        opened += 1
        pack_points += 5

        for rarity, pull in pulled:
            if rarity in collected:
                collected[rarity].add(pull, opened)

        if required_pack_points(collected) == pack_points:
            buy_remaining(collected, pack_points, opened)

        if pack_points == MAX_PACK_POINTS and not completed_all(collected):
            # rarity, picked = pick_most_expensive(collected)
            rarity, picked = pick_rarest(collected, variant)
            collected[rarity].buy(picked, opened)
            pack_points -= collected[rarity].rarity.cost

        if all_common_at is None and completed_common(collected):
            all_common_at = opened
            if stop_at_all_common:
                break

        if completed_all(collected):
            break

    return SimulationResult(collected, opened, all_common_at)
