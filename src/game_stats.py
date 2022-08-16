import sys
from typing import List
import pprint


class GameStats:
    def __init__(self):
        self.init_game_stats()

    def init_game_stats(self):
        # rolls
        self.game_number_of_rolls_to_win: int = 0
        self.game_total_lucky_rolls: int = 0
        self.game_total_unlucky_rolls: int = 0

        # distance slid
        self.game_min_distance_slide: int = sys.maxsize
        self.game_max_distance_slide: int = 0
        self.game_total_distance_slid: int = 0
        self.biggest_slide_in_a_streak: int = 0

        # distance climbed
        self.game_min_distance_climbed: int = sys.maxsize
        self.game_max_distance_climbed: int = 0
        self.game_total_distance_climbed: int = 0
        self.biggest_climb_in_a_streak: int = 0

        # streak
        self.game_max_streak: List[int] = []

    def __repr__(self):  # pragma: no coverage
        return pprint.pformat(self.__dict__.copy())

    def __str__(self):  # pragma: no coverage
        return self.__repr__()
