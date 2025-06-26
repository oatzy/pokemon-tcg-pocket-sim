from dataclasses import dataclass, field
from itertools import islice

from pokemon_tcg_simulate.expansion import Rarity


@dataclass
class Collection:
    # rarity of cards in collection
    rarity: Rarity

    # cards that have been collected
    collected: set = field(default_factory=set)

    # cards bought with pack points
    bought: list = field(default_factory=list)

    # how many packs were opened to complete the set
    completed_at: int | None = None

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
    mission: dict[str, int] | None = None

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
