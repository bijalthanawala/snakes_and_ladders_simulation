import sys
from typing import List
import pprint
from .constants import Constants as Const


class Player:
    def __init__(self, name: str):
        self.name: str = name
        self.init_player_stats()

    def init_player_stats(self):
        self.token_position: int = Const.PLAYER_START_POSITION

        # rolls
        self.number_of_rolls: int = 0
        self.number_of_lucky_rolls: int = 0
        self.number_of_unlucky_rolls: int = 0

        # distance slid
        self.min_distance_slid: int = sys.maxsize
        self.max_distance_slid: int = 0
        self.total_distance_slid: int = 0
        self.biggest_slide_in_a_streak: int = 0

        # distance climbed
        self.min_distance_climbed: int = sys.maxsize
        self.max_distance_climbed: int = 0
        self.total_distance_climbed: int = 0
        self.biggest_climb_in_a_streak: int = 0

        # streak
        self.max_streak: List[int] = []

    def __str__(self):  # pragma: no coverage
        return pprint.pformat(self.__dict__.copy())
