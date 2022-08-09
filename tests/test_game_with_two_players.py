from src.constants import Constants as Const
from src.artefact import Snake, Ladder
from src.player import Player
from src.snake_ladder_simulation import Game
from .mock_die import Mock_Die


class Test_GameWithTwoPlayers:
    def test_two_player_winner_with_no_snake_no_ladder(self):
        winner: Player = None
        mock_rolls = [1, 5] * 20

        game = Game(Mock_Die(mock_rolls), number_of_simulations=1)
        player1: Player = Player("P1")
        player2: Player = Player("P2")
        game.add_players([player1, player2])

        _, winner = game.play(simulation_number=1)

        assert winner.name == "P2"
        assert player2.token_position == Const.BOARD_POSITION_MAX
        assert player2.number_of_rolls == 20

        assert player1.token_position == 20
        assert player1.number_of_rolls == 20

    def test_two_player_max_streak_with_no_snake_no_ladder(self):
        winner: Player = None
        mock_rolls = [6, 6, 6, 6, 6, 5]  # Player 1 streak ends here
        mock_rolls += [6, 6, 6, 6, 6, 4]  # Player 2 streak ends here
        mock_rolls += [1, 2] * 33  # Twice faster Player 2 will win

        game = Game(Mock_Die(mock_rolls), number_of_simulations=1)
        player1: Player = Player("P1")
        player2: Player = Player("P2")
        game.add_players([player1, player2])

        _, winner = game.play(simulation_number=1)

        assert winner.name == "P2"
        assert player2.token_position == Const.BOARD_POSITION_MAX
        assert player2.number_of_rolls == 39
        assert player2.max_streak == [6, 6, 6, 6, 6, 4]

        assert player1.token_position == 68
        assert player2.number_of_rolls == 39
        assert player1.max_streak == [6, 6, 6, 6, 6, 5]

        assert game.game_stats[0].game_number_of_rolls_to_win == 39
        assert game.game_stats[0].game_max_streak == [6, 6, 6, 6, 6, 5]
