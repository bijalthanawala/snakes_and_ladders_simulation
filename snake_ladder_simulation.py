from typing import Union, List, Tuple, Dict, Set
from constants import Constants as Const
from game_exceptions import (
    EXCEPTION_ARTEFACT_INVALID_POSITION,
    EXCEPTION_ARTEFACT_LONG,
    EXCEPTION_ARTEFACT_SHORT,
    EXCEPTION_ARTEFACT_INVERSE,
    EXCEPTION_SNAKE_AT_WINNING_POSITION,
)
from random import randint
import pprint

# TODO: Decide to type hint all the way or not. Comment accordingly


class Player:
    def __init__(self, name: str):
        self.name: str = name
        self.init_player_stats()

    def init_player_stats(self):
        self.curr_position: int = Const.PLAYER_START_POSITION
        self.number_of_rolls: int = 0
        self.number_of_lucky_rolls: int = 0
        self.number_of_unlucky_rolls: int = 0
        self.max_distance_slid: int = 0
        self.max_distance_climbed: int = 0
        self.total_distance_slid: int = 0
        self.total_distance_climbed: int = 0
        self.max_streak: List[int] = []

    def __str__(self):
        return pprint.pformat(self.__dict__.copy())


class Artefact:
    def __init__(self, activation_point, termination_point):
        self._validate_artefact(activation_point, termination_point)
        self.activation_point = activation_point
        self.termination_point = termination_point
        self.distance = abs(self.activation_point - self.termination_point)

    def _validate_artefact(
        self, activation_point, termination_point
    ):  # TODO: Check if leading _ (undserscore) is a good convention
        if (
            activation_point < Const.BOARD_POSITION_MIN
            or activation_point > Const.BOARD_POSITION_MAX
            or termination_point < Const.BOARD_POSITION_MIN
            or termination_point > Const.BOARD_POSITION_MAX
        ):
            raise EXCEPTION_ARTEFACT_INVALID_POSITION

        if int((activation_point - 1) / Const.BOARD_ROW_SIZE) == int(
            (termination_point - 1) / Const.BOARD_ROW_SIZE
        ):
            raise EXCEPTION_ARTEFACT_SHORT

        if (
            activation_point == Const.BOARD_POSITION_MIN
            and termination_point == Const.BOARD_POSITION_MAX
        ):
            raise EXCEPTION_ARTEFACT_LONG

    def __str__(self):
        return pprint.pformat(self.__dict__.copy())


class Snake(Artefact):
    def __init__(self, mouth, tail):
        super().__init__(activation_point=mouth, termination_point=tail)
        if mouth < tail:
            raise EXCEPTION_ARTEFACT_INVERSE
        if mouth == Const.BOARD_POSITION_MAX:
            raise EXCEPTION_SNAKE_AT_WINNING_POSITION
        self.mouth = mouth


class Ladder(Artefact):
    def __init__(self, top, bottom):
        super().__init__(activation_point=bottom, termination_point=top)
        if top < bottom:
            raise EXCEPTION_ARTEFACT_INVERSE


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

    def __init__(self):
        self.players: List[Player] = []
        self.snakes: List[Snake] = []
        self.ladders: List[Ladder] = []
        self.activation_points_map: Dict[int:Player] = dict()
        self.termination_points: List[int] = []
        self.lucky_positions: Set(int) = set()
        self.curr_player_ndx: int = 0
        self.stats: self.Stat = self.Stats()

    def reset_game_state(self) -> None:
        self.curr_player_ndx = 0
        self.stats.init_game_stats()

        player: Player
        for player in self.players:
            player.init_player_stats()

    def add_player(self, player: Player) -> None:
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

            die_roll = self.roll_die()
            self.move_player(curr_player, die_roll)

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

    def roll_die(self) -> int:
        return randint(Const.DIE_ROLL_MIN, Const.DIE_ROLL_MAX)

    def spot_winner(self) -> Union[Player, None]:  # TODO: test
        player: Player
        for player in self.players:
            if player.curr_position == Const.BOARD_POSITION_MAX:
                return player
        return None

    def move_player(self, player: Player, die_roll: int) -> int:  # TODO: test this
        # First handle the case if the player is near the end of the board
        if player.curr_position + die_roll > Const.BOARD_POSITION_MAX:
            # bounce back
            die_roll = Const.BOARD_POSITION_MAX - (player.curr_position + die_roll)
            print(f"{player.name} bouncing back by {die_roll}")

        if (
            player.curr_position <= Const.BOARD_LAST_LUCKY_ZONE_BEGIN
            and player.curr_position + die_roll == Const.BOARD_POSITION_MAX
        ):
            print(
                f"{player.name} rolled a last lucky roll {die_roll} while at {player.curr_position}"
            )
            player.number_of_lucky_rolls += 1
        elif player.curr_position + die_roll == Const.BOARD_POSITION_MAX:
            print(
                f"{player.name} rolled the last roll {die_roll} while at {player.curr_position}"
            )

        player.curr_position += die_roll

        # See if we missed a snake by 1 or 2 positions
        if player.curr_position in self.lucky_positions:
            print(
                f"{player.name} avoided a snake by landing on a lucky position: {player.curr_position}"
            )
            player.number_of_lucky_rolls += 1

        if player.curr_position in self.activation_points_map:
            print(f"{player.name} is at {player.curr_position} ({die_roll=})")
            artefact: Artefact = self.activation_points_map[player.curr_position]
            player.curr_position = artefact.termination_point
            if isinstance(artefact, Snake):
                player.number_of_unlucky_rolls += 1
                player.total_distance_slid += artefact.distance
                player.max_distance_slid = max(
                    artefact.distance, player.max_distance_slid
                )
                print(f"{player.name} moved to {player.curr_position} due to Snake")
            elif isinstance(artefact, Ladder):
                player.number_of_lucky_rolls += 1
                player.total_distance_climbed += artefact.distance
                player.max_distance_climbed = max(
                    artefact.distance, player.max_distance_climbed
                )
                print(f"{player.name} moved to {player.curr_position} due to Ladder")
        return die_roll


def main():
    print("Game starting...")
    game = Game()
    game.add_player(Player("P1"))
    game.add_player(Player("P2"))
    game.add_player(Player("P3"))
    snakes = [
        Snake(mouth=27, tail=5),
        Snake(mouth=15, tail=5),
        Snake(mouth=40, tail=3),
        Snake(mouth=43, tail=18),
        Snake(mouth=54, tail=31),
        Snake(mouth=66, tail=45),
        Snake(mouth=89, tail=53),
    ]  # TODO: Make this configurable
    ladders = [
        Ladder(top=25, bottom=4),
        Ladder(top=49, bottom=33),
        Ladder(top=63, bottom=42),
        Ladder(top=46, bottom=13),
        Ladder(top=69, bottom=50),
        Ladder(top=81, bottom=62),
        Ladder(top=92, bottom=74),
    ]  # TODO: Make this configurable
    isSuccess, err_message = game.add_artefacts(snakes + ladders)
    if not isSuccess:
        print(f"Error: {err_message}")
        return
    winner = game.play()
    for player in game.players:
        print(player)
    print(f"Winner = {winner}")
    print(f"{game.stats}")
    print("Game finished")


if __name__ == "__main__":
    main()
