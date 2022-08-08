import pytest
from src.constants import Constants as Const
from src.game_exceptions import (
    ERROR_MESSAGE_UNSUPPORTED_ARTEFACT,
    EXCEPTION_ARTEFACT_INVALID_POSITION,
    EXCEPTION_ARTEFACT_SHORT,
    EXCEPTION_ARTEFACT_LONG,
    EXCEPTION_ARTEFACT_INVERSE,
    EXCEPTION_SNAKE_AT_WINNING_POSITION,
    ERROR_MESSAGE_ACTIVATION_CLASH,
    ERROR_MESSAGE_ACTIVATION_DUPLICATED,
)
from src.artefact import Artefact, Snake, Ladder
from src.die import Die
from src.snake_ladder_simulation import Game


class Test_artefacts:
    @pytest.fixture
    def game(self):
        return Game(Die(), number_of_simulations=1)

    def test_valid_snake(self):
        snake = Snake(head=50, tail=30)
        assert snake.activation_point == 50
        assert snake.termination_point == 30

    def test_valid_ladder(self):
        ladder = Ladder(bottom=30, top=50)
        assert ladder.activation_point == 30
        assert ladder.termination_point == 50

    def test_invalid_snake_placed_at_winning_position(self):
        with pytest.raises(Exception) as excinfo:
            _ = Snake(head=Const.BOARD_POSITION_MAX, tail=50)
        assert excinfo.type == EXCEPTION_SNAKE_AT_WINNING_POSITION

    def test_invalid_snake_inverse(self):
        with pytest.raises(Exception) as excinfo:
            _ = Snake(head=30, tail=50)
        assert excinfo.type == EXCEPTION_ARTEFACT_INVERSE

    def test_invalid_ladder_inverse(self):
        with pytest.raises(Exception) as excinfo:
            _ = Ladder(bottom=50, top=30)
        assert excinfo.type == EXCEPTION_ARTEFACT_INVERSE

    def test_artefact_spans_board(self):
        with pytest.raises(Exception) as excinfo:
            _ = Artefact(
                activation_point=Const.BOARD_POSITION_MIN,
                termination_point=Const.BOARD_POSITION_MAX,
            )
        assert excinfo.type == EXCEPTION_ARTEFACT_LONG

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
    def test_artefact_valid_length(self, valid_length):
        try:
            _ = Artefact(**valid_length)
        except Exception as exception:
            assert False, f"Artefact instantiation failed: {exception}"

    @pytest.mark.parametrize(
        "invalid_short_length",
        [
            {"activation_point": 59, "termination_point": 60},  # Shortest invalid
            {
                "activation_point": 51,
                "termination_point": 60,
            },  # Longest invalid that fits a row
        ],
    )
    def test_artefact_invalid_length(self, invalid_short_length):
        with pytest.raises(Exception) as excinfo:
            _ = Artefact(**invalid_short_length)
        assert excinfo.type == EXCEPTION_ARTEFACT_SHORT

    @pytest.mark.parametrize(
        "invalid_position",
        [
            {"activation_point": -1, "termination_point": 50},
            {"activation_point": 50, "termination_point": 101},
        ],
    )
    def test_artefact_invalid_position(self, invalid_position):
        with pytest.raises(Exception) as excinfo:
            _ = Artefact(**invalid_position)
        assert excinfo.type == EXCEPTION_ARTEFACT_INVALID_POSITION

    def test_add_artefacts_valid(self, game):
        isSuccess, _ = game.add_artefacts(
            [
                Snake(head=50, tail=30),
            ]
        )
        assert isSuccess == True
        assert len(game.snakes) == 1
        assert len(game.ladders) == 0
        isSuccess, _ = game.add_artefacts(
            [
                Ladder(top=40, bottom=20),
            ]
        )
        assert isSuccess == True
        assert len(game.snakes) == 1
        assert len(game.ladders) == 1

    @pytest.mark.parametrize(
        "artefacts_with_same_activation_points",
        [
            [Snake(head=50, tail=30), Snake(head=50, tail=20)],
            [Ladder(top=50, bottom=30), Ladder(top=70, bottom=30)],
            [Snake(head=50, tail=30), Ladder(top=60, bottom=50)],
        ],
    )
    def test_add_artefacts_invalid_with_same_initiation_points(
        self, game: Game, artefacts_with_same_activation_points
    ):
        isSuccess, error_message = game.add_artefacts(
            artefacts_with_same_activation_points
        )
        assert isSuccess == False
        assert error_message == ERROR_MESSAGE_ACTIVATION_DUPLICATED

    @pytest.mark.parametrize(
        "artefacts_with_same_initiation_and_termination_points",
        [
            [Snake(head=50, tail=30), Ladder(top=60, bottom=30)],
            [Snake(head=50, tail=30), Ladder(top=50, bottom=10)],
        ],
    )
    def test_add_artefacts_invalid_snake_and_ladder_with_same_initiation_and_termination_points(
        self, game: Game, artefacts_with_same_initiation_and_termination_points
    ):
        isSuccess, error_message = game.add_artefacts(
            artefacts_with_same_initiation_and_termination_points
        )
        assert isSuccess == False
        assert error_message == ERROR_MESSAGE_ACTIVATION_CLASH

    def test_add_artefact_invalid_generic(self, game: Game):
        generic_artefact = Artefact(activation_point=1, termination_point=20)
        isSuccess, error_message = game.add_artefacts([generic_artefact])
        assert isSuccess == False
        assert error_message == ERROR_MESSAGE_UNSUPPORTED_ARTEFACT
