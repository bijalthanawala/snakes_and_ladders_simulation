import pytest
from game_board import GameObject, Snake, Ladder, Game


class Test_add_game_objects:
    @pytest.fixture
    def game(self):
        return Game()

    def test_add_game_objects(self, game):
        isSuccess, _ = game.add_game_objects(
            [
                Snake(high=50, low=30),
            ]
        )
        assert isSuccess == True
        assert len(game.snakes) == 1
        assert len(game.ladders) == 0
        isSuccess, _ = game.add_game_objects(
            [
                Ladder(high=40, low=20),
            ]
        )
        assert isSuccess == True
        assert len(game.snakes) == 1
        assert len(game.ladders) == 1

    @pytest.mark.parametrize(
        "game_objects_with_same_activation_points",
        [
            [Snake(high=50, low=30), Snake(high=50, low=20)],
            [Ladder(high=50, low=30), Ladder(high=70, low=30)],
            [Snake(high=50, low=30), Ladder(high=60, low=50)],
        ],
    )
    def test_add_game_objects_with_same_initiation_points(
        self, game: Game, game_objects_with_same_activation_points
    ):
        isSuccess, error_message = game.add_game_objects(
            game_objects_with_same_activation_points
        )
        assert isSuccess == False
        assert error_message == game.ERROR_MESSAGE_ACTIVATION_DUPLICATED

    @pytest.mark.parametrize(
        "game_objects_with_same_initiation_and_termination_points",
        [
            [Snake(high=50, low=30), Ladder(high=60, low=30)],
            [Snake(high=50, low=30), Ladder(high=50, low=10)],
        ],
    )
    def test_add_game_objects_snake_and_ladder_with_same_initiation_and_termination_points(
        self, game: Game, game_objects_with_same_initiation_and_termination_points
    ):
        isSuccess, error_message = game.add_game_objects(
            game_objects_with_same_initiation_and_termination_points
        )
        assert isSuccess == False
        assert error_message == game.ERROR_MESSAGE_ACTIVATION_CLASH
