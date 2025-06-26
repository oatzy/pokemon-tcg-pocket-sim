import random
from dataclasses import dataclass, field
from itertools import accumulate, chain, islice
from typing import Optional


ANY = "_any_"


@dataclass
class Rarity:
    # name of rarity type
    name: str

    # cost to buy in pack points
    cost: int

    # % rate for each of the 5 slots
    offering_rate: tuple[int]

    # counts[ANY] = cards appearing in all variants
    # counts[x] = variant exclusive cards
    counts: dict[str, int]

    # whether it appears in rare boosters
    rare: bool = False

    # counts of cards in rare boosters
    rare_counts: Optional[dict[str, int]] = None

    def __post_init__(self):
        self._any_count = self.counts.get(ANY, 0)

        self._offsets = _offsets(self.counts)

        if self.rare:
            if self.rare_counts is None:
                self.rare_counts = self.counts
            self._rare_offsets = _offsets(self.rare_counts)

    def iter_rare_cards(self, variant):
        if not self.rare:
            return

        any_count = self.rare_counts.get(ANY, 0)
        yield from range(any_count)

        offset = any_count + self._rare_offsets[variant]
        yield from (i + offset for i in range(self.rare_counts.get(variant, 0)))

    def iter_variant_cards(self, variant):
        if variant == ANY:
            return range(self._any_count)

        offset = self._any_count + self._offsets[variant]
        yield from (i + offset for i in range(self.counts.get(variant, 0)))

    def count(self, variant=None):
        if variant is not None:
            return self._any_count + self.counts.get(variant, 0)
        return sum(self.counts.values())

    def pick(self, variant):
        p = random.randint(0, self.count(variant) - 1)
        if p >= self._any_count:
            p += self._offsets[variant]
        return p


def _offsets(counts):
    offsets = {}

    offset = 0
    for k, v in counts.items():
        if k == ANY:
            continue
        offsets[k] = offset
        offset += v

    return offsets


@dataclass
class Expansion:
    name: str
    variants: list[str]
    rarities: tuple[Rarity]

    def __post_init__(self):
        # pre-calculate cumulative probability by position
        self._cum_prob = [
            list(accumulate(x.offering_rate[p] for x in self.rarities))
            for p in range(5)
        ]

        # pre-generate a list of all rare cards for rare booster picks
        self._rare_cards = {
            v: tuple(
                chain.from_iterable(
                    ((x.name, i) for i in x.iter_rare_cards(v))
                    for x in self.rarities
                    if x.rare
                )
            )
            for v in self.variants
        }

    @classmethod
    def from_json(cls, data):
        return Expansion(
            name=data["name"],
            variants=data["variants"],
            rarities=tuple(
                Rarity(**i) for i in sorted(data["rarities"], key=lambda x: -x["cost"])
            ),
        )

    def open_rare(self, variant):
        return random.choices(self._rare_cards[variant], k=5)

    def _pick(self, pos, variant):
        r = 100 * random.random()

        for i, p in enumerate(self._cum_prob[pos]):
            if r <= p:
                rarity = self.rarities[i]
                break
        else:
            # due to rounding, sometimes probabilities don't add to 100
            # if we fail to pick, retry
            return self._pick(pos, variant)

        return rarity.name, rarity.pick(variant)

    def open_regular(self, variant):
        return [self._pick(i, variant) for i in range(5)]


@dataclass
class Collection:
    # rarity of cards in collection
    rarity: Rarity

    # cards that have been collected
    collected: set = field(default_factory=set)

    # cards bought with pack points
    bought: list = field(default_factory=list)

    # how many packs were opened to complete the set
    completed_at: Optional[int] = None

    def add(self, item, opened):
        self.collected.add(item)

        if self.completed_at is None and self.remaining() == 0:
            self.completed_at = opened

    def buy(self, item, opened):
        self.add(item, opened)
        self.bought.append(item)

    def iter_missing(self):
        return (i for i in range(self.rarity.count()) if i not in self.collected)

    def remaining(self):
        return self.rarity.count() - len(self.collected)

    def remaining_cost(self):
        return self.rarity.cost * self.remaining()

    def load_initial_state(self, state):
        for variant, count in state.items():
            self.collected.update(
                islice(self.rarity.iter_variant_cards(variant), count)
            )

        if self.remaining() == 0:
            self.completed_at = 0


@dataclass
class MissionCollection(Collection):
    mission: Optional[dict] = None

    def __post_init__(self):
        self.goal = set()
        if not self.mission:
            return

        for variant, count in self.mission.items():
            self.goal.update(islice(self.rarity.iter_variant_cards(variant), count))

    def iter_missing(self):
        return (i for i in self.goal if i not in self.collected)

    def remaining(self):
        return len(list(self.iter_missing()))
