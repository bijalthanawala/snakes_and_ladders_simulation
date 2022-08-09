from typing import List, Tuple
from src.constants import Constants as Const
from src.artefact import Snake, Ladder
from src.player import Player
from src.snake_ladder_simulation import Game
from .mock_die import Mock_Die


class Test_GameWithOnePlayer:
    def prepare_test(
        self, die_rolls: List[int], number_of_simulations: int
    ) -> Tuple[Game, Player]:
        print(number_of_simulations)
        game = Game(Mock_Die(die_rolls), number_of_simulations)
        player1: Player = Player("P1")
        game.add_players([player1])
        return (game, player1)

    def test_one_player_finish_with_no_snake_no_ladder(self):
        repeat_roll = 5
        game, player1 = self.prepare_test([repeat_roll], number_of_simulations=1)

        game.play(simulation_number=1)

        assert player1.token_position == Const.BOARD_POSITION_MAX
        assert player1.number_of_rolls == Const.BOARD_POSITION_MAX / repeat_roll
        assert player1.total_distance_climbed == 0
        assert player1.total_distance_slid == 0
        assert player1.max_streak == [repeat_roll]

    def test_one_player_finish_with_one_ladder(self):
        repeat_roll = 5
        game, player1 = self.prepare_test([repeat_roll], number_of_simulations=1)
        ladder1: Ladder = Ladder(top=100, bottom=5)
        game.add_artefacts([ladder1])

        game.play(simulation_number=1)

        assert player1.token_position == Const.BOARD_POSITION_MAX
        assert player1.number_of_rolls == 1
        assert player1.total_distance_climbed == ladder1.distance
        assert player1.total_distance_slid == 0

    def test_one_player_finish_with_one_snake(self):
        mock_rolls = [5, 5, 5]  # Slid down the snake to position 1
        mock_rolls += [6, 3]  # On 10th position
        mock_rolls += [4, 6] * 9
        game, player1 = self.prepare_test(mock_rolls, number_of_simulations=1)
        snake1: Snake = Snake(head=15, tail=1)
        game.add_artefacts([snake1])

        game.play(simulation_number=1)

        assert player1.token_position == Const.BOARD_POSITION_MAX
        assert player1.number_of_rolls == len(mock_rolls)
        assert (
            player1.number_of_lucky_rolls == 1
        )  # Missed snake by 1 position, on position 16
        assert player1.number_of_unlucky_rolls == 1
        assert player1.total_distance_climbed == 0
        assert player1.total_distance_slid == snake1.distance
        assert player1.max_streak == [6, 4]

    def test_one_player_finish_with_two_ladders(self):
        mock_rolls = [5, 5]  # Go up the ladder - 15 to 50
        mock_rolls += [5, 5, 5]  # Go up the ladder - 65 to 100
        game, player1 = self.prepare_test(mock_rolls, number_of_simulations=1)
        ladder1: Ladder = Ladder(top=50, bottom=10)
        ladder2: Ladder = Ladder(top=100, bottom=65)
        game.add_artefacts([ladder1, ladder2])

        game.play(simulation_number=1)

        assert player1.token_position == Const.BOARD_POSITION_MAX
        assert player1.number_of_rolls == len(mock_rolls)
        assert player1.number_of_lucky_rolls == 2
        assert player1.number_of_unlucky_rolls == 0
        assert player1.total_distance_climbed == ladder1.distance + ladder2.distance
        assert player1.max_distance_climbed == max(ladder1.distance, ladder2.distance)
        assert player1.total_distance_slid == 0

    def test_one_player_finish_with_two_snakes(self):
        mock_rolls = [5, 5, 5]  # Slid down the snake from position 15 to 1
        mock_rolls += [6, 3]  # On 10th position
        mock_rolls += [6, 4] * 8  # Slid down the snake from position 90 to 80
        mock_rolls += [6, 6, 2, 6]
        game, player1 = self.prepare_test(mock_rolls, number_of_simulations=1)
        snake1: Snake = Snake(head=15, tail=1)
        snake2: Snake = Snake(head=90, tail=80)
        game.add_artefacts([snake1, snake2])

        game.play(simulation_number=1)

        assert player1.token_position == Const.BOARD_POSITION_MAX
        assert player1.number_of_rolls == len(mock_rolls)
        assert (
            player1.number_of_lucky_rolls == 2
        )  # Missed snake when landed on 16 and 92
        assert player1.number_of_unlucky_rolls == 2
        assert player1.total_distance_climbed == 0
        assert player1.total_distance_slid == snake1.distance + snake2.distance
        assert player1.max_distance_slid == max(snake1.distance, snake2.distance)
        assert player1.max_streak == [6, 6, 2]

    def test_one_player_max_streak(self):
        mock_rolls = [6, 4]
        mock_rolls += [6, 6, 4, 4]
        mock_rolls += [6, 6, 6, 4, 4, 4]
        mock_rolls += [6, 6, 6, 6, 4, 4, 4, 4]
        game, player1 = self.prepare_test(mock_rolls, number_of_simulations=1)

        game.play(simulation_number=1)

        assert player1.token_position == Const.BOARD_POSITION_MAX
        assert player1.number_of_rolls == len(mock_rolls)
        assert player1.max_streak == [6, 6, 6, 6, 4]

    def test_one_player_bounce_back(self):
        game, player1 = self.prepare_test([1], number_of_simulations=1)
        player1.token_position = Const.BOARD_POSITION_MAX - 2
        game.move_token(player1, 5)
        assert player1.token_position == Const.BOARD_POSITION_MAX - 5 + 2

    def test_one_player_last_lucky_zone(self):
        game, player1 = self.prepare_test([1], number_of_simulations=1)
        player1.token_position = Const.BOARD_LAST_LUCKY_ZONE_BEGIN + 1
        game.move_token(
            player1, Const.BOARD_POSITION_MAX - Const.BOARD_LAST_LUCKY_ZONE_BEGIN - 1
        )
        assert player1.token_position == Const.BOARD_POSITION_MAX
        assert player1.number_of_lucky_rolls == 1
