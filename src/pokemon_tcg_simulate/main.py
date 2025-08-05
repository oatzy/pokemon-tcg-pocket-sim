import json
import time
from argparse import ArgumentParser

from pokemon_tcg_simulate.collection import Collection
from pokemon_tcg_simulate.expansion import Expansion, create_common_mission
from pokemon_tcg_simulate.output import (
    BoughtStatistics,
    CardStatistics,
    OpenedStatistics,
    report_opened_histograms,
    format_markdown,
)
from pokemon_tcg_simulate.simulation import simulate


def main():
    parser = ArgumentParser()
    parser.add_argument("expansion_json", help="path to an expansion data json")
    parser.add_argument("-i", "--initial-state", help="path to initial state json")

    mission_group = parser.add_mutually_exclusive_group()
    mission_group.add_argument("-m", "--mission", help="path to mission json")
    mission_group.add_argument(
        "-c",
        "--stop-at-common",
        action="store_true",
        help="stop simulation when all common are collected",
    )

    parser.add_argument(
        "-r", "--runs", default=100, type=int, help="number of simulations to run"
    )
    parser.add_argument("--max-opened", type=int, help="max packs to open")
    parser.add_argument(
        "--no-buy", action="store_false", dest="buy", help="do not buy cards"
    )
    parser.add_argument("--json", action="store_true", help="output results as JSON")
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

    if args.stop_at_common:
        mission = create_common_mission(expansion)

    mission = mission and mission["cards"]

    results = {}
    results["metadata"] = {
        "expansion": expansion.name,
        "runs": args.runs,
        "mission": mission and mission.get("mission"),
    }

    # --- Simulation ---

    start = time.time()

    statistics = {}

    if args.max_opened:
        statistics["cards"] = CardStatistics()
    else:
        statistics["opened"] = OpenedStatistics()
    if args.buy:
        statistics["bought"] = BoughtStatistics()

    for _ in range(args.runs):
        # Create a new collection for each run
        # as collection is mutated during simulation
        collection = Collection.from_json(expansion, mission=mission)

        if initial_state:
            collection.load_initial_state(initial_state)

        result = simulate(
            expansion,
            collection,
            buy_cards=args.buy,
            max_opened=args.max_opened,
        )

        for stat in statistics.values():
            stat.add(result)

    # --- Results ---

    end = time.time()
    results["runtime"] = {
        "total": end - start,
        "per_run": (end - start) / args.runs,
    }

    results["statistics"] = {name: stat.summary() for name, stat in statistics.items()}

    if args.json:
        print(json.dumps(results, indent=2))

    else:
        for stat in results["statistics"].values():
            print(format_markdown(stat))

    if args.output_histograms:
        with open(args.output_histograms, "w") as f:
            report_opened_histograms(statistics, file=f)


if __name__ == "__main__":
    main()
