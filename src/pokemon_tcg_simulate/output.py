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
        if result.all_common_at is not None:
            self.common_opened_hist.update([result.all_common_at])

        for rarity, collection in result.collected.items():
            if collection.completed_at is not None:
                if rarity not in self.rarity_hist:
                    self.rarity_hist[rarity] = Counter()
                self.rarity_hist[rarity].update([collection.completed_at])

    def summary(self):
        return {
            "average_opened": {
                "value": avg(self.opened_hist),
                "description": "Average packs opened",
            },
            "average_opened_for_common": {
                "value": avg(self.common_opened_hist),
                "description": "Average opened for all common",
            },
            "average_opened_by_rarity": {
                "value": {
                    rarity: avg(hist) for rarity, hist in self.rarity_hist.items()
                },
                "description": "Average opened by rarity",
            },
        }


@dataclass(kw_only=True)
class CardStatistics:
    cards_by_rarity: dict[str, Counter] = field(
        init=False, default_factory=lambda: defaultdict(Counter)
    )

    cards_missing_by_rarity: dict[str, Counter] = field(
        init=False, default_factory=lambda: defaultdict(Counter)
    )

    duplicates_by_rarity: dict[str, Counter] = field(
        init=False, default_factory=lambda: defaultdict(Counter)
    )

    common_collected: Counter = field(init=False, default_factory=Counter)

    total_collected: Counter = field(init=False, default_factory=Counter)

    # TODO: common completed, rare completed
    # TODO: variants

    def add(self, result: Collection):
        # TODO: include raw numbers and percentages
        self.common_collected.update(
            [sum(r.count() for r in result.collected.values() if not r.rarity.rare)]
        )
        self.total_collected.update([sum(r.count() for r in result.collected.values())])

        for rarity, collection in result.collected.items():
            count = collection.count()
            size = collection.size()
            if size > 0:
                self.cards_by_rarity[rarity].update([count / size])
                self.cards_missing_by_rarity[rarity].update(
                    [collection.remaining() / size]
                )
            if count > 0:
                self.duplicates_by_rarity[rarity].update([collection.total() / count])

    def summary(self):
        return {
            "common_collected": {
                "value": avg(self.common_collected),
                "description": "Total unique common cards collected",
            },
            "total_collected": {
                "value": avg(self.total_collected),
                "description": "Total unique cards collected",
            },
            "cards_by_rarity": {
                "value": {
                    rarity: 100 * avg(hist)
                    for rarity, hist in self.cards_by_rarity.items()
                },
                "description": "Average percent collected by rarity",
            },
            "cards_missing_by_rarity": {
                "value": {
                    rarity: 100 * avg(hist)
                    for rarity, hist in self.cards_missing_by_rarity.items()
                },
                "description": "Average percent missing by rarity",
            },
            "duplicates_by_rarity": {
                "value": {
                    rarity: avg(hist)
                    for rarity, hist in self.duplicates_by_rarity.items()
                },
                "description": "Average number of copies of each card by rarity",
            },
        }


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

    def summary(self):
        return {
            "average_bought_by_rarity": {
                "value": (
                    {rarity: count / self.runs for rarity, count in self.bought.items()}
                    if self.bought
                    else None
                ),
                "description": "Average bought by rarity",
            }
        }


def format_markdown(stats: dict) -> str:
    # TODO: round numbers to 2 decimal places
    lines = []
    for stat in stats.values():
        if isinstance(stat["value"], dict):
            lines.append(f"# {stat['description']}")
            # TODO: sorting (maybe not here)
            for key, value in stat["value"].items():
                lines.append(f"- {key}: {value}")
        else:
            lines.append(f"# {stat['description']}: {stat['value']}")
        lines.append("")  # Add a blank line for separation
    return "\n".join(lines)


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
