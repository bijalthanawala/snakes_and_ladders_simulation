from random import randint

# SPECIAL CASES
#
# Bounce back:
# If a player rolls more than the last n required to win, will bounce back
# eg. a player on 97 (who needs 3 to win) rolls 5 will bounce back to 98 (100-2)

# Concious decision to not use type hint. My own opinion, would prefer to but not in this small exercise. Happy to adapt to team's adapter practices


class Player:
    def __init__(self, name):
        self.name = name
        self.curr_position = 0
        self.number_of_rolls = 0
        self.max_streak = []

    def __str__(self):
        # print(dir(self))
        print(self.__dict__)
        s = ""
        s += f"{self.number_of_rolls=}\n"
        s += f"{self.curr_position=}\n"
        return s


class Game:
    DIE_ROLL_MIN = 1
    DIE_ROLL_MAX = 6
    DIE_ROLL_REPEAT = DIE_ROLL_MAX
    POSITION_MIN = 0
    POSITION_MAX = 100

    def __init__(self):
        self.players = []
        self.curr_player_ndx = 0

    def add_player(self, player):
        player.curr_position = self.POSITION_MIN
        self.players.append(player)

    def play(self):
        if not self.players:
            print(f"There are no players. Quitting game.")
            return
        while not self.game_over():
            curr_player = self.players[self.curr_player_ndx]
            die_roll = self.roll_die()
            self.move_player(curr_player, die_roll)
            print(f"{curr_player.name} is at {curr_player.curr_position}")
            if die_roll != self.DIE_ROLL_REPEAT:
                self.curr_player_ndx = (self.curr_player_ndx + 1) % len(self.players)

    def roll_die(self):
        return randint(self.DIE_ROLL_MIN, self.DIE_ROLL_MAX)

    def game_over(self):
        return any(
            players.curr_position == self.POSITION_MAX for players in self.players
        )

    def move_player(self, player, die_roll):

        if player.curr_position + die_roll > self.POSITION_MAX:
            # bounce back
            die_roll = self.POSITION_MAX - (player.curr_position + die_roll)
            print(f"Bouncing back by {die_roll}")
        player.curr_position += die_roll


if __name__ == "__main__":
    print("Starting...")
    player1 = Player("Hulk")
    print(player1)
    game = Game()
    game.add_player(player1)
    game.play()
    print("Game finished")
