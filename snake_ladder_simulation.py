import sys
from typing import Union, List, Tuple, Dict, Set
import pprint

from constants import Constants as Const
from player import Player
from artefact import Artefact, Snake, Ladder
from die import Die
from game_stats import GameStats
from game_exceptions import get_user_friendly_error_message


class Game:

    ERROR_MESSAGE_ACTIVATION_DUPLICATED = (
        "Can not add a snake/ladder that shares head/bottom with another snake/ladder"
    )
    ERROR_MESSAGE_ACTIVATION_CLASH = (
        "Can not add a snake/ladder that starts where another ends"
    )
    ERROR_MESSAGE_UNSUPPORTED_ARTEFACT = (
        "Neither snake, nor ladder! Unsupported game object"
    )

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

    def add_artefacts(self, artefacts: List[Artefact]) -> Tuple[bool, str]:
        # Ensure: Snakes and the ladders to be placed on the board, do not start at the same position
        activation_points = [
            artefact.activation_point for artefact in artefacts
        ] + list(self.activation_points_map.keys())
        print(f"{activation_points=}")
        if len(activation_points) != len(set(activation_points)):
            return False, self.ERROR_MESSAGE_ACTIVATION_DUPLICATED

        # Ensure: Snakes and the ladders to be placed on the board, do not have start and end on the same position
        all_termination_points = [
            artefact.termination_point for artefact in artefacts
        ] + list(self.termination_points)
        overlaps = set(activation_points) & set(all_termination_points)
        print(f"{all_termination_points=}")
        print(f"{overlaps=}")
        if len(overlaps):
            return (False, self.ERROR_MESSAGE_ACTIVATION_CLASH)

        # Update internal records of activation, termination and lucky positions
        new_activation_points = {
            artefact.activation_point: artefact for artefact in artefacts
        }
        self.activation_points_map.update(new_activation_points)
        self.termination_points = set(all_termination_points)
        print(f"{self.termination_points=}")

        # record lucky positions 1 or 2 positions aways from snakes
        # TODO: Exclude positions that has another snake on it
        # TODO: Avoid re-iterating over artefacts
        for artefact in artefacts:
            if isinstance(artefact, Snake):
                if artefact.head + 1 <= Const.BOARD_POSITION_MAX:
                    self.lucky_positions.add(artefact.head + 1)
                    if artefact.head + 2 <= Const.BOARD_POSITION_MAX:
                        self.lucky_positions.add(artefact.head + 2)
                if artefact.head - 1 >= Const.BOARD_POSITION_MIN:
                    self.lucky_positions.add(artefact.head - 1)
                    if artefact.head - 2 >= Const.BOARD_POSITION_MIN:
                        self.lucky_positions.add(artefact.head - 2)
        print(f"{self.lucky_positions=}")

        # Finally add all the artefacts to the board
        for artefact in artefacts:
            if isinstance(artefact, Snake):
                self.snakes.append(artefact)
            elif isinstance(artefact, Ladder):
                self.ladders.append(artefact)
            else:
                return (
                    False,
                    self.ERROR_MESSAGE_UNSUPPORTED_ARTEFACT,
                )  # TODO: Test this

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
            game_stat.game_biggest_slid = max(
                player.max_distance_slid, game_stat.game_biggest_slid
            )
            game_stat.game_biggest_climb = max(
                player.max_distance_climbed, game_stat.game_biggest_climb
            )

    def spot_winner(self) -> Union[Player, None]:  # TODO: test
        player: Player
        for player in self.players:
            if player.token_position == Const.BOARD_POSITION_MAX:
                return player
        return None

    def move_token(self, player: Player, die_roll: int) -> int:  # TODO: test this
        if player.token_position + die_roll > Const.BOARD_POSITION_MAX:
            # Bounce back if we are overshooting the board
            die_roll = Const.BOARD_POSITION_MAX - (player.token_position + die_roll)
            print(f"{player.name} bouncing back by {die_roll}")

        if (
            player.token_position <= Const.BOARD_LAST_LUCKY_ZONE_BEGIN
            and player.token_position + die_roll == Const.BOARD_POSITION_MAX
        ):
            print(
                f"{player.name} rolled a last lucky roll {die_roll} while at {player.token_position}"
            )
            player.number_of_lucky_rolls += 1
        elif player.token_position + die_roll == Const.BOARD_POSITION_MAX:
            print(
                f"{player.name} rolled the last roll {die_roll} while at {player.token_position}"
            )

        player.token_position += die_roll

        # See if we missed a snake by 1 or 2 positions
        if player.token_position in self.lucky_positions:
            print(
                f"{player.name} avoided a snake by landing on a lucky position: {player.token_position}"
            )
            player.number_of_lucky_rolls += 1

        if player.token_position in self.activation_points_map:
            print(f"{player.name} is at {player.token_position} ({die_roll=})")
            artefact: Artefact = self.activation_points_map[player.token_position]
            player.token_position = artefact.termination_point
            if isinstance(artefact, Snake):
                player.number_of_unlucky_rolls += 1
                player.total_distance_slid += artefact.distance
                player.max_distance_slid = max(
                    artefact.distance, player.max_distance_slid
                )
                print(f"{player.name} slid to {player.token_position} due to Snake")
            elif isinstance(artefact, Ladder):
                player.number_of_lucky_rolls += 1
                player.total_distance_climbed += artefact.distance
                player.max_distance_climbed = max(
                    artefact.distance, player.max_distance_climbed
                )
                print(f"{player.name} climbed to {player.token_position} due to Ladder")
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
        print(f"Invalid line: {line}")

    return (
        isSuccess,
        number_of_simulations,
        number_of_players,
        snakes_conf,
        ladders_conf,
    )


def main() -> bool:
    players: List[Player] = []
    snakes: List[Artefact] = []
    ladders: List[Artefact] = []

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
    pprint.pprint(snakes)
    pprint.pprint(ladders)

    # Set up the game
    game = Game(Die(), number_of_simulations)
    game.add_players(players)
    isSuccess, err_message = game.add_artefacts(snakes + ladders)
    if not isSuccess:
        print(f"Error: {err_message}")
        print("Please fix the configuration and re-rerun")
        return False

    for simulation_number in range(1, number_of_simulations + 1):
        print(f"Game simulation #{simulation_number} starting...")
        winner = game.play(simulation_number)
        for player in game.players:
            print(player)
        print(f"Winner = {winner}")
        game.reset_game_state()
        print("Game finished")

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
    for game_stat in game.game_stats:
        print(f"{game_stat}")
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

        biggest_climb = max(game_stat.game_biggest_climb, biggest_climb)
        biggest_slide = max(game_stat.game_biggest_climb, biggest_slide)

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

    print(f"{min_number_of_win_rolls=}")
    print(f"{avg_number_of_win_rolls=}")
    print(f"{max_number_of_win_rolls=}")

    print(f"{min_distance_climbed=}")
    print(f"{avg_distance_climbed=}")
    print(f"{max_distance_climbed=}")

    print(f"{min_distance_slid=}")
    print(f"{avg_distance_slid=}")
    print(f"{max_distance_slid=}")

    print(f"{biggest_climb=}")
    print(f"{biggest_slide=}")

    print(f"{min_unlucky_rolls=}")
    print(f"{avg_unlucky_rolls=}")
    print(f"{max_unlucky_rolls=}")

    print(f"{min_lucky_rolls=}")
    print(f"{avg_lucky_rolls=}")
    print(f"{max_lucky_rolls=}")

    print(f"{max_streak=}")

    return True


if __name__ == "__main__":
    main()
