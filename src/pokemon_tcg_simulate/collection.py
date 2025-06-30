from dataclasses import dataclass, field

from pokemon_tcg_simulate.expansion import Rarity, ANY


@dataclass
class Variant:
    # how many cards are in the variant
    size: int

    # number of unique cards collected
    unique: int = field(init=False, default=0)

    # total cards collected, including duplicated
    total: int = field(init=False, default=0)

    # number collected of each card in the variant
    collection: list[int] = field(init=False)

    def __post_init__(self):
        self.collection = [0 for _ in range(self.size)]

    @property
    def completed(self):
        return self.size == self.unique

    def __len__(self):
        return self.unique

    def __contains__(self, item):
        return self.collection[item] > 0

    def __getitem__(self, item):
        return self.collection[item]

    def add(self, item, count=1):
        if self.collection[item] == 0:
            self.unique += 1
        self.collection[item] += count
        self.total += 1


@dataclass(kw_only=True)
class Collection:
    # rarity of cards in collection
    rarity: Rarity

    # cards that have been collected
    collected: dict[str, Variant] = field(init=False)

    # cards bought with pack points
    bought: list[tuple[str, int]] = field(init=False, default_factory=list)

    # how many packs were opened to complete the set
    completed_at: int | None = field(init=False, default=None)

    def __post_init__(self):
        counts = self.rarity.counts
        if isinstance(counts, int):
            counts = {ANY: counts}

        self.collected = {v: Variant(c) for v, c in counts.items()}

    def add(self, item, opened):
        variant, card = item

        if variant not in self.collected and list(self.rarity.counts.keys()) == [ANY]:
            # special case: crown cards can appear in any variant for regular boosters
            # but only appear in one variant for rare boosters
            card = list(self.rarity.rare_counts.keys()).index(variant)
            variant = ANY  # TODO: is this sound?

        self.collected[variant].add(card)

        if self.completed_at is None and self.remaining() == 0:
            self.completed_at = opened

    def buy(self, item, opened):
        self.add(item, opened)
        self.bought.append(item)

    def count(self, variant=None):
        any_count = len(self.collected.get(ANY, []))
        if variant == ANY:
            return any_count
        if variant:
            return any_count + len(self.collected.get(variant, []))
        return sum(len(v) for v in self.collected.values())

    def iter_missing(self):
        for variant, count in self.rarity.counts.items():
            yield from (
                (variant, i)
                for i in range(count)
                if i not in self.collected.get(variant, [])
            )

    def remaining(self, variant=None):
        return self.rarity.count(variant) - self.count(variant)

    def remaining_cost(self, variant=None):
        return self.rarity.cost * self.remaining(variant)

    def load_initial_state(self, state):
        if not isinstance(state, dict):
            state = {ANY: state}

        for variant, count in state.items():
            if isinstance(count, int):
                for i in range(count):
                    self.collected[variant].add(i)
            else:
                for i, num in enumerate(count):
                    self.collected[variant].add(i, num)

        if self.remaining() == 0:
            self.completed_at = 0


@dataclass(kw_only=True)
class MissionCollection(Collection):
    mission: dict[str, int]

    def __post_init__(self):
        super().__post_init__()
        for rarity, count in self.mission.items():
            if isinstance(count, int):
                self.mission[rarity] = [1 for _ in range(count)]

    def iter_missing(self, variant=None):
        if variant is not None:
            mission = [(variant, self.mission.get(variant, []))]
            if variant != ANY and ANY in self.mission:
                mission.append((ANY, self.mission[ANY]))
        else:
            mission = self.mission.items()

        for variant, count in mission:
            for inx, need in enumerate(count):
                have = self.collected[variant][inx]
                if need > have:
                    yield from ((variant, inx) for _ in range(need - have))

    def remaining(self, variant=None):
        return sum(1 for _ in self.iter_missing(variant))
