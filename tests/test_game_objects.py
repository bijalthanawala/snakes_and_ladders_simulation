import pytest
from constants import Constants as Const
from game_exceptions import (
    EXCEPTION_OBJECT_INVALID_POSITION,
    EXCEPTION_OBJECT_SHORT,
    EXCEPTION_OBJECT_LONG,
    EXCEPTION_OBJECT_INVERSE,
)
from snake_ladder_simulation import GameObject, Snake, Ladder, Game


class Test_game_objects:
    @pytest.fixture
    def game(self):
        return Game()

    def test_gameobject_spans_board(self):
        with pytest.raises(Exception) as excinfo:
            _ = GameObject(
                activation_point=Const.BOARD_POSITION_MIN,
                termination_point=Const.BOARD_POSITION_MAX,
            )
        assert excinfo.type == EXCEPTION_OBJECT_LONG

    @pytest.mark.parametrize(
        "valid_length",
        [
            {"activation_point": 1, "termination_point": 99},  # Longest valid
            {"activation_point": 2, "termination_point": 100},  # Another longest valid
            {
                "activation_point": 60,
                "termination_point": 61,
            },  # Shortest valid that spans one row
            {
                "activation_point": 51,
                "termination_point": 61,
            },  # A long valid that spans exactly one row
        ],
    )
    def test_gameobject_valid_length(self, valid_length):
        try:
            _ = GameObject(**valid_length)
        except Exception as exception:
            assert False, f"GameObject instantiation failed: {exception}"

    @pytest.mark.parametrize(
        "invalid_short_length",
        [
            {"activation_point": 59, "termination_point": 60},  # Shortest invalid
            {
                "activation_point": 51,
                "termination_point": 60,
            },  # Longes invalid that fits a role
        ],
    )
    def test_gameobject_invalid_length(self, invalid_short_length):
        with pytest.raises(Exception) as excinfo:
            _ = GameObject(**invalid_short_length)
        assert excinfo.type == EXCEPTION_OBJECT_SHORT

    @pytest.mark.parametrize(
        "invalid_position",
        [
            {"activation_point": -1, "termination_point": 50},
            {"activation_point": 50, "termination_point": 101},
        ],
    )
    def test_gameobject_invalid_position(self, invalid_position):
        with pytest.raises(Exception) as excinfo:
            _ = GameObject(**invalid_position)
        assert excinfo.type == EXCEPTION_OBJECT_INVALID_POSITION

    def test_valid_snake(self):
        snake = Snake(mouth=50, tail=30)
        assert snake.activation_point == 50
        assert snake.termination_point == 30

    def test_valid_ladder(self):
        ladder = Ladder(bottom=30, top=50)
        assert ladder.activation_point == 30
        assert ladder.termination_point == 50

    def test_invalid_snake_inverse(self):
        with pytest.raises(Exception) as excinfo:
            _ = Snake(mouth=30, tail=50)
        assert excinfo.type == EXCEPTION_OBJECT_INVERSE

    def test_invalid_ladder_inverse(self):
        with pytest.raises(Exception) as excinfo:
            _ = Ladder(bottom=50, top=30)
        assert excinfo.type == EXCEPTION_OBJECT_INVERSE

    def test_add_game_objects(self, game):
        isSuccess, _ = game.add_game_objects(
            [
                Snake(mouth=50, tail=30),
            ]
        )
        assert isSuccess == True
        assert len(game.snakes) == 1
        assert len(game.ladders) == 0
        isSuccess, _ = game.add_game_objects(
            [
                Ladder(top=40, bottom=20),
            ]
        )
        assert isSuccess == True
        assert len(game.snakes) == 1
        assert len(game.ladders) == 1

    @pytest.mark.parametrize(
        "game_objects_with_same_activation_points",
        [
            [Snake(mouth=50, tail=30), Snake(mouth=50, tail=20)],
            [Ladder(top=50, bottom=30), Ladder(top=70, bottom=30)],
            [Snake(mouth=50, tail=30), Ladder(top=60, bottom=50)],
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
            [Snake(mouth=50, tail=30), Ladder(top=60, bottom=30)],
            [Snake(mouth=50, tail=30), Ladder(top=50, bottom=10)],
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
