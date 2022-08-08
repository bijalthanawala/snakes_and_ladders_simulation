import sys
from typing import List
import pprint


class SimulationStats:
    def __init__(self):
        self.init_simulation_stats()

    def init_simulation_stats(self):
        self.number_of_simulations: int = 0
        self.min_number_of_win_rolls: int = sys.maxsize
        self.avg_number_of_win_rolls: float = 0.0
        self.max_number_of_win_rolls: int = 0
        self.min_distance_climbed = sys.maxsize
        self.avg_distance_climbed: float = 0.0
        self.max_distance_climbed: int = 0
        self.min_distance_slid = sys.maxsize
        self.avg_distance_slid: float = 0.0
        self.max_distance_slid: int = 0
        self.biggest_climb: int = 0
        self.biggest_slide: int = 0
        self.min_unlucky_rolls: int = sys.maxsize
        self.avg_unlucky_rolls: float = 0.0
        self.max_unlucky_rolls: int = 0
        self.min_lucky_rolls: int = sys.maxsize
        self.avg_lucky_rolls: float = 0.0
        self.max_lucky_rolls: int = 0
        self.max_streak: List[int] = [0]
