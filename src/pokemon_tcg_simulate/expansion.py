import random
from dataclasses import dataclass, field
from itertools import accumulate, chain

ANY = "_any_"

# max number of cards that can appear in a pack
# currently 6 for "regular + one card"
MAX_CARDS_PER_PACK = 6

# % prob of pulling a rare booster pack
RARE_PROBABILITY = 0.050

# default rate for pulling different booster types
DEFAULT_BOOSTER_RATE = {
    "regular": 100 - RARE_PROBABILITY,
    "rare": RARE_PROBABILITY,
}


@dataclass
class Rarity:
    # name of rarity type
    name: str

    # cost to buy in pack points
    cost: int

    # % rate for each of the 5 slots
    offering_rate: tuple[float]

    # counts[ANY] = cards appearing in all variants
    # counts[x] = variant exclusive cards
    counts: dict[str, int]

    # whether this is a 'common' 1-4 diamond card
    common: bool | None = None

    # whether it appears in rare boosters
    rare: bool = False

    # counts of cards in rare boosters
    rare_counts: dict[str, int] | None = None

    # whether it appears as the 6th in a plus one booster
    plus_one: bool = False

    def __post_init__(self):
        # backwards compatibility
        # any card which doesn't appear in rare boosters
        # is assumed to be common
        if self.common is None:
            self.common = not self.rare

        if isinstance(self.counts, int):
            self.counts = {ANY: self.counts}

        self._any_count = self.counts.get(ANY, 0)

        # this logic is for crown cards
        # for normal boosters all crown cards appear in any variant
        # but for rare boosters, each crown card is variant locked
        if self.rare and self.rare_counts is None:
            self.rare_counts = self.counts

        if self.plus_one:
            if isinstance(self.offering_rate, float):
                self.offering_rate = (0,) * 5 + (self.offering_rate,)
        elif len(self.offering_rate) < MAX_CARDS_PER_PACK:
            self.offering_rate += (0,) * (MAX_CARDS_PER_PACK - len(self.offering_rate))

    def iter_rare_cards(self, variant):
        if not self.rare:
            return

        any_count = self.rare_counts.get(ANY, 0)
        yield from ((ANY, i) for i in range(any_count))

        if variant != ANY:
            yield from ((variant, i) for i in range(self.rare_counts.get(variant, 0)))

    def count(self, variant=None):
        if variant == ANY:
            return self._any_count

        if variant is not None:
            return self._any_count + self.counts.get(variant, 0)

        return sum(self.counts.values())

    def pick(self, variant):
        p = random.randint(0, self.count(variant) - 1)
        if p >= self._any_count:
            return (variant, p - self._any_count)
        return (ANY, p)


@dataclass
class Expansion:
    name: str
    variants: list[str]
    rarities: tuple[Rarity]
    booster_rates: dict[str, float] = field(default_factory=DEFAULT_BOOSTER_RATE.copy)
    cards_per_pack: int = 5

    def __post_init__(self):
        # pre-calculate cumulative probability by position
        self._cum_prob = [
            list(accumulate(x.offering_rate[p] for x in self.rarities))
            for p in range(MAX_CARDS_PER_PACK)
        ]

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
        # TODO: validation
        kwargs = {
            **data,
            "variants": data.get("variants", [ANY]),
            "rarities": tuple(
                Rarity(**r) for r in sorted(data["rarities"], key=lambda x: -x["cost"])
            ),
        }
        return Expansion(**kwargs)

    def pick_booster(self):
        r = 100 * random.random()

        p = 0
        for booster, prob in self.booster_rates.items():
            p += prob
            if r <= p:
                return booster

        if p == 0:
            raise Exception("Infinite loop! Check your booster probabilities")

        # shouldn't happen (rounding error?)
        return self.pick_booster()

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
        return [self._pick(i, variant) for i in range(self.cards_per_pack)]

    def open_regular_plus_one(self, variant):
        return [self._pick(i, variant) for i in range(self.cards_per_pack + 1)]

    def open(self, variant):
        booster = self.pick_booster()
        return {
            "regular": self.open_regular,
            "rare": self.open_rare,
            "plus_one": self.open_regular_plus_one,
        }[booster](variant)


def create_common_mission(expansion: Expansion):
    """
    Create a mission that only requires collecting all common cards.
    """
    return {
        "expansion": expansion.name,
        "mission": "Collect all common cards",
        "cards": {r.name: r.counts.copy() for r in expansion.rarities if not r.rare},
    }
