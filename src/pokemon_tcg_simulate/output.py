from collections import Counter, defaultdict
from dataclasses import dataclass, field

from pokemon_tcg_simulate.collection import Collection

# TODO: CardStatistics; dupes, missing, etc.


@dataclass(kw_only=True)
class OpenedStatistics:
    # histogram of number of packs opened
    opened_hist: Counter = field(init=False, default_factory=Counter)

    # histogram of number of packs opened for all common cards
    common_opened_hist: Counter = field(init=False, default_factory=Counter)

    # histogram of number of packs opened to complete each rarity
    rarity_hist: dict[str, Counter] = field(init=False, default_factory=dict)

    def add(self, result: Collection):
        self.opened_hist.update([result.opened])
        self.common_opened_hist.update([result.all_common_at])

        for rarity, collection in result.collected.items():
            if collection.completed_at is not None:
                if rarity not in self.rarity_hist:
                    self.rarity_hist[rarity] = Counter()
                self.rarity_hist[rarity].update([collection.completed_at])


@dataclass(kw_only=True)
class BoughtStatistics:
    # number of cards bought for each rarity
    bought: dict[str, Counter] = field(
        init=False, default_factory=lambda: defaultdict(int)
    )

    runs: int = field(init=False, default=0)

    def add(self, result: Collection):
        self.runs += 1
        for rarity, collection in result.collected.items():
            if collection.bought:
                self.bought[rarity] += len(collection.bought)


def report_opened_averages(stats: OpenedStatistics, file=None):
    print(f"# Average packs opened: {avg(stats.opened_hist)}", file=file)
    print(
        f"# Average opened for all common: {avg(stats.common_opened_hist)}",
        file=file,
    )

    print("\n# Average opened by rarity:", file=file)
    for rarity, hist in stats.rarity_hist.items():
        if hist:
            print(f"  - {rarity}: {avg(hist)}", file=file)


def report_opened_percentiles(stats: OpenedStatistics, file=None):
    # TODO: configurable percentiles
    print("\n# Percentiles", file=file)
    print("\nTarget, 50, 75, 90, 95", file=file)

    print(f"ALL, {', '.join(map(str, percentiles(stats.opened_hist)))}", file=file)
    print(
        f"COMMON, {', '.join(map(str, percentiles(stats.common_opened_hist)))}",
        file=file,
    )
    for rarity, hist in stats.rarity_hist.items():
        print(f"{rarity}, {', '.join(map(str, percentiles(hist)))}", file=file)


def report_opened_histograms(stats: OpenedStatistics, file=None):
    histograms = {
        "ALL": stats.opened_hist,
        "COMMON": stats.common_opened_hist,
        **stats.rarity_hist,
    }
    dump_histograms(histograms, file=file)


def report_bought_averages(stats: BoughtStatistics, file=None):
    if not stats.bought:
        print("# None were bought", file=file)
    else:
        print("\n# Average bought by rarity:", file=file)
        for rarity, count in stats.bought.items():
            print(f"  - {rarity}: {count / stats.runs}", file=file)


def avg(counter: Counter):
    if el := list(counter.elements()):
        return sum(el) / len(el)
    return None


def percentiles(counter: Counter):
    # TODO: configurable percentiles
    values = sorted(counter.items())
    total = counter.total()
    points = [i * total for i in (0.5, 0.75, 0.9, 0.95)]
    results = []

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


def dump_histograms(histograms: list[Counter], file=None):
    upper = max(max(h.keys()) for h in histograms.values())
    keys = list(histograms)

    print(",".join(["opened", *keys]), file=file)
    for i in range(upper + 1):
        print(
            ",".join(map(str, [i] + [histograms[k].get(i, 0) for k in keys])), file=file
        )
