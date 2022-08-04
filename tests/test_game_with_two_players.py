from constants import Constants as Const
from artefact import Snake, Ladder
from player import Player
from snake_ladder_simulation import Game
from .mock_die import Mock_Die


class Test_GameWithTwoPlayers:
    def test_two_player_winner_with_no_snake_no_ladder(self):
        mock_rolls = [1, 5] * 20

        game = Game(Mock_Die(mock_rolls), number_of_simulations=1)
        player1: Player = Player("P1")
        player2: Player = Player("P2")
        game.add_players([player1, player2])

        winner: Player = game.play(simulation_number=1)

        assert winner.name == "P2"
        assert player2.token_position == Const.BOARD_POSITION_MAX
        assert player2.number_of_rolls == 20
        assert player2.number_of_lucky_rolls == 0
        assert player2.number_of_unlucky_rolls == 0

        assert player1.token_position == 20
        assert player1.number_of_lucky_rolls == 0
        assert player1.number_of_unlucky_rolls == 0
