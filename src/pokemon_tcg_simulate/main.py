import json
from argparse import ArgumentParser
from collections import Counter, defaultdict

from pokemon_tcg_simulate.expansion import Expansion
from pokemon_tcg_simulate.output import avg, percentiles, dump_histograms
from pokemon_tcg_simulate.simulation import simulate


def main():
    parser = ArgumentParser()
    parser.add_argument("expansion_json", help="path to an expansion data json")
    parser.add_argument("-i", "--initial-state", help="path to initial state json")
    parser.add_argument("-m", "--mission", help="path to mission json")
    parser.add_argument(
        "-r", "--runs", default=100, type=int, help="number of simulations to run"
    )
    parser.add_argument(
        "-c",
        "--stop-at-common",
        action="store_true",
        help="stop simulation when all common are collected",
    )
    parser.add_argument(
        "-p", "--percentiles", action="store_true", help="print percentiles"
    )
    parser.add_argument("-o", "--output-histograms", help="path to dump histograms to")

    args = parser.parse_args()

    # --- Setup ---

    with open(args.expansion_json) as f:
        data = json.load(f)
        expansion = Expansion.from_json(data)

    initial_state = None
    if args.initial_state:
        with open(args.initial_state) as f:
            initial_state = json.load(f)

    mission = None
    if args.mission:
        with open(args.mission) as f:
            mission = json.load(f)

    # --- Result containers ---

    # TODO: wrap in a dataclass
    opened_hist = Counter()
    common_opened_hist = Counter()
    rarity_hist = {x.name: Counter() for x in expansion.rarities}

    bought = defaultdict(int)

    # --- Simulation ---

    for _ in range(args.runs):
        result = simulate(
            expansion,
            initial_state=initial_state,
            mission=mission and mission["cards"],
            stop_at_all_common=args.stop_at_common,  # TODO: could be reimplemented as a mission
        )

        opened_hist.update([result.opened])
        common_opened_hist.update([result.all_common_at])

        for rarity, collection in result.collected.items():
            if collection.completed_at is not None:
                rarity_hist[rarity].update([collection.completed_at])
            if collection.bought:
                bought[rarity] += len(collection.bought)

    # --- Results ---
    # TODO: move to output.py

    print(f"# Average packs opened: {avg(opened_hist)}")
    print(f"# Average opened for all common: {avg(common_opened_hist)}")

    print("\n# Average opened by rarity:")
    for rarity, hist in rarity_hist.items():
        print(f"  - {rarity}: {avg(hist)}")

    if not bought:
        print("\n# None were bought")
    else:
        print("\n# Average bought by rarity:")
        for rarity, count in bought.items():
            print(f"  - {rarity}: {count / args.runs}")

    if args.percentiles:
        print("\n# Percentiles")
        print("\nTarget, 50, 75, 90, 95")

        print(f"ALL, {', '.join(map(str, percentiles(opened_hist, args.runs)))}")
        print(
            f"COMMON, {', '.join(map(str, percentiles(common_opened_hist, args.runs)))}"
        )
        for rarity, hist in rarity_hist.items():
            print(f"{rarity}, {', '.join(map(str, percentiles(hist, args.runs)))}")

    if args.output_histograms:
        histograms = {"ALL": opened_hist, "COMMON": common_opened_hist, **rarity_hist}
        with open(args.output_histograms, "w") as f:
            dump_histograms(histograms, file=f)


if __name__ == "__main__":
    main()
