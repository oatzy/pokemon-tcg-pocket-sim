import random
from collections import deque

from pokemon_tcg_simulate.collection import Collection
from pokemon_tcg_simulate.expansion import ANY

# max pack points that can be held at a time
MAX_PACK_POINTS = 2_500

# % prob of pulling a rare booster pack
RARE_PROBABILITY = 0.050


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
    for collected in collection.values():
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


class VariantIterator:
    def __init__(self, variants):
        if variants == [ANY]:
            self.variants = deque([ANY])
        else:
            self.variants = deque(v for v in variants if v != ANY)

    def __iter__(self):
        return self

    def __next__(self):
        self.variants.rotate(-1)
        return self.variants[-1]

    def remove(self, variant):
        if variant in self.variants:
            self.variants.remove(variant)


def simulate(expansion, collection: Collection, *, buy_cards=True, max_opened=None):
    # NOTE: mutates the collection object
    collected = collection.collected

    # TODO: configurable variant generator (cf simulate_mission)
    variants = VariantIterator(expansion.variants)
    for variant in variants:
        if rare_booster():
            pulled = expansion.open_rare(variant)
        else:
            pulled = expansion.open_regular(variant)

        collection.opened += 1
        collection.pack_points += 5

        collection.add(pulled)

        if buy_cards:
            if required_pack_points(collected) <= collection.pack_points:
                collection.pack_points = buy_remaining(
                    collected, collection.pack_points, collection.opened
                )

            if collection.pack_points == MAX_PACK_POINTS and not completed_all(
                collected
            ):
                picked = pick_from_remaining(collected, rarest(variant))
                collection.buy(picked)

        if collection.all_common_at is None and completed_common(collected):
            collection.all_common_at = collection.opened

        if completed_all(collected):
            break

        if completed_variant(collected, variant):
            variants.remove(variant)

        if max_opened is not None and collection.opened >= max_opened:
            break

    return collection
