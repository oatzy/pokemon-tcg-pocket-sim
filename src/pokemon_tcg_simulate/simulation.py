import random
from collections import deque
from dataclasses import dataclass

from pokemon_tcg_simulate.collection import Collection, MissionCollection
from pokemon_tcg_simulate.expansion import ANY

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


def pick_from_remaining(collection, key):
    for rarity, collected in sorted(collection.items(), key=key):
        if collected.remaining() > 0:
            return rarity, next(collected.iter_missing())


def most_expensive(collection_item):
    return -collection_item[1].rarity.cost


def rarest(variant):
    # the individual card you're least likely to pull
    def inner(collection_item):
        return max(collection_item[1].rarity.offering_rate) / collection_item[
            1
        ].rarity.count(variant)

    return inner


def buy_remaining(collection, pack_points, opened):
    for rarity, collected in collection.items():
        for missing in collected.iter_missing():
            if pack_points < collected.rarity.cost:
                # likely a programming error
                raise RuntimeError("Ran out of points")

            collected.buy(missing, opened)
            pack_points -= collected.rarity.cost
    return pack_points


def required_pack_points(collection):
    return sum(c.remaining_cost() for c in collection.values())


def completed_all(collection):
    return all(v.completed_at is not None for v in collection.values())


def completed_common(collection):
    return all(
        v.completed_at is not None for v in collection.values() if not v.rarity.rare
    )


def completed_variant(collection, variant):
    return not any(v.remaining(variant) for v in collection.values())


def simulate(expansion, initial_state=None, mission=None, stop_at_all_common=False):
    if mission:
        collected = {
            r.name: MissionCollection(rarity=r, mission=mission.get(r.name))
            for r in expansion.rarities
            if r.name in mission
        }
    else:
        collected = {r.name: Collection(rarity=r) for r in expansion.rarities}

    pack_points = 0

    if initial_state:
        pack_points = initial_state.get("pack_points", 0)
        for rarity, counts in initial_state["collected"].items():
            collected[rarity].load_initial_state(counts)

    opened = 0
    all_common_at = None

    # TODO: configurable variant generator (cf simulate_mission)
    if expansion.variants != [ANY]:
        variants = deque(v for v in expansion.variants if v != ANY)
    else:
        variants = deque([ANY])

    while True:
        variant = variants[0]
        variants.rotate(-1)

        if rare_booster():
            pulled = expansion.open_rare(variant)
        else:
            pulled = expansion.open_regular(variant)

        opened += 1
        pack_points += 5

        for rarity, pull in pulled:
            if rarity in collected:
                collected[rarity].add(pull, opened)

        if required_pack_points(collected) <= pack_points:
            pack_points = buy_remaining(collected, pack_points, opened)

        if pack_points == MAX_PACK_POINTS and not completed_all(collected):
            rarity, picked = pick_from_remaining(collected, rarest(variant))
            collected[rarity].buy(picked, opened)
            pack_points -= collected[rarity].rarity.cost

        if all_common_at is None and completed_common(collected):
            all_common_at = opened
            if stop_at_all_common:
                break

        if completed_all(collected):
            break

        if completed_variant(collected, variant):
            variants.remove(variant)

    return SimulationResult(collected, opened, all_common_at)
