import argparse


def pysh_parser() -> [int, dict]:
    """import this module and call this method before creating a GeneSpawner"""

    parser = argparse.ArgumentParser()

    # Arguments for PushEstimator
    # All of these arguments have defaults built into PushEstimator, and are therefore not required
    # only --verbose has a changed default value to make it easier for the user
    parser.add_argument("--search", type=str, required=False,
                        choices=["GA", "SA"], help="the search algorithms")
    parser.add_argument("--selector", type=str, required=False,
                        choices=["roulette", "tournament", "lexicase", "elite"],
                        help="the selector to use when selecting parents")
    parser.add_argument("--variation_strategy", type=str, required=False,
                        choices=["deletion", "addition", "alternation", "genesis", "cloning", "umad", "umad-shrink",
                                 "umad-grow"],
                        help="describes a collection of VariationOperators and how frequently to use them")
    parser.add_argument("--population_size", type=int, required=False,
                        help="number of individuals held in the population each generation")
    parser.add_argument("--max_generations", type=int, required=False,
                        help="number of generations to run the search algorithm")
    parser.add_argument("--initial_genome_size", type=int, required=False, nargs=2,
                        help="range of genome sizes to produce during initialization")
    parser.add_argument("--simplification_steps", type=int, required=False,
                        help="number of simplification iterations to apply to the best Push program produced")
    parser.add_argument("--parallelism", type=bool, required=False,
                        help="sets the number of processes to spawn for use when performing embarrassingly parallel "
                             "tasks")
    parser.add_argument("--verbose", type=int, required=False, choices=[0, 1, 2], default=2,
                        help="indicates if verbose printing should be used during searching")

    # parse command line
    args = parser.parse_args()

    # add all command line arguments to a dictionary
    est_dict_args = dict(search=args.search, selector=args.selector, variation_strategy=args.variation_strategy,
                         population_size=args.population_size, max_generations=args.max_generations,
                         initial_genome_size=args.initial_genome_size, simplification_steps=args.simplification_steps,
                         parallelism=args.parallelism, verbose=args.verbose)

    # remove all command line arguments that were not entered
    # the defaults stored in GeneSpawner and PushEstimator will be used
    est_dict = {key: val for key, val in est_dict_args.items() if val != None}

    # returns dictionary of parameters for PushEstimator
    return est_dict
