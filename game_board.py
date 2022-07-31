from typing import Union
from random import randint

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
    def __init__(self, name):
        self.name = name
        self.curr_position = 0
        self.number_of_rolls = 0
        self.max_streak = []

    def __str__(self):
        return str(self.__dict__)


class Game:
    DIE_ROLL_MIN = 1
    DIE_ROLL_MAX = 6
    DIE_ROLL_REPEAT = DIE_ROLL_MAX
    POSITION_MIN = 0
    POSITION_MAX = 100

    def __str__(self):
        printable_properties = self.__dict__
        printable_properties.pop("players")
        return str(printable_properties)

    def __init__(self):
        self.players = []
        self.curr_player_ndx = 0

        self.stat_number_of_rolls_to_win = 0
        self.stat_max_streak = []

    def add_player(self, player: Player) -> None:
        player.curr_position = self.POSITION_MIN
        self.players.append(player)

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
                print(
                    f"{curr_streak=} ,  {curr_player.name}'s {curr_player.max_streak=}"
                )
                if sum(curr_streak) > sum(
                    curr_player.max_streak
                ):  # TODO: How do we unit-test this logic?
                    curr_player.max_streak = curr_streak
                self.curr_player_ndx = (self.curr_player_ndx + 1) % len(self.players)
                curr_streak = []
            else:
                print(f"{curr_player.name} earns a repeat die roll")
        self.stat_number_of_rolls_to_win = winner.number_of_rolls
        self.record_stat_max_streak()
        return winner

    def record_stat_max_streak(self):
        for player in self.players:
            if sum(player.max_streak) > sum(self.stat_max_streak):
                self.stat_max_streak = player.max_streak

    def roll_die(self) -> int:
        return randint(self.DIE_ROLL_MIN, self.DIE_ROLL_MAX)

    def spot_winner(self) -> Union[Player, None]:
        for player in self.players:
            if player.curr_position == self.POSITION_MAX:
                return player
        return None

    def move_player(self, player, die_roll) -> int:
        if player.curr_position + die_roll > self.POSITION_MAX:
            # bounce back
            die_roll = self.POSITION_MAX - (player.curr_position + die_roll)
            print(f"{player.name} bouncing back by {die_roll}")
        player.curr_position += die_roll
        print(f"{player.name} is at {player.curr_position} after {die_roll} moves")
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
    game.add_player(player1)
    game.add_player(player2)
    game.add_player(player3)
    winner = game.play()
    print(f"Winner = {winner}")
    print(f"{game}")
    print("Game finished")


if __name__ == "__main__":
    main()
