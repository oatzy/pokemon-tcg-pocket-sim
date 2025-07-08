import json
from argparse import ArgumentParser

from pokemon_tcg_simulate.expansion import Expansion
from pokemon_tcg_simulate.output import ResultReporter, dump_histograms
from pokemon_tcg_simulate.simulation import simulate


def main():
    parser = ArgumentParser()
    parser.add_argument("expansion_json", help="path to an expansion data json")
    parser.add_argument("-i", "--initial-state", help="path to initial state json")
    parser.add_argument("-m", "--mission", help="path to mission json")
    parser.add_argument(
        "-r", "--runs", default=100, type=int, help="number of simulations to run"
    )
    # TODO: make stop-at-common mutually exclusive with mission
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

    # --- Simulation ---

    results_reporter = ResultReporter(
        runs=args.runs,
        percentiles=args.percentiles,
    )

    for _ in range(args.runs):
        result = simulate(
            expansion,
            initial_state=initial_state,
            mission=mission and mission["cards"],
            stop_at_all_common=args.stop_at_common,  # TODO: could be reimplemented as a mission
        )

        results_reporter.add(result)

    # --- Results ---

    results_reporter.report()

    if args.output_histograms:
        # TODO: leaky abstraction
        histograms = {
            "ALL": results_reporter.opened_hist,
            "COMMON": results_reporter.common_opened_hist,
            **results_reporter.rarity_hist,
        }
        with open(args.output_histograms, "w") as f:
            dump_histograms(histograms, file=f)


if __name__ == "__main__":
    main()
