import pytest
from snake_ladder_simulation import GameObject, Snake, Ladder, Game


class Test_add_game_objects:
    @pytest.fixture
    def game(self):
        return Game()

    def test_valid_gameobject_longest(self):
        try:
            GameObject(activation_point=51, termination_point=61)
        except Exception as exception:
            assert False, f"GameObject instantiation failed: {exception}"

    def test_valid_gameobject_shortest(self):
        try:
            GameObject(activation_point=60, termination_point=61)
        except Exception as exception:
            assert False, f"GameObject instantiation failed: {exception}"

    def test_invalid_gameobject_longest(self):
        with pytest.raises(Exception) as excinfo:
            GameObject(activation_point=51, termination_point=59)
        assert GameObject.EXCEPTION_SHORT_OBJECT in str(excinfo.value)

    def test_invalid_gameobject_shortest(self):
        with pytest.raises(Exception) as excinfo:
            GameObject(activation_point=59, termination_point=60)
        assert GameObject.EXCEPTION_SHORT_OBJECT in str(excinfo.value)

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
            snake = Snake(mouth=30, tail=50)
        assert Snake.EXCEPTION_INVERSE_OBJECT in str(excinfo.value)

    def test_invalid_ladder_inverse(self):
        with pytest.raises(Exception) as excinfo:
            ladder = Ladder(bottom=50, top=30)
        assert Ladder.EXCEPTION_INVERSE_OBJECT in str(excinfo.value)

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
