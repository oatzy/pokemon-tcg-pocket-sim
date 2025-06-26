import random
from dataclasses import dataclass
from itertools import accumulate, chain


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
    rare_counts: dict[str, int] | None = None

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
        # TODO: need to change the approach
        # so we can track when a variant is complete
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
