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
        if isinstance(self.counts, int):
            self.counts = {ANY: self.counts}

        self._any_count = self.counts.get(ANY, 0)

        # this logic is for crown cards
        # for normal boosters all crown cards appear in any variant
        # but for rare boosters, each crown card is variant locked
        if self.rare and self.rare_counts is None:
            self.rare_counts = self.counts

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

    def __post_init__(self):
        # pre-calculate cumulative probability by position
        self._cum_prob = [
            list(accumulate(x.offering_rate[p] for x in self.rarities))
            for p in range(5)
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
        return Expansion(
            name=data["name"],
            variants=data.get("variants", [ANY]),
            rarities=tuple(
                Rarity(**r) for r in sorted(data["rarities"], key=lambda x: -x["cost"])
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


def create_common_mission(expansion: Expansion):
    """
    Create a mission that only requires collecting all common cards.
    """
    return {r.name: r.counts for r in expansion.rarities if not r.rare}
