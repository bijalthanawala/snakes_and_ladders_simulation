from typing import List
import pprint
from .constants import Constants as Const


class Player:
    def __init__(self, name: str):
        self.name: str = name
        self.init_player_stats()

    def init_player_stats(self):
        self.token_position: int = Const.PLAYER_START_POSITION
        self.number_of_rolls: int = 0
        self.number_of_lucky_rolls: int = 0
        self.number_of_unlucky_rolls: int = 0
        self.max_distance_slid: int = 0
        self.max_distance_climbed: int = 0
        self.total_distance_slid: int = 0
        self.total_distance_climbed: int = 0
        self.max_streak: List[int] = []

    def __str__(self):
        return pprint.pformat(self.__dict__.copy())
