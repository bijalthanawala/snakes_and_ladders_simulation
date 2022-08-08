from src.constants import Constants as Const
from src.player import Player
from src.snake_ladder_simulation import Game
from .mock_die import Mock_Die


class Test_Game:
    def test_game_play_no_player(self):
        game = Game(Mock_Die([5]), number_of_simulations=1)
        isSuccess, _ = game.play(1)
        assert isSuccess == False

    def test_game_play_invalid_simulation_number(self):
        game = Game(Mock_Die([5]), number_of_simulations=3)
        player1: Player = Player("P1")
        game.add_players([player1])
        isSuccess, _ = game.play(4)
        assert isSuccess == False

    def test_reset_game_state(self):
        game = Game(Mock_Die([5, 1]), number_of_simulations=1)
        player1: Player = Player("P1")
        player2: Player = Player("P2")
        game.add_players([player1, player2])

        game.play(simulation_number=1)

        assert player1.token_position == Const.BOARD_POSITION_MAX
        assert player1.number_of_rolls == 20
        assert player2.token_position == 19
        assert player2.number_of_rolls == 19
        assert game.curr_player_ndx == 1

        game.reset_game_state()

        assert player1.token_position == Const.PLAYER_START_POSITION
        assert player1.number_of_rolls == 0
        assert player2.token_position == Const.PLAYER_START_POSITION
        assert player2.number_of_rolls == 0
        assert game.curr_player_ndx == 0
