from typing import Union, List, Tuple, Dict, Set
import pprint

from constants import Constants as Const
from player import Player
from artefact import Artefact, Snake, Ladder
from die import Die


class Game:

    ERROR_MESSAGE_ACTIVATION_DUPLICATED = (
        "Activation point duplicated with other artefacts"
    )
    ERROR_MESSAGE_ACTIVATION_CLASH = (
        "Some activation point sharing termination point with other artefacts"
    )
    ERROR_MESSAGE_UNSUPPORTED_ARTEFACT = "Unsupported artefact"

    class Stats:
        def __init__(self):
            self.init_game_stats()

        def init_game_stats(self):
            self.game_number_of_rolls_to_win: int = 0
            self.game_max_streak: List[int] = []
            self.game_total_lucky_rolls: int = 0
            self.game_total_unlucky_rolls: int = 0
            self.game_total_distance_slid: int = 0
            self.game_total_distance_climbed: int = 0
            self.game_biggest_slid: int = 0
            self.game_biggest_climb: int = 0

        def __str__(self):
            return pprint.pformat(self.__dict__.copy())

    def __init__(self, die: Die):
        self.players: List[Player] = []
        self.snakes: List[Snake] = []
        self.ladders: List[Ladder] = []
        self.die: Die = die
        self.activation_points_map: Dict[int, Artefact] = dict()
        self.termination_points: List[int] = []
        self.lucky_positions: Set[int] = set()
        self.curr_player_ndx: int = 0
        self.stats: "Game.Stats" = self.Stats()

    def reset_game_state(self) -> None:
        self.curr_player_ndx = 0
        self.stats.init_game_stats()

        player: Player
        for player in self.players:
            player.init_player_stats()

    def add_players(self, players: List[Player]) -> None:
        player: Player
        for player in players:
            self.players.append(player)

    def add_artefacts(self, artefacts: List[Artefact]) -> Tuple[bool, str]:
        artefact: Artefact  # Used in for loops

        for artefact in artefacts:
            print(artefact)

        # Ensure that the snakes and the ladders to be placed on the board,
        # do not start at the same position
        activation_points = [
            artefact.activation_point for artefact in artefacts
        ] + list(self.activation_points_map.keys())
        print(f"{activation_points=}")
        if len(activation_points) != len(set(activation_points)):
            return False, self.ERROR_MESSAGE_ACTIVATION_DUPLICATED

        # Ensure that the snakes and the ladders to be placed on the board,
        # do not have start and end on the same position
        # TODO: Avoid re-iterating over artefacts
        termination_points = [
            artefact.termination_point for artefact in artefacts
        ] + self.termination_points
        overlaps = set(activation_points) & set(termination_points)
        print(f"{termination_points=}")
        print(f"{overlaps=}")
        if len(overlaps):
            return (False, self.ERROR_MESSAGE_ACTIVATION_CLASH)

        # Update internal records of activation, termination and lucky positions
        new_activation_points = {
            artefact.activation_point: artefact for artefact in artefacts
        }
        self.activation_points_map.update(new_activation_points)
        self.termination_points = termination_points

        # record lucky positions 1 or 2 positions aways from snakes
        # TODO: Exclude positions that has another snake on it
        # TODO: Avoid re-iterating over artefacts
        for artefact in artefacts:
            if isinstance(artefact, Snake):
                if artefact.mouth + 1 <= Const.BOARD_POSITION_MAX:
                    self.lucky_positions.add(artefact.mouth + 1)
                    if artefact.mouth + 2 <= Const.BOARD_POSITION_MAX:
                        self.lucky_positions.add(artefact.mouth + 2)
                if artefact.mouth - 1 >= Const.BOARD_POSITION_MIN:
                    self.lucky_positions.add(artefact.mouth - 1)
                    if artefact.mouth - 2 >= Const.BOARD_POSITION_MIN:
                        self.lucky_positions.add(artefact.mouth - 2)
        print(f"{self.lucky_positions=}")

        # Finally add all artefacts to the board
        for artefact in artefacts:
            if isinstance(artefact, Snake):
                print("Adding snake")
                self.snakes.append(artefact)
            elif isinstance(artefact, Ladder):
                print("Adding ladder")
                self.ladders.append(artefact)
            else:
                return (
                    False,
                    self.ERROR_MESSAGE_UNSUPPORTED_ARTEFACT,
                )  # TODO: Test this

        return True, ""

    def play(self) -> Union[Player, None]:
        winner: Union[Player, None] = None
        curr_streak = []
        if not self.players:
            print(f"There are no players. Quitting game.")
            return None
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
                # print( f"{curr_streak=} ,  {curr_player.name}'s {curr_player.max_streak=}")
                if sum(curr_streak) > sum(
                    curr_player.max_streak
                ):  # TODO: How do we unit-test this logic?
                    curr_player.max_streak = curr_streak
                self.curr_player_ndx = (self.curr_player_ndx + 1) % len(self.players)
                curr_streak = []
            else:
                # print(f"{curr_player.name} earns a repeat die roll")
                pass

        self.record_game_stat(winner)
        return winner

    def record_game_stat(self, winner: Player):
        self.stats.game_number_of_rolls_to_win = winner.number_of_rolls
        player: Player
        for player in self.players:
            if sum(player.max_streak) > sum(self.stats.game_max_streak):
                self.stats.game_max_streak = player.max_streak
            self.stats.game_total_lucky_rolls += player.number_of_lucky_rolls
            self.stats.game_total_unlucky_rolls += player.number_of_unlucky_rolls
            self.stats.game_total_distance_slid += player.total_distance_slid
            self.stats.game_total_distance_climbed += player.total_distance_climbed
            self.stats.game_biggest_slid = max(
                player.max_distance_slid, self.stats.game_biggest_slid
            )
            self.stats.game_biggest_climb = max(
                player.max_distance_climbed, self.stats.game_biggest_climb
            )

    def spot_winner(self) -> Union[Player, None]:  # TODO: test
        player: Player
        for player in self.players:
            if player.token_position == Const.BOARD_POSITION_MAX:
                return player
        return None

    def move_token(self, player: Player, die_roll: int) -> int:  # TODO: test this
        # First handle the case if the player is near the end of the board
        if player.token_position + die_roll > Const.BOARD_POSITION_MAX:
            # bounce back
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
                print(f"{player.name} moved to {player.token_position} due to Snake")
            elif isinstance(artefact, Ladder):
                player.number_of_lucky_rolls += 1
                player.total_distance_climbed += artefact.distance
                player.max_distance_climbed = max(
                    artefact.distance, player.max_distance_climbed
                )
                print(f"{player.name} moved to {player.token_position} due to Ladder")
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
        line = line.strip()
        if len(line) == 0 or line[0] == "#":
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


def main():
    players: List[Player] = []
    snakes: List[Snake] = []
    ladders: List[Ladder] = []

    isSuccess: bool
    number_of_simulations: int
    number_of_players: int
    snakes_conf: List[List[int]]
    ladders_conf: List[List[int]]
    print("Reading game configuration...")
    (
        isSuccess,
        number_of_simulations,
        number_of_players,
        snakes_conf,
        ladders_conf,
    ) = read_conf_file()
    if not isSuccess:
        print("Error reading config file. Quitting")
        return

    for head, tail in snakes_conf:
        snakes.append(Snake(mouth=head, tail=tail))

    for top, bottom in ladders_conf:
        ladders.append(Ladder(top=top, bottom=bottom))

    for n in range(1, number_of_players + 1):
        players.append(Player(f"Player_{n}"))

    print("CONFIGURATION:")
    print(f"Number of simulations: {number_of_simulations}")
    print(f"Number of players: {number_of_players}")
    pprint.pprint(snakes)
    pprint.pprint(ladders)

    print("Game starting...")

    game = Game(Die())
    game.add_players(players)

    isSuccess, err_message = game.add_artefacts(snakes + ladders)
    if not isSuccess:
        print(f"Error: {err_message}")
        print("Quitting")
        return
    winner = game.play()
    for player in game.players:
        print(player)
    print(f"Winner = {winner}")
    print(f"{game.stats}")
    print("Game finished")


if __name__ == "__main__":
    main()
