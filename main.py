import sys
import pprint
from typing import List, Tuple
import argparse
import logging

from src.artefact import Artefact, Snake, Ladder
from src.player import Player
from src.die import Die
from src.snake_ladder_simulation import Game
from src.simulation_stats import SimulationStats
from src.game_exceptions import EXCEPTION_SNAKE_LADDER_SIMULATOR


def print_simultation_statistics(sim_stats: SimulationStats, number_of_players):
    print()
    print(
        f"STATISTICS FOR {number_of_players} PLAYERS OVER {sim_stats.number_of_simulations} SIMULATION RUN(S)"
    )

    print("Winning rolls:")
    print(f"Minimum = {sim_stats.min_number_of_win_rolls}")
    print(f"Average = {sim_stats.avg_number_of_win_rolls}")
    print(f"Maximum = {sim_stats.max_number_of_win_rolls}")

    print()
    print("Distance climbed:")
    print(f"Minimum = {sim_stats.min_distance_climbed}")
    print(f"Average = {sim_stats.avg_distance_climbed}")
    print(f"Maximum = {sim_stats.max_distance_climbed}")

    print()
    print("Distance slid:")
    print(f"Minimum = {sim_stats.min_distance_slid}")
    print(f"Average = {sim_stats.avg_distance_slid}")
    print(f"Maximum = {sim_stats.max_distance_slid}")

    print()
    print("Unlucky rolls:")
    print(f"Minimum = {sim_stats.min_unlucky_rolls}")
    print(f"Average = {sim_stats.avg_unlucky_rolls}")
    print(f"Maximum = {sim_stats.max_unlucky_rolls}")

    print()
    print("Lucky rolls:")
    print(f"Minimum = {sim_stats.min_lucky_rolls}")
    print(f"Average = {sim_stats.avg_lucky_rolls}")
    print(f"Maximum = {sim_stats.max_lucky_rolls}")

    print()
    print(f"Biggest climb in a streak = {sim_stats.biggest_climb_in_a_streak}")
    print(f"Biggest slide in a streak = {sim_stats.biggest_slide_in_a_streak}")
    print(f"Longest streak: {sim_stats.max_streak}")

    print()
    return


def read_conf_file() -> Tuple[bool, int, int, List[List[int]], List[List[int]]]:
    def str_to_int(s):
        try:
            return int(s)
        except ValueError:
            return -1

    CONFIG_FILENAME = "game.conf"
    isSuccess: bool = False
    number_of_simulations: int = 0
    number_of_players: int = 0
    snakes_conf: List[List[int]] = []
    ladders_conf: List[List[int]] = []
    try:
        with open(CONFIG_FILENAME) as conf_file:
            raw_config_lines = conf_file.readlines()
    except FileNotFoundError:
        print(f"Please supply a config file by name {CONFIG_FILENAME}")
        return (
            isSuccess,
            number_of_simulations,
            number_of_players,
            snakes_conf,
            ladders_conf,
        )

    for line in raw_config_lines:
        line = line.strip().split("#")[0]  # Strip away the comments
        if not line:
            continue
        config = line.split("=")
        if len(config) < 2:
            break
        key, value = config[0].strip().upper(), config[1].strip()
        if key == "NUMBER_OF_SIMULATIONS":
            number_of_simulations = str_to_int(value)
            if number_of_simulations < 0:
                break
            continue
        if key == "NUMBER_OF_PLAYERS":
            number_of_players = str_to_int(value)
            if number_of_players < 0:
                break
            continue
        if key == "SNAKE" or key == "LADDER":
            positions_conf = value.split(",")
            if len(positions_conf) != 2:
                break
            positions = list(map(lambda x: str_to_int(x.strip()), positions_conf))
            if positions.count(-1) != 0:
                break
            if key == "SNAKE":
                snakes_conf.append(positions)
            else:
                ladders_conf.append(positions)
    else:  # For-else
        isSuccess = True

    if not isSuccess:
        print(f"Invalid configuration line: {line}")

    return (
        isSuccess,
        number_of_simulations,
        number_of_players,
        snakes_conf,
        ladders_conf,
    )


def setup_argument_parser() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Snake & Ladder Simulator")
    parser.add_argument("--verbose", "-v", action="count", default=0)
    args = parser.parse_args(sys.argv[1:])
    return args


def setup_logger(args: argparse.Namespace):
    level_to_set = logging.WARNING
    if args.verbose >= 2:
        level_to_set = logging.DEBUG
    elif args.verbose == 1:
        level_to_set = logging.INFO
    logging.basicConfig(format="%(message)s", level=level_to_set)


def main() -> bool:
    players: List[Player] = []
    snakes: List[Artefact] = []
    ladders: List[Artefact] = []

    args = setup_argument_parser()
    setup_logger(args)

    # Read game configurations
    (
        isSuccess,
        number_of_simulations,
        number_of_players,
        snakes_conf,
        ladders_conf,
    ) = read_conf_file()
    if not isSuccess:
        print("Error reading config file. Quitting")
        return False

    if number_of_players == 0:
        print("There are no players. Quitting")
        return False

    if number_of_simulations == 0:
        print("No simulations to run. Quitting")
        return False

    # Instantiate snakes as per the configuration
    for head, tail in snakes_conf:
        try:
            snakes.append(Snake(head=head, tail=tail))
        except EXCEPTION_SNAKE_LADDER_SIMULATOR as exception_sim:
            print(exception_sim.message)
            print("Please fix the configuration and re-rerun")
            return False

    # Instantiate ladders as per the configuration
    for bottom, top in ladders_conf:
        try:
            ladders.append(Ladder(top=top, bottom=bottom))
        except EXCEPTION_SNAKE_LADDER_SIMULATOR as exception_sim:
            print(exception_sim.message)
            print("Please fix the configuration and re-rerun")
            return False

    # Instantiate players as per the configuration
    for n in range(1, number_of_players + 1):
        players.append(Player(f"Player_{n}"))

    print("CONFIGURATION:")
    print(f"Number of simulations: {number_of_simulations}")
    print(f"Number of players: {number_of_players}")
    print(f"Number of snakes: {len(snakes)}")
    print(f"Number of ladders: {len(ladders)}")
    logging.debug(pprint.pformat(snakes))
    logging.debug(pprint.pformat(ladders))
    print()

    # Set up the game
    game = Game(Die(), number_of_simulations)
    game.add_players(players)
    isSuccess, err_message = game.add_artefacts(snakes + ladders)
    if not isSuccess:
        print(f"Error: {err_message}")
        print("Please fix the configuration and re-rerun")
        return False

    # Run the simulations
    game.run_simulations(print_progress=True)

    game.calculate_simultation_statistics()
    print_simultation_statistics(game.sim_stats, number_of_players)

    return True


if __name__ == "__main__":
    main()
