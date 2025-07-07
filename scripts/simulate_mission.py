"""
Original iteration of the simulation

Focused specifically on the Champion of Sinnoh secret mission.
"""

import random
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from functools import lru_cache, partial
from itertools import chain


@dataclass
class Card:
    # pack points required, as boosters opened
    cost: int
    # probabilities for position 4 in regular booster
    pull_rate_4: float
    # probabilities for position 5 in regular booster
    pull_rate_5: float
    # booster variant
    booster: str


# NOTE: these probabilities apply to Space-Time Smackdown
# Other expansions may vary, see "Offering rates" in app.
ONE_STAR = partial(Card, 80, 0.00214, 0.00857)
TWO_STAR = partial(Card, 250, 0.00041, 0.00166)

CARDS = {
    "Cynthia": TWO_STAR("Palkia"),
    "Gastrodon": ONE_STAR("Palkia"),
    # "Spiritomb": ONE_STAR("Palkia"),
    # "Garchomp": ONE_STAR("Palkia"),
    # "Lucario": ONE_STAR("Dialga"),
}

# probability of a rare booster
RARE_PROB = 0.0005

# probability of pulling a card in a rare booster
# (same for all cards)
RARE_PULL = 0.03846

# how many pack points (in boosters) you have to begin with
START_POINTS = 1065 // 5


def _sample(probabilities):
    cumm = 0
    r = random.random()

    for k, p in probabilities:
        cumm += p
        if r <= cumm:
            return k

    return None


# card probability functions
# standalone instead of lambdas so they can be cached
def _pull_rare(_):
    return RARE_PULL


def _pull_4(c):
    return c.pull_rate_4


def _pull_5(c):
    return c.pull_rate_5


@lru_cache
def _probabilities(booster, card_probability):
    return [
        (name, card_probability(c)) for name, c in CARDS.items() if c.booster == booster
    ]


def open_rare(booster):
    pulled = []
    for _ in range(5):
        if pull := _sample(_probabilities(booster, _pull_rare)):
            pulled.append(pull)
    return pulled


def open_regular(booster):
    pulled = []

    # pick card 4
    if pull := _sample(_probabilities(booster, _pull_4)):
        pulled.append(pull)

    # pick card 5
    if pull := _sample(_probabilities(booster, _pull_5)):
        pulled.append(pull)

    return pulled


def rare_booster():
    return random.random() <= RARE_PROB


@lru_cache
def cost_for_remaining(pulled):
    # how many boosters do we need to open to get enough points for the remaining cards?
    return sum(c.cost for name, c in CARDS.items() if name not in pulled)


def rotating_generator(booster_ratio):
    # TODO: ignore booster if all cards pulled for it
    boosters = deque(chain.from_iterable([k] * v for k, v in booster_ratio.items()))

    def inner(opened, pulled):
        boosters.rotate(-1)
        return boosters[0]

    return inner


def dialga_first(opened, pulled):
    # TODO: generalise
    if "Lucario" not in pulled and opened["Dialga"] < 80:
        return "Dialga"
    return "Palkia"


def simulate(booster_generator):
    need = set(CARDS)

    # keep track of when we pulled each card, including duplicates
    pulled = defaultdict(list)
    opened = defaultdict(int)
    total_opened = 0

    while True:
        booster = booster_generator(opened, pulled)

        if rare_booster():
            pull = open_rare(booster)
        else:
            pull = open_regular(booster)

        opened[booster] += 1
        total_opened += 1

        for c in pull:
            pulled[c].append(total_opened)

        if set(pulled) == need:
            # we've pulled all the cards we need
            break

        if cost_for_remaining(tuple(pulled)) <= total_opened + START_POINTS:
            # we have enough points
            break

    return opened, pulled


def main():
    runs = 10000

    # ratio of booster variants to open
    booster_ratio = {"Palkia": 1, "Dialga": 0}

    outcomes = defaultdict(int)
    dupes = defaultdict(int)

    boosters_opened = defaultdict(int)
    opened_hist = Counter()

    excess = 0

    for _ in range(runs):
        # opened, pulled = simulate(dialga_first)
        opened, pulled = simulate(rotating_generator(booster_ratio))

        for k, v in opened.items():
            boosters_opened[k] += v
        num_opened = sum(opened.values())
        opened_hist.update([num_opened])

        outcomes["(none)" if not pulled else ", ".join(sorted(pulled))] += 1

        for k, v in pulled.items():
            dupes[k] += len(v)

        excess += (num_opened + START_POINTS) - cost_for_remaining(tuple(pulled))

    avg = int(round(sum(opened_hist.elements()) / runs))
    print(f"# Average boosters opened - {avg} ({avg * 5} pts)")
    for k, v in boosters_opened.items():
        print(f" - {k} - {v / runs}")

    most_common = opened_hist.most_common(1)[0]
    above_mode = sum(v for k, v in opened_hist.items() if k > most_common[0])
    print(f"\n# Most likely number opened - {most_common[0]} ({most_common[1] / runs})")
    print(f"# Probability above most common - {above_mode / runs}")

    print(f"\n# Average left over points - {5 * excess / runs}")

    print("\n# Average copies of each card")
    for k, v in sorted(dupes.items(), key=lambda i: i[1]):
        print(f" - {k}: {v / runs}")

    print("\n# Probabilities of card sets")
    for k, v in sorted(outcomes.items(), key=lambda i: i[1]):
        print(f" - {k}: {v / runs}")


if __name__ == "__main__":
    main()
