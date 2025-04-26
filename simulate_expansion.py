import json
import random
from argparse import ArgumentParser
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from itertools import accumulate, chain, cycle
from typing import Optional


# max pack points that can be held at a time
MAX_PACK_POINTS = 2_500

# % prob of pulling a rare booster pack
RARE_PROBABILITY = 0.050


@dataclass
class Card:
    # cost to buy in pack points
    cost: int
    
    # % rate for each of the 5 slots
    offering_rate: tuple[int]
    
    # counts[0] appear in all variants
    # counts[i>0] are variant exclusive
    counts: tuple[int]
    
    # whether it appears in rare boosters
    rare: bool

    def __post_init__(self):
        self._offsets = [0, 0] + list(accumulate(self.counts[1:]))

    def count(self, variant=None):
        if variant is not None:
            return self.counts[0] + self.counts[variant]
        return sum(self.counts)

    def pick(self, variant):
        p = random.randint(0, self.count(variant) - 1)
        if p >= self.counts[0]:
            p += self._offsets[variant]
        return p


@dataclass
class Expansion:
    cards: dict[str, Card]

    def __post_init__(self):
        self.variants = len(list(self.cards.values())[0].counts) - 1

        # pre-calculate cumulative probability by position
        self._cum_prob = [
            list(accumulate(c.offering_rate[p] for c in self.cards.values()))
            for p in range(5)
        ]
        self._pop = list(self.cards)
        
        # pre-generate a list of all rare cards for rare booster picks
        # crown cards are variant exclusive, unlike for regular boosters
        self._rare_cards = tuple(
            tuple(chain.from_iterable(
                ((rarity, i) for i in range(1 if rarity == "CROWN" else c.count(v))) 
                for rarity, c in self.cards.items() if c.rare
            ))
            for v in range(1, self.variants + 1)
        )

    @classmethod
    def from_json(cls, data):
        return Expansion(
            cards={k: Card(**v) for k, v in sorted(data.items(), key=lambda x: -x[1]["cost"])}
        )
        
    def open_rare(self, variant=1):
        return random.choices(self._rare_cards[variant - 1], k=5)

    def _pick(self, x, variant=1):
        #rarity = random.choices(_POP, cum_weights=self._cum_prob[x])[0]
        r = 100 * random.random()
        for i, p in enumerate(self._cum_prob[x]):
            if r <= p:
                rarity = self._pop[i]
                break
        return rarity, self.cards[rarity].pick(variant)
    
    def open_regular(self, variant=1):
        return [self._pick(i, variant) for i in range(5)]


@dataclass
class Collection:
    card: Card
    collected: set = field(default_factory=set)
    bought: list = field(default_factory=list)
    completed_at: Optional[int] = None

    def add(self, item, opened):
        self.collected.add(item)
        
        if self.completed_at is None and self.remaining() == 0:
            self.completed_at = opened

    def buy(self, item, opened):
        self.add(item, opened)
        self.bought.append(item)
    
    def iter_missing(self):
        return (i for i in range(self.card.count()) if i not in self.collected)
    
    def remaining(self):
        return self.card.count() - len(self.collected)
    
    def remaining_cost(self):
        return self.card.cost * self.remaining()


def rare_booster():
    return 100 * random.random() <= RARE_PROBABILITY


def pick_most_expensive(collected):
    # assumes 'collected' is sorted rarest first
    for rarity, collection in collected.items():
        if collection.remaining() > 0:
            return rarity, next(collection.iter_missing())


def buy_remaining(collection, pack_points, opened):
    for rarity, collected in collection.items():
        for missing in collected.iter_missing():
            
            if pack_points < collected.card.cost:
                raise RuntimeError("ran out of points")
                
            collected.buy(missing, opened)
            pack_points -= collected.card.cost


def required_pack_points(collected):
    return sum(c.remaining_cost() for c in collected.values())


def completed_all(collected):
    return all(v.completed_at is not None for v in collected.values())


def completed_common(collected):
    return all(v.completed_at is not None for v in collected.values() if not v.card.rare)


def simulate(expansion, stop_at_all_common=False):
    collected = {k: Collection(v) for k, v in expansion.cards.items()}

    all_common_at = None
    
    opened = 0
    pack_points = 0

    # repeatedly cycle though all variants
    for variant in cycle(range(1, expansion.variants + 1)):
        
        if rare_booster():
            pulled = expansion.open_rare(variant)
        else:
            pulled = expansion.open_regular(variant)

        opened += 1
        pack_points += 5

        for rarity, pull in pulled:
            collected[rarity].add(pull, opened)

        if required_pack_points(collected) == pack_points:
            buy_remaining(collected, pack_points, opened)
            break
        
        if pack_points == MAX_PACK_POINTS and not completed_all(collected):
            rarity, picked = pick_most_expensive(collected)
            collected[rarity].buy(picked, opened)
            pack_points -= expansion.cards[rarity].cost

        if all_common_at is None and completed_common(collected):
            all_common_at = opened
            if stop_at_all_common:
                break
        
        if completed_all(collected):
            break

    return opened, all_common_at, collected
        

def _avg(counter):
    if el := list(counter.elements()):
        return sum(el) / len(el)
    return None


def main():
    parser = ArgumentParser()
    parser.add_argument("expansion_json", help="path to an expansion data json")
    parser.add_argument("-r", "--runs", default=100, type=int, help="number of simulations to run")
    parser.add_argument("-c", "--stop-at-common", action="store_true", help="stop simulation when all common are collected")

    args = parser.parse_args()
    
    with open(args.expansion_json) as f:
        data = json.load(f)
        expansion = Expansion.from_json(data)

    opened_hist = Counter()
    common_opened_hist = Counter()
    rarity_hist = {rarity: Counter() for rarity in expansion.cards}

    bought = defaultdict(int)

    for _ in range(args.runs):
        opened, all_common_at, collected = simulate(expansion, stop_at_all_common=args.stop_at_common)

        opened_hist.update([opened])
        common_opened_hist.update([all_common_at])

        for rarity, collection in collected.items():
            if collection.completed_at is not None:
                rarity_hist[rarity].update([collection.completed_at])
            if collection.bought:
                bought[rarity] += len(collection.bought)

    
    print(f"# Average packs opened: {_avg(opened_hist)}")
    print(f"# Average opened for all common: {_avg(common_opened_hist)}")

    print("\n# Average opened by rarity:")
    for rarity, hist in rarity_hist.items():
        print(f"  - {rarity}: {_avg(hist)}")

    if not bought:
        print("\n# None were bought")
    else:
        print("\n# Average bought by rarity:")
        for rarity, count in bought.items():
            print(f"  - {rarity}: {count / args.runs}")



if __name__ == '__main__':
    main()

