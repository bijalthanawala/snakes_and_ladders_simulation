from src.constants import Constants as Const
from src.die import Die
from src.player import Player
from src.snake_ladder_simulation import Game
from .mock_die import Mock_Die


class Test_Stats:
    def test_sim_stats(self):
        ROLLS_TO_WIN = 12
        UNLUCKY_ROLLS = 2
        LUCKY_ROLLS = 3
        DISTANCE_SLID = 4
        DISTANCE_CLIMBED = 5
        TOTAL_DISTANCE_SLID = 25
        TOTAL_DISTANCE_CLIMBED = 50
        MAX_STREAK = [6, 6, 6, 2]

        game = Game(Die(), number_of_simulations=3)

        # NOTE: The made up numbers do not make sense for a real game.
        #       The idea is to test stats calculation

        # Player 0 - rolls
        game.game_stats[0].game_number_of_rolls_to_win = ROLLS_TO_WIN
        game.game_stats[0].game_total_lucky_rolls = LUCKY_ROLLS
        game.game_stats[0].game_total_unlucky_rolls = UNLUCKY_ROLLS
        # Player 0 - distance slid
        game.game_stats[0].game_min_distance_slide = DISTANCE_SLID
        game.game_stats[0].game_max_distance_slide = DISTANCE_SLID
        game.game_stats[0].game_total_distance_slid = DISTANCE_SLID + 4
        game.game_stats[0].biggest_slide_in_a_streak = TOTAL_DISTANCE_SLID
        # Player 0 - distance climbed
        game.game_stats[0].game_min_distance_climbed = DISTANCE_CLIMBED
        game.game_stats[0].game_max_distance_climbed = DISTANCE_CLIMBED
        game.game_stats[0].game_total_distance_climbed = DISTANCE_CLIMBED + 4
        game.game_stats[0].biggest_climb_in_a_streak = TOTAL_DISTANCE_CLIMBED
        # Player 0 - max streak
        game.game_stats[0].game_max_streak = MAX_STREAK

        # Player 1 - rolls
        game.game_stats[1].game_number_of_rolls_to_win = ROLLS_TO_WIN * 10
        game.game_stats[1].game_total_lucky_rolls = LUCKY_ROLLS * 10
        game.game_stats[1].game_total_unlucky_rolls = UNLUCKY_ROLLS * 10
        # Player 1 - distance slid
        game.game_stats[1].game_min_distance_slide = DISTANCE_SLID * 10
        game.game_stats[1].game_max_distance_slide = DISTANCE_SLID * 10
        game.game_stats[1].game_total_distance_slid = DISTANCE_SLID + 2
        game.game_stats[1].biggest_slide_in_a_streak = TOTAL_DISTANCE_SLID + 1
        # Player 1 - distance climbed
        game.game_stats[1].game_min_distance_climbed = DISTANCE_CLIMBED * 10
        game.game_stats[1].game_max_distance_climbed = DISTANCE_CLIMBED * 10
        game.game_stats[1].game_total_distance_climbed = DISTANCE_CLIMBED + 2
        game.game_stats[1].biggest_climb_in_a_streak = TOTAL_DISTANCE_CLIMBED * 10
        # Player 1 - max streak
        MAX_STREAK.pop(0)
        game.game_stats[1].game_max_streak = MAX_STREAK

        # Player 2 - rolls
        game.game_stats[2].game_number_of_rolls_to_win = ROLLS_TO_WIN + 1
        game.game_stats[2].game_total_lucky_rolls = LUCKY_ROLLS + 2
        game.game_stats[2].game_total_unlucky_rolls = UNLUCKY_ROLLS + 3
        # Player 2 - distance slid
        game.game_stats[2].game_min_distance_slide = DISTANCE_SLID + 4
        game.game_stats[2].game_max_distance_slide = DISTANCE_SLID + 5
        game.game_stats[2].game_total_distance_slid = DISTANCE_SLID + 1
        game.game_stats[2].biggest_slide_in_a_streak = TOTAL_DISTANCE_SLID * 10
        # Player 2 - distance climbed
        game.game_stats[2].game_min_distance_climbed = DISTANCE_CLIMBED + 6
        game.game_stats[2].game_max_distance_climbed = DISTANCE_CLIMBED + 7
        game.game_stats[2].game_total_distance_climbed = DISTANCE_CLIMBED + 1
        game.game_stats[2].biggest_climb_in_a_streak = TOTAL_DISTANCE_CLIMBED + 1
        # Player 2 - max streak
        MAX_STREAK.pop(0)
        game.game_stats[2].game_max_streak = MAX_STREAK

        # Expected averages
        expected_avg_distance_slid = round(
            (
                game.game_stats[0].game_total_distance_slid
                + game.game_stats[1].game_total_distance_slid
                + game.game_stats[2].game_total_distance_slid
            )
            / 3,
            2,
        )
        expected_avg_distance_climbed = round(
            (
                game.game_stats[0].game_total_distance_climbed
                + game.game_stats[1].game_total_distance_climbed
                + game.game_stats[2].game_total_distance_climbed
            )
            / 3,
            2,
        )

        game.calculate_simultation_statistics()

        # Assert roll stats
        assert game.sim_stats.min_number_of_win_rolls == ROLLS_TO_WIN
        assert game.sim_stats.max_number_of_win_rolls == ROLLS_TO_WIN * 10
        assert game.sim_stats.min_unlucky_rolls == UNLUCKY_ROLLS
        assert game.sim_stats.max_unlucky_rolls == UNLUCKY_ROLLS * 10
        # Assert slide stats
        assert game.sim_stats.min_distance_slid == DISTANCE_SLID
        assert game.sim_stats.max_distance_slid == DISTANCE_SLID * 10
        assert game.sim_stats.biggest_slide_in_a_streak == TOTAL_DISTANCE_SLID * 10
        assert game.sim_stats.avg_distance_slid == expected_avg_distance_slid
        # Assert climb stats
        assert game.sim_stats.min_distance_climbed == DISTANCE_CLIMBED
        assert game.sim_stats.max_distance_climbed == DISTANCE_CLIMBED * 10
        assert game.sim_stats.biggest_climb_in_a_streak == TOTAL_DISTANCE_CLIMBED * 10
        assert game.sim_stats.avg_distance_climbed == expected_avg_distance_climbed
        # Assert max streak
        assert game.sim_stats.max_streak == MAX_STREAK
