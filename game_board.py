from typing import Union, List, Tuple, Dict
from random import randint

# ASSUMPTION
# Start Position
# It appears typo in the spec, the start position is mistakenly mentioned to be 0
# Looking at the board diagram it should have been 1

#
# The longest turn
# The longest turn is recorded such that it could be of any of the players, not necessarily the winner
#

# SPECIAL CASES
#
# Bounce back:
# If a player rolls more than the last n required to win, will bounce back
# eg. a player on 97 (who needs 3 to win) rolls 5 will bounce back to 98 (100-2)

# TODO: Decide to type hint all the way or not. Comment accordingly
# Concious decision to not use type hint. My own opinion, would prefer to but not in this small exercise. Happy to adapt to team's adapter practices


class Player:
    def __init__(self, name: str):
        self.name: str = name
        self.curr_position: int = 0
        self.number_of_rolls: int = 0
        self.number_of_lucky_rolls: int = 0
        self.number_of_unlucky_rolls: int = 0
        self.max_distance_slid: int = 0
        self.max_distance_climbed: int = 0
        self.total_distance_slid: int = 0
        self.total_distance_climbed: int = 0
        self.max_streak: List[int] = []

    def __str__(self):
        return str(self.__dict__)


class GameObject:
    MIN_LENGTH = 10

    def __init__(self, high, low):
        self.activation_point = 0  # To be determined by the child class
        self.end_point = 0  # To be determined by child class
        if high < low:
            raise Exception(f"High point must be larger than the low")
        if abs(low - high) < self.MIN_LENGTH:
            raise Exception(f"Object length must be minimum {self.MIN_LENGTH}")
        self.distance = high - low


class Snake(GameObject):
    def __init__(self, high, low):
        super().__init__(high, low)
        self.activation_point = high
        self.end_point = low

    def __str__(self):
        return str(self.__dict__)


class Ladder(GameObject):
    def __init__(self, high, low):
        super().__init__(high, low)
        self.activation_point = low
        self.end_point = high

    def __str__(self):
        return str(self.__dict__)


class Game:
    DIE_ROLL_MIN = 1
    DIE_ROLL_MAX = 6
    DIE_ROLL_REPEAT = DIE_ROLL_MAX
    POSITION_MIN = 1
    POSITION_MAX = 100

    def __str__(self):
        printable_properties = self.__dict__.copy()
        printable_properties["number_of_snakes"] = len(self.snakes)
        printable_properties["number_of_ladders"] = len(self.ladders)
        printable_properties.pop("snakes")
        printable_properties.pop("ladders")
        printable_properties.pop("players")
        printable_properties.pop("activation_points_map")
        printable_properties.pop("end_points")
        return str(printable_properties)

    def __init__(self):
        self.players = []
        self.snakes = []
        self.ladders = []
        self.activation_points_map: Dict[int:Player] = dict()
        self.end_points = []
        self.reset_play_state()

    def reset_play_state(self) -> None:
        self.curr_player_ndx = 0
        self.stat_number_of_rolls_to_win = 0
        self.stat_max_streak: List[int] = []
        self.game_total_lucky_rolls = 0
        self.game_total_unlucky_rolls = 0
        self.game_total_distance_slid = 0
        self.game_total_distance_climbed = 0
        self.game_biggest_slid = 0
        self.game_biggest_climb = 0

    def add_player(self, player: Player) -> None:
        player.curr_position = self.POSITION_MIN
        self.players.append(player)

    def add_game_object(self, game_object: GameObject) -> None:
        if isinstance(game_object, Snake):
            print("Adding snake")
            self.snakes.append(game_object)
        if isinstance(game_object, Ladder):
            print("Adding ladder")
            self.ladders.append(game_object)

    def add_game_objects(self, game_objects: List[GameObject]) -> Tuple[bool, str]:

        for go in game_objects:
            print(go)

        # Ensure that snakes and ladders, do not start at the same position
        activation_points = [
            game_object.activation_point for game_object in game_objects
        ] + list(self.activation_points_map.keys())
        print(f"{activation_points=}")
        if len(activation_points) != len(set(activation_points)):
            return False, "Activation point clashing with other objects"

        # Ensure that snakes and ladders, do not have start and end on the same position
        end_points = [
            game_object.end_point for game_object in game_objects
        ] + self.end_points
        overlaps = set(activation_points) & set(end_points)
        print(f"{end_points=}")
        print(f"{overlaps=}")
        if len(overlaps):
            return False, "Some activation point sharing end_point with other objects"

        new_activation_points = {
            game_object.activation_point: game_object for game_object in game_objects
        }
        self.activation_points_map.update(new_activation_points)
        self.end_points = end_points
        for game_object in game_objects:
            self.add_game_object(game_object)

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

        self.stat_number_of_rolls_to_win = winner.number_of_rolls
        self.record_game_stat()
        return winner

    def record_game_stat(self):
        for player in self.players:
            if sum(player.max_streak) > sum(self.stat_max_streak):
                self.stat_max_streak = player.max_streak
            self.game_total_lucky_rolls += player.number_of_lucky_rolls
            self.game_total_unlucky_rolls += player.number_of_unlucky_rolls
            self.game_total_distance_slid += player.total_distance_slid
            self.game_total_distance_climbed += player.total_distance_climbed
            self.game_biggest_slid = max(
                player.max_distance_slid, self.game_biggest_slid
            )
            self.game_biggest_climb = max(
                player.max_distance_climbed, self.game_biggest_climb
            )

    def roll_die(self) -> int:
        return randint(self.DIE_ROLL_MIN, self.DIE_ROLL_MAX)

    def spot_winner(self) -> Union[Player, None]:  # TODO: test
        for player in self.players:
            if player.curr_position == self.POSITION_MAX:
                return player
        return None

    def move_player(self, player, die_roll) -> int:  # TODO: test
        if player.curr_position + die_roll > self.POSITION_MAX:
            # bounce back
            die_roll = self.POSITION_MAX - (player.curr_position + die_roll)
            print(f"{player.name} bouncing back by {die_roll}")
        player.curr_position += die_roll
        # print(f"{player.name} is at {player.curr_position} after {die_roll} moves")
        if player.curr_position in self.activation_points_map:
            print(f"{player.name} is at {player.curr_position} after {die_roll} moves")
            game_object: GameObject = self.activation_points_map[player.curr_position]
            player.curr_position = game_object.end_point
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
    print("Starting...")
    player1 = Player("P1")
    print(player1)
    player2 = Player("P2")
    print(player2)
    player3 = Player("P3")
    print(player3)
    game = Game()
    # print(f"{game}")
    snakes = [
        Snake(high=27, low=5),
        Snake(high=15, low=5),
        Snake(high=40, low=3),
        Snake(high=43, low=18),
        Snake(high=54, low=31),
        Snake(high=66, low=45),
        Snake(high=89, low=53),
    ]  # TODO: Make this configurable
    ladders = [
        Ladder(high=25, low=4),
        Ladder(high=49, low=33),
        Ladder(high=63, low=42),
        Ladder(high=46, low=13),
        Ladder(high=69, low=50),
        Ladder(high=81, low=62),
        Ladder(high=92, low=74),
    ]  # TODO: Make this configurable
    isSuccess, err_message = game.add_game_objects(snakes + ladders)
    print(f"{isSuccess=} {err_message=}")
    print(f"{game}")
    new_snakes = [
        Snake(high=30, low=5),
        Snake(high=20, low=5),
    ]  # TODO: Make this configurable
    new_ladders = [
        Ladder(high=40, low=24),
        Ladder(high=34, low=3),
    ]  # TODO: Make this configurable
    isSuccess, err_message = game.add_game_objects(new_snakes + new_ladders)
    print(f"{isSuccess=} {err_message=}")
    print(f"{game}")
    game.add_player(player1)
    game.add_player(player2)
    game.add_player(player3)
    winner = game.play()
    print(f"Winner = {winner}")
    print(f"{game}")
    print("Game finished")


if __name__ == "__main__":
    main()
