import pprint
from constants import Constants as Const
from game_exceptions import (
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
    def __init__(self, mouth, tail):
        super().__init__(activation_point=mouth, termination_point=tail)
        if mouth < tail:
            raise EXCEPTION_ARTEFACT_INVERSE
        if mouth == Const.BOARD_POSITION_MAX:
            raise EXCEPTION_SNAKE_AT_WINNING_POSITION
        self.mouth = mouth


class Ladder(Artefact):
    def __init__(self, top, bottom):
        super().__init__(activation_point=bottom, termination_point=top)
        if top < bottom:
            raise EXCEPTION_ARTEFACT_INVERSE
