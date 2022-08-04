import sys
from typing import Union, List, Tuple, Dict, Set
import pprint
import argparse
import logging

from constants import Constants as Const
from player import Player
from artefact import Artefact, Snake, Ladder
from die import Die
from game_stats import GameStats
from game_exceptions import (
    get_user_friendly_error_message,
    ERROR_MESSAGE_ACTIVATION_CLASH,
    ERROR_MESSAGE_ACTIVATION_DUPLICATED,
    ERROR_MESSAGE_UNSUPPORTED_ARTEFACT,
)


class Game:
    def __init__(self, die: Die, number_of_simulations: int):
        self.number_of_simulations = number_of_simulations
        self.players: List[Player] = []
        self.snakes: List[Snake] = []
        self.ladders: List[Ladder] = []
        self.die: Die = die
        self.activation_points_map: Dict[int, Artefact] = dict()
        self.termination_points: Set[int] = set()
        self.lucky_positions: Set[int] = set()
        self.curr_player_ndx: int = 0
        self.game_stats: List[GameStats] = []

        for n in range(number_of_simulations):
            self.game_stats.append(GameStats())

    def reset_game_state(self) -> None:
        self.curr_player_ndx = 0

        for player in self.players:
            player.init_player_stats()

    def add_players(self, players: List[Player]) -> None:
        player: Player
        for player in players:
            self.players.append(player)

    def update_lucky_positions(self, snake: Snake, heads_of_snakes_on_board: List[int]):
        # This method records lucky positions (1 or 2 positions aways from snakes)
        lucky_positions_after_snake = [snake.head + 1, snake.head + 2]
        lucky_positions_before_snake = [snake.head - 1, snake.head - 2]

        for after in lucky_positions_after_snake:
            if (
                after not in heads_of_snakes_on_board
                and after <= Const.BOARD_POSITION_MAX
            ):
                self.lucky_positions.add(after)
        for before in lucky_positions_before_snake:
            if (
                before not in heads_of_snakes_on_board
                and before >= Const.BOARD_POSITION_MIN
            ):
                self.lucky_positions.add(before)

    def add_artefacts(self, artefacts: List[Artefact]) -> Tuple[bool, str]:
        # Ensure that the snakes and the ladders do not start at the same position
        # (take into consideration snakes and ladders in this list, and alse those
        # already placed on the board)
        all_activation_points = [
            artefact.activation_point for artefact in artefacts
        ] + list(self.activation_points_map.keys())
        all_activation_points_unique = set(all_activation_points)
        logging.debug(f"add_artefact: {all_activation_points=}")
        logging.debug(f"add_artefact: {all_activation_points_unique=}")
        if len(all_activation_points) != len(all_activation_points_unique):
            return False, ERROR_MESSAGE_ACTIVATION_DUPLICATED

        # Ensure that the snakes and the ladders do not have the start and the end
        # on the same position
        # (take into consideration snakes and ladders in this list, and alse those
        # already placed on the board)
        all_termination_points = [
            artefact.termination_point for artefact in artefacts
        ] + list(self.termination_points)
        all_termination_points_unique = set(all_termination_points)
        logging.debug(f"add_artefacts: {all_termination_points=}")
        logging.debug(f"add_artefacts: {all_termination_points_unique=}")
        overlaps = all_activation_points_unique & all_termination_points_unique
        logging.debug(
            f"add_artefacts: Overlap between all (old and new) activation and termination points = {overlaps}"
        )
        if len(overlaps):
            return (False, ERROR_MESSAGE_ACTIVATION_CLASH)

        # Update internal records of activation, termination and lucky positions
        new_activation_points_map = {
            artefact.activation_point: artefact for artefact in artefacts
        }
        self.activation_points_map.update(new_activation_points_map)
        self.termination_points = all_termination_points_unique
        logging.debug(f"add_artefacts: Updated {self.activation_points_map=}")
        logging.debug(f"add_artefacts: Updated {self.termination_points=}")

        # Finally add all the artefacts to the board
        heads_of_snakes_on_board = [
            x[0] for x in self.activation_points_map.items() if isinstance(x[1], Snake)
        ]
        for artefact in artefacts:
            if isinstance(artefact, Snake):
                self.update_lucky_positions(artefact, heads_of_snakes_on_board)
                self.snakes.append(artefact)
            elif isinstance(artefact, Ladder):
                self.ladders.append(artefact)
            else:
                return (
                    False,
                    ERROR_MESSAGE_UNSUPPORTED_ARTEFACT,
                )  # TODO: Write test for this

        logging.debug(f"add_artefacts: {len(self.lucky_positions)=}")
        logging.debug(f"add_artefacts: {self.lucky_positions=}")

        return True, ""

    def play(self, simulation_number) -> Union[Player, None]:
        winner: Union[Player, None] = None
        curr_streak = []

        # simulation_number is expected to be 1-based
        if simulation_number < 1 or simulation_number > self.number_of_simulations:
            print(
                f"Invalid simulation number ({simulation_number}). Expected number between 1 and {self.number_of_simulations}"
            )
            return None

        simulation_number_offset = simulation_number - 1

        while True:
            winner = self.spot_winner()
            if winner:
                break

            curr_player: Player = self.players[self.curr_player_ndx]

            die_roll = self.die.roll()
            self.move_token(curr_player, die_roll)

            curr_player.number_of_rolls += 1
            curr_streak.append(die_roll)
            if die_roll != Const.DIE_ROLL_REPEAT:
                if sum(curr_streak) > sum(curr_player.max_streak):
                    curr_player.max_streak = curr_streak
                self.curr_player_ndx = (self.curr_player_ndx + 1) % len(self.players)
                curr_streak = []

        self.record_game_stat(winner, simulation_number_offset)
        return winner

    def record_game_stat(self, winner: Player, simulation_number_offset):
        # TODO: Write test for game_stat calculations
        game_stat = self.game_stats[simulation_number_offset]
        game_stat.game_number_of_rolls_to_win = winner.number_of_rolls
        player: Player
        for player in self.players:
            if sum(player.max_streak) > sum(game_stat.game_max_streak):
                game_stat.game_max_streak = player.max_streak
            game_stat.game_total_lucky_rolls += player.number_of_lucky_rolls
            game_stat.game_total_unlucky_rolls += player.number_of_unlucky_rolls
            game_stat.game_total_distance_slid += player.total_distance_slid
            game_stat.game_total_distance_climbed += player.total_distance_climbed
            game_stat.game_max_distance_slide = max(
                player.max_distance_slid, game_stat.game_max_distance_slide
            )
            game_stat.game_max_distance_climbed = max(
                player.max_distance_climbed, game_stat.game_max_distance_climbed
            )

    def spot_winner(self) -> Union[Player, None]:  # TODO: Write test for this
        player: Player
        for player in self.players:
            if player.token_position == Const.BOARD_POSITION_MAX:
                return player
        return None

    def move_token(self, player: Player, die_roll: int) -> int:
        """
        This method moves the token on the board and also maintains
        player's own state and stats
        """
        logging.debug(f"Moving {player.name} by {die_roll}")
        if player.token_position + die_roll > Const.BOARD_POSITION_MAX:
            # Bounce back if we are overshooting the board
            die_roll = Const.BOARD_POSITION_MAX - (player.token_position + die_roll)
            logging.info(f"{player.name} bouncing back by {die_roll}")

        # Check if this the last lucky roll from the lucky zone
        if (
            player.token_position <= Const.BOARD_LAST_LUCKY_ZONE_BEGIN
            and player.token_position + die_roll == Const.BOARD_POSITION_MAX
        ):
            # TODO: Write a test for this
            logging.info(
                f"{player.name} rolled a last lucky roll {die_roll} while at {player.token_position}"
            )
            player.number_of_lucky_rolls += 1

        player.token_position += die_roll

        # Check if the player missed a snake by 1 or 2 positions
        if player.token_position in self.lucky_positions:
            # TODO: Write a test for this
            logging.info(
                f"{player.name} avoided a snake by landing on a lucky position: {player.token_position}"
            )
            player.number_of_lucky_rolls += 1

        # Act if we have arrived at the head of snake, or start of a ladder
        if player.token_position in self.activation_points_map:
            artefact: Artefact = self.activation_points_map[player.token_position]
            player.token_position = artefact.termination_point
            if isinstance(artefact, Snake):
                player.number_of_unlucky_rolls += 1
                player.total_distance_slid += artefact.distance
                player.max_distance_slid = max(
                    artefact.distance, player.max_distance_slid
                )
                logging.info(
                    f"{player.name} encountered snake and slid {artefact.distance} units from {artefact.activation_point} to {artefact.termination_point}"
                )
            elif isinstance(artefact, Ladder):
                player.number_of_lucky_rolls += 1
                player.total_distance_climbed += artefact.distance
                player.max_distance_climbed = max(
                    artefact.distance, player.max_distance_climbed
                )
                logging.info(
                    f"{player.name} encountered ladder and climbed {artefact.distance} units from {artefact.activation_point} to {artefact.termination_point}"
                )
        return die_roll


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


def print_simultation_statistics(game_stats: List[GameStats], number_of_players):
    # TODO: Decouple calculation and printing
    # TODO: Write test for these simulations-level calculations
    number_of_simulations = len(game_stats)

    sum_number_of_win_rolls = 0
    sum_distance_climbed = 0
    sum_distance_slid = 0
    sum_unlucky_rolls = 0
    sum_lucky_rolls = 0
    min_number_of_win_rolls = sys.maxsize
    avg_number_of_win_rolls: float = 0.0
    max_number_of_win_rolls = 0
    min_distance_climbed = sys.maxsize
    avg_distance_climbed: float = 0.0
    max_distance_climbed = 0
    min_distance_slid = sys.maxsize
    avg_distance_slid: float = 0.0
    max_distance_slid = 0
    biggest_climb = 0
    biggest_slide = 0
    min_unlucky_rolls = sys.maxsize
    avg_unlucky_rolls: float = 0.0
    max_unlucky_rolls = 0
    min_lucky_rolls = sys.maxsize
    avg_lucky_rolls: float = 0.0
    max_lucky_rolls = 0
    max_streak = [0]
    for game_stat in game_stats:
        # print(f"{game_stat}")
        min_number_of_win_rolls = min(
            game_stat.game_number_of_rolls_to_win, min_number_of_win_rolls
        )
        max_number_of_win_rolls = max(
            game_stat.game_number_of_rolls_to_win, max_number_of_win_rolls
        )
        sum_number_of_win_rolls += game_stat.game_number_of_rolls_to_win

        min_distance_climbed = min(
            game_stat.game_total_distance_climbed, min_distance_climbed
        )
        max_distance_climbed = max(
            game_stat.game_total_distance_climbed, max_distance_climbed
        )
        sum_distance_climbed += game_stat.game_total_distance_climbed

        min_distance_slid = min(game_stat.game_total_distance_slid, min_distance_slid)
        max_distance_slid = max(game_stat.game_total_distance_slid, max_distance_slid)
        sum_distance_slid += game_stat.game_total_distance_slid

        biggest_climb = max(game_stat.game_max_distance_climbed, biggest_climb)
        biggest_slide = max(game_stat.game_max_distance_slide, biggest_slide)

        min_unlucky_rolls = min(game_stat.game_total_unlucky_rolls, min_unlucky_rolls)
        max_unlucky_rolls = max(game_stat.game_total_unlucky_rolls, max_unlucky_rolls)
        sum_unlucky_rolls += game_stat.game_total_unlucky_rolls

        min_lucky_rolls = min(game_stat.game_total_lucky_rolls, min_lucky_rolls)
        max_lucky_rolls = max(game_stat.game_total_lucky_rolls, max_lucky_rolls)
        sum_lucky_rolls += game_stat.game_total_lucky_rolls

        if sum(game_stat.game_max_streak) > sum(max_streak):
            max_streak = game_stat.game_max_streak

    avg_number_of_win_rolls = round(sum_number_of_win_rolls / number_of_simulations, 2)
    avg_distance_climbed = round(sum_distance_climbed / number_of_simulations, 2)
    avg_distance_slid = round(sum_distance_slid / number_of_simulations, 2)
    avg_unlucky_rolls = round(sum_unlucky_rolls / number_of_simulations, 2)
    avg_lucky_rolls = round(sum_lucky_rolls / number_of_simulations, 2)

    print()
    print(
        f"STATISTICS FOR {number_of_players} PLAYERS OVER {number_of_simulations} SIMULATION RUN(S)"
    )

    print("Winning rolls:")
    print(f"Minimum = {min_number_of_win_rolls}")
    print(f"Average = {avg_number_of_win_rolls}")
    print(f"Maximum = {max_number_of_win_rolls}")

    print()
    print("Distance climbed:")
    print(f"Minimum = {min_distance_climbed}")
    print(f"Average = {avg_distance_climbed}")
    print(f"Maximum = {max_distance_climbed}")

    print()
    print("Distance slid:")
    print(f"Minimum = {min_distance_slid}")
    print(f"Average = {avg_distance_slid}")
    print(f"Maximum = {max_distance_slid}")

    print()
    print("Unlucky rolls:")
    print(f"Minimum = {min_unlucky_rolls}")
    print(f"Average = {avg_unlucky_rolls}")
    print(f"Maximum = {max_unlucky_rolls}")

    print()
    print("Lucky rolls:")
    print(f"Minimum = {min_lucky_rolls}")
    print(f"Average = {avg_lucky_rolls}")
    print(f"Maximum = {max_lucky_rolls}")

    print()
    print(f"Biggest climb = {biggest_climb}")
    print(f"Biggest slide = {biggest_slide}")
    print(f"Longest streak: {max_streak}")

    print()
    return


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
        except Exception as exception:
            print(
                get_user_friendly_error_message(
                    "Snake", exception, top=head, bottom=tail
                )
            )
            print("Please fix the configuration and re-rerun")
            return False

    # Instantiate ladders as per the configuration
    for bottom, top in ladders_conf:
        try:
            ladders.append(Ladder(top=top, bottom=bottom))
        except Exception as exception:
            print(
                get_user_friendly_error_message(
                    "Ladder", exception, top=top, bottom=bottom
                )
            )
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

    for simulation_number in range(1, number_of_simulations + 1):
        print(f"Game simulation #{simulation_number} running...")
        game.play(simulation_number)
        game.reset_game_state()

    print_simultation_statistics(game.game_stats, number_of_players)

    return True


if __name__ == "__main__":
    main()
