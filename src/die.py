from random import randint
from .constants import Constants as Const


class Die:
    @staticmethod
    def roll() -> int:
        return randint(Const.DIE_ROLL_MIN, Const.DIE_ROLL_MAX)
