from typing import Union, List, Tuple, Dict
from constants import Constants as Const
from game_exceptions import (
    EXCEPTION_OBJECT_INVALID_POSITION,
    EXCEPTION_OBJECT_LONG,
    EXCEPTION_OBJECT_SHORT,
    EXCEPTION_OBJECT_INVERSE,
)
from random import randint
import pprint

# SPECIAL CASES
#
# Bounce back:
# If a player rolls more than the last n required to win, will bounce back
# eg. a player on 97 (who needs 3 to win) rolls 5 will bounce back to 98 (100-2)

# NOTES
# Max length allowed for any snake or a ladder within the board boundaries is 99

# TODO: Decide to type hint all the way or not. Comment accordingly


class Player:
    def __init__(self, name: str):
        self.name: str = name
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


class GameObject:
    def __init__(self, activation_point, termination_point):
        self._validate_gameobject(activation_point, termination_point)
        self.activation_point = activation_point
        self.termination_point = termination_point
        self.distance = abs(self.activation_point - self.termination_point)

    def _validate_gameobject(self, activation_point, termination_point):
        if (
            activation_point < Const.BOARD_POSITION_MIN
            or activation_point > Const.BOARD_POSITION_MAX
            or termination_point < Const.BOARD_POSITION_MIN
            or termination_point > Const.BOARD_POSITION_MAX
        ):
            raise EXCEPTION_OBJECT_INVALID_POSITION

        if int((activation_point - 1) / Const.BOARD_ROW_SIZE) == int(
            (termination_point - 1) / Const.BOARD_ROW_SIZE
        ):
            raise EXCEPTION_OBJECT_SHORT

        if (
            activation_point == Const.BOARD_POSITION_MIN
            and termination_point == Const.BOARD_POSITION_MAX
        ):
            raise EXCEPTION_OBJECT_LONG

    def __str__(self):
        return pprint.pformat(self.__dict__.copy())


class Snake(GameObject):
    def __init__(self, mouth, tail):
        super().__init__(activation_point=mouth, termination_point=tail)
        if mouth < tail:
            raise EXCEPTION_OBJECT_INVERSE
        # self.luck_range_top = self.activation_point+2 if self.activation_point+2<=100 else 100
        # self.luck_range_end = self.activation_point-2 if self.activation_point-2>=1 else 1


class Ladder(GameObject):
    def __init__(self, top, bottom):
        super().__init__(activation_point=bottom, termination_point=top)
        if top < bottom:
            raise EXCEPTION_OBJECT_INVERSE


class Game:
    DIE_ROLL_MIN = 1
    DIE_ROLL_MAX = 6
    DIE_ROLL_REPEAT = DIE_ROLL_MAX

    ERROR_MESSAGE_ACTIVATION_DUPLICATED = (
        "Activation point duplicated with other objects"
    )
    ERROR_MESSAGE_ACTIVATION_CLASH = (
        "Some activation point sharing termination point with other objects"
    )

    class Stats:
        def __init__(self):
            self.game_number_of_rolls_to_win = 0
            self.game_max_streak: List[int] = []
            self.game_total_lucky_rolls = 0
            self.game_total_unlucky_rolls = 0
            self.game_total_distance_slid = 0
            self.game_total_distance_climbed = 0
            self.game_biggest_slid = 0
            self.game_biggest_climb = 0

        def __str__(self):
            return pprint.pformat(self.__dict__.copy())

    def __init__(self):
        self.players = []
        self.snakes = []
        self.ladders = []
        self.activation_points_map: Dict[int:Player] = dict()
        self.termination_points = []
        self.curr_player_ndx = 0
        self.stats = self.Stats()

    def reset_play_state(self) -> None:
        self.curr_player_ndx = 0

    def add_player(self, player: Player) -> None:
        self.players.append(player)

    def add_game_objects(self, game_objects: List[GameObject]) -> Tuple[bool, str]:

        for go in game_objects:
            print(go)

        # TODO: Ensure only the Snake or the Ladder (and the parent) objects are
        # added to the game

        # Ensure that the snakes and the ladders to be placed on the board,
        # do not start at the same position
        activation_points = [
            game_object.activation_point for game_object in game_objects
        ] + list(self.activation_points_map.keys())
        print(f"{activation_points=}")
        if len(activation_points) != len(set(activation_points)):
            return False, self.ERROR_MESSAGE_ACTIVATION_DUPLICATED

        # Ensure that the snakes and the ladders to be placed on the board,
        # do not have start and end on the same position
        termination_points = [
            game_object.termination_point for game_object in game_objects
        ] + self.termination_points
        overlaps = set(activation_points) & set(termination_points)
        print(f"{termination_points=}")
        print(f"{overlaps=}")
        if len(overlaps):
            return (False, self.ERROR_MESSAGE_ACTIVATION_CLASH)

        # Update internal records of activation and termination points
        new_activation_points = {
            game_object.activation_point: game_object for game_object in game_objects
        }
        self.activation_points_map.update(new_activation_points)
        self.termination_points = termination_points

        # Finally add all objects to the board
        for game_object in game_objects:
            if isinstance(game_object, Snake):
                print("Adding snake")
                self.snakes.append(game_object)
            if isinstance(game_object, Ladder):
                print("Adding ladder")
                self.ladders.append(game_object)

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
            if die_roll != self.DIE_ROLL_REPEAT:
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
        return randint(self.DIE_ROLL_MIN, self.DIE_ROLL_MAX)

    def spot_winner(self) -> Union[Player, None]:  # TODO: test
        for player in self.players:
            if player.curr_position == Const.BOARD_POSITION_MAX:
                return player
        return None

    def move_player(self, player, die_roll) -> int:  # TODO: test
        if player.curr_position + die_roll > Const.BOARD_POSITION_MAX:
            # bounce back
            die_roll = Const.BOARD_POSITION_MAX - (player.curr_position + die_roll)
            print(f"{player.name} bouncing back by {die_roll}")
        player.curr_position += die_roll
        # print(f"{player.name} is at {player.curr_position} after {die_roll} moves")
        if player.curr_position in self.activation_points_map:
            print(f"{player.name} is at {player.curr_position} after {die_roll} moves")
            game_object: GameObject = self.activation_points_map[player.curr_position]
            player.curr_position = game_object.termination_point
            if isinstance(game_object, Snake):
                player.number_of_unlucky_rolls += 1
                player.total_distance_slid += game_object.distance
                player.max_distance_slid = max(
                    game_object.distance, player.max_distance_slid
                )
                print(f"{player.name} moved to {player.curr_position} due to Snake")
            elif isinstance(game_object, Ladder):
                player.number_of_lucky_rolls += 1
                player.total_distance_climbed += game_object.distance
                player.max_distance_climbed = max(
                    game_object.distance, player.max_distance_climbed
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
    isSuccess, err_message = game.add_game_objects(snakes + ladders)
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
