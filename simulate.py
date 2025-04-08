import random
from collections import defaultdict, Counter
from dataclasses import dataclass


@dataclass
class Card:
    # pack points required, as boosters opened
    cost: int
    # probabilities for position 4 in regular booster
    pull_rate_4: float
    # probabilities for position 5 in regular booster
    pull_rate_5: float


# NOTE: these probabilities apply to Space-Time Smackdown
# Other expansions may vary, see "Offering rates" in app.
ONE_STAR = Card(80, 0.00214, 0.00857)
TWO_STAR = Card(250, 0.00041, 0.00166)

CARDS = {
    "Cynthia": TWO_STAR,
    "Gastrodon": ONE_STAR,
    "Spiritomb": ONE_STAR,
    # "Lucario": ONE_STAR,
    # "Garchomp": ONE_STAR,
}

# probability of a rare booster
RARE_PROB = 0.0005

# probability of pulling a card in a rare booster
# (same for all cards)
RARE_PULL = 0.03846

# how many pack points (in boosters) you have to begin with
START_POINTS = 500 // 5


def _sample(probability):
    cumm = 0
    r = random.random()

    for k, p in probability.items():
        cumm += p
        if r <= cumm:
            return k

    return None


def rare_booster():
    return random.random() <= RARE_PROB


def open_rare():
    pulled = []
    for _ in range(5):
        if pull := _sample({name: RARE_PULL for name in CARDS}):
            pulled.append(pull)
    return pulled


def open_regular():
    pulled = []

    # pick card 4
    if pull := _sample({name: c.pull_rate_4 for name, c in CARDS.items()}):
        pulled.append(pull)

    # pick card 5
    if pull := _sample({name: c.pull_rate_5 for name, c in CARDS.items()}):
        pulled.append(pull)

    return pulled


def cost_for_remaining(pulled):
    # how many boosters do we need to open to get enough points for the remaining cards?
    return sum(c.cost for name, c in CARDS.items() if name not in pulled)


def simulate():
    need = set(CARDS)

    # keep track of when we pulled each card, including duplicates
    pulled = defaultdict(list)
    opened = 0

    while True:

        if rare_booster():
            pull = open_rare()
        else:
            pull = open_regular()

        opened += 1

        for c in pull:
            pulled[c].append(opened)

        if set(pulled) == need:
            # we've pulled all the cards we need
            break

        if cost_for_remaining(pulled) <= opened + START_POINTS:
            # we have enough points
            break

    return opened, pulled


def main():
    runs = 10000

    outcomes = defaultdict(int)
    dupes = defaultdict(int)

    all_opened = Counter()

    excess = 0

    for _ in range(runs):
        opened, pulled = simulate()
        all_opened.update([opened])

        outcomes["(none)" if not pulled else ", ".join(sorted(pulled))] += 1

        for k, v in pulled.items():
            dupes[k] += len(v)

        excess += (opened + START_POINTS) - cost_for_remaining(pulled)

    print(f"# Average boosters opened - {sum(all_opened.elements()) / runs}")

    most_common = all_opened.most_common(1)[0]
    above_mode = sum(v for k, v in all_opened.items() if k > most_common[0])
    print(f"\n# Most likely number opened - {most_common[0]} ({most_common[1]/runs})")
    print(f"# Probability above most common - {above_mode / runs}")

    print(f"\n# Average left over points - {5 * excess / runs}")

    print("\n# Average copies of each card")
    for k, v in sorted(dupes.items(), key=lambda i: i[1]):
        print(f" - {k}: {v/runs}")

    print("\n# Probabilities of card sets")
    for k, v in sorted(outcomes.items(), key=lambda i: i[1]):
        print(f" - {k}: {v/runs}")


if __name__ == "__main__":
    main()
