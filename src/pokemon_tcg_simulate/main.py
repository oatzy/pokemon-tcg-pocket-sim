import json
from argparse import ArgumentParser

from pokemon_tcg_simulate.collection import Collection
from pokemon_tcg_simulate.expansion import Expansion, create_common_mission
from pokemon_tcg_simulate.output import (
    BoughtStatistics,
    OpenedStatistics,
    report_bought_averages,
    report_opened_averages,
    report_opened_histograms,
    report_opened_percentiles,
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
    parser.add_argument(
        "--no-buy", action="store_false", dest="buy", help="do not buy cards"
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

    if args.stop_at_common:
        mission = create_common_mission(expansion)

    mission = mission and mission["cards"]

    # --- Simulation ---

    statistics = OpenedStatistics()
    bought = BoughtStatistics()

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
        )

        statistics.add(result)
        bought.add(result)

    # --- Results ---

    report_opened_averages(statistics)

    report_bought_averages(bought)

    if args.percentiles:
        report_opened_percentiles(statistics)

    if args.output_histograms:
        with open(args.output_histograms, "w") as f:
            report_opened_histograms(statistics, file=f)


if __name__ == "__main__":
    main()
