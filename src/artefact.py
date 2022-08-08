import pprint
from .constants import Constants as Const
from .game_exceptions import (
    EXCEPTION_ARTEFACT_INVALID_POSITION,
    EXCEPTION_ARTEFACT_LONG,
    EXCEPTION_ARTEFACT_SHORT,
    EXCEPTION_ARTEFACT_INVERSE,
    EXCEPTION_SNAKE_AT_WINNING_POSITION,
)


class Artefact:
    def __init__(self, activation_point, termination_point):
        self._validate_artefact(activation_point, termination_point)
        self.activation_point = activation_point
        self.termination_point = termination_point
        self.distance = abs(self.activation_point - self.termination_point)

    def _validate_artefact(
        self, activation_point, termination_point
    ):  # TODO: Check if leading _ (undserscore) is a good convention
        if (
            activation_point < Const.BOARD_POSITION_MIN
            or activation_point > Const.BOARD_POSITION_MAX
            or termination_point < Const.BOARD_POSITION_MIN
            or termination_point > Const.BOARD_POSITION_MAX
        ):
            raise EXCEPTION_ARTEFACT_INVALID_POSITION

        if int((activation_point - 1) / Const.BOARD_ROW_SIZE) == int(
            (termination_point - 1) / Const.BOARD_ROW_SIZE
        ):
            raise EXCEPTION_ARTEFACT_SHORT

        if (
            activation_point == Const.BOARD_POSITION_MIN
            and termination_point == Const.BOARD_POSITION_MAX
        ):
            raise EXCEPTION_ARTEFACT_LONG

    def __str__(self):
        return pprint.pformat(self.__dict__.copy())


class Snake(Artefact):
    def __init__(self, head, tail):
        super().__init__(activation_point=head, termination_point=tail)
        if head < tail:
            raise EXCEPTION_ARTEFACT_INVERSE
        if head == Const.BOARD_POSITION_MAX:
            raise EXCEPTION_SNAKE_AT_WINNING_POSITION
        self.head = head

    def __repr__(self):
        return f"Snake: head={self.head} tail={self.termination_point}, length={self.distance}"

    def __str__(self):
        return self.__repr__()


class Ladder(Artefact):
    def __init__(self, top, bottom):
        super().__init__(activation_point=bottom, termination_point=top)
        if top < bottom:
            raise EXCEPTION_ARTEFACT_INVERSE

    def __repr__(self):
        return f"Ladder: top={self.termination_point} bottom={self.activation_point}, length={self.distance}"

    def __str__(self):
        return self.__repr__()
