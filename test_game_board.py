import pytest
from snake_ladder_simulation import GameObject, Snake, Ladder


def test_GameObject_short():
    with pytest.raises(Exception) as excinfo:
        gameobject = GameObject(high=50, low=45)
    assert GameObject.EXCEPTION_MIN_LENGTH in str(excinfo.value)


def test_GameObject_high_point_invalid():
    with pytest.raises(Exception) as excinfo:
        gameobject = GameObject(high=30, low=50)
    assert GameObject.EXCEPTION_HIGH_POINT_INVALID in str(excinfo.value)


def test_Snake_good():
    snake = Snake(high=50, low=30)
    assert snake.activation_point == 50
    assert snake.termination_point == 30


def test_Ladder_good():
    ladder = Ladder(high=50, low=30)
    assert ladder.activation_point == 30
    assert ladder.termination_point == 50
