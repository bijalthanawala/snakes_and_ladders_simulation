import pytest
from snake_ladder_simulation import GameObject, Snake, Ladder, Game


class Test_add_game_objects:
    def test_GameObject_short(self):
        with pytest.raises(Exception) as excinfo:
            gameobject = GameObject(high=50, low=45)
        assert GameObject.EXCEPTION_MIN_LENGTH in str(excinfo.value)

    def test_GameObject_high_point_invalid(self):
        with pytest.raises(Exception) as excinfo:
            gameobject = GameObject(high=30, low=50)
        assert GameObject.EXCEPTION_HIGH_POINT_INVALID in str(excinfo.value)

    def test_Snake_good(self):
        snake = Snake(high=50, low=30)
        assert snake.activation_point == 50
        assert snake.termination_point == 30

    def test_Ladder_good(self):
        ladder = Ladder(high=50, low=30)
        assert ladder.activation_point == 30
        assert ladder.termination_point == 50

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
