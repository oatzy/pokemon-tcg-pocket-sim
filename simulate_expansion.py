import json
import random
from argparse import ArgumentParser
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from itertools import accumulate, chain, cycle, islice
from typing import Optional


# max pack points that can be held at a time
MAX_PACK_POINTS = 2_500

# % prob of pulling a rare booster pack
RARE_PROBABILITY = 0.050

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
            v: tuple(chain.from_iterable(
                ((x.name, i) for i in x.iter_rare_cards(v)) 
                for x in self.rarities if x.rare
            ))
            for v in self.variants
        }

    @classmethod
    def from_json(cls, data):
        return Expansion(
            name=data["name"],
            variants=data["variants"],
            rarities=tuple(Rarity(**i) for i in sorted(data["rarities"], key=lambda x: -x["cost"]))
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
            self.collected.update(islice(self.rarity.iter_variant_cards(variant), count))
        if self.remaining() == 0:
            self.completed_at = 0


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
    prob_per_card = lambda x: max(x[1].rarity.offering_rate) / x[1].rarity.count(variant)
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
    return all(v.completed_at is not None for v in collection.values() if not v.rarity.rare)


def simulate(expansion, initial_state=None, stop_at_all_common=False):
    collected = {x.name: Collection(x) for x in expansion.rarities}

    pack_points = 0
    opened = 0

    if initial_state:
        pack_points = initial_state.get("pack_points", 0)
        for rarity, counts in initial_state["collected"].items():
            collected[rarity].load_initial_state(counts)

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
            collected[rarity].add(pull, opened)

        if required_pack_points(collected) == pack_points:
            buy_remaining(collected, pack_points, opened)
        
        if pack_points == MAX_PACK_POINTS and not completed_all(collected):
            #rarity, picked = pick_most_expensive(collected)
            rarity, picked = pick_rarest(collected, variant)
            collected[rarity].buy(picked, opened)
            pack_points -= collected[rarity].rarity.cost

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


def _percentiles(counter, total):
    points = [i * total for i in (0.5, 0.75, 0.9, 0.95)]
    results = []
    values = sorted(counter.items())
    
    offset = 0
    s = 0
    i = 0
    while offset < len(points) and i < len(values):
        if s >= points[offset]:
            results.append(values[i][0])
            offset += 1
        else:
            s += values[i][1]
            i += 1
    return results


def dump_histograms(histograms, file=None):
    upper = max(max(h.keys()) for h in histograms.values())
    keys = list(histograms)
    
    print(",".join(["opened", *keys]), file=file)
    for i in range(upper + 1):
        print(",".join(map(str, [i] + [histograms[k].get(i, 0) for k in keys])), file=file)


def main():
    # TODO: add support for sub-set goals and initial state
    # (i.e. re-implement the orignal mission simulation)
    parser = ArgumentParser()
    parser.add_argument("expansion_json", help="path to an expansion data json")
    parser.add_argument("-i", "--initial_state", help="path to initial state info")
    parser.add_argument("-r", "--runs", default=100, type=int, help="number of simulations to run")
    parser.add_argument("-c", "--stop-at-common", action="store_true", help="stop simulation when all common are collected")
    parser.add_argument("-p", "--percentiles", action="store_true", help="print percentiles")
    parser.add_argument("-o", "--output-histograms", help="path to dump histograms to")

    args = parser.parse_args()
    
    with open(args.expansion_json) as f:
        data = json.load(f)
        expansion = Expansion.from_json(data)

    initial_state = None
    if args.initial_state:
        with open(args.initial_state) as f:
            initial_state = json.load(f)

    opened_hist = Counter()
    common_opened_hist = Counter()
    rarity_hist = {x.name: Counter() for x in expansion.rarities}

    bought = defaultdict(int)

    for _ in range(args.runs):
        opened, all_common_at, collected = simulate(
            expansion, 
            initial_state=initial_state,
            stop_at_all_common=args.stop_at_common
        )

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
    
    if args.percentiles:
        print("\n# Percentiles")
        print("\nTarget, 50, 75, 90, 95")
        
        print(f"ALL, {', '.join(map(str, _percentiles(opened_hist, args.runs)))}")
        print(f"COMMON, {', '.join(map(str, _percentiles(common_opened_hist, args.runs)))}")
        for rarity, hist in rarity_hist.items():
            print(f"{rarity}, {', '.join(map(str, _percentiles(hist, args.runs)))}")

    if args.output_histograms:
        histograms = {"ALL": opened_hist, "COMMON": common_opened_hist, **rarity_hist}
        with open(args.output_histograms, 'w') as f:
            dump_histograms(histograms, file=f)


if __name__ == '__main__':
    main()

