import sys
from typing import Union, List, Tuple, Dict, Set
import argparse
import logging

from .constants import Constants as Const
from .player import Player
from .artefact import Artefact, Snake, Ladder
from .die import Die
from .simulation_stats import SimulationStats
from .game_stats import GameStats
from .game_exceptions import (
    ERROR_MESSAGE_ACTIVATION_CLASH,
    ERROR_MESSAGE_ACTIVATION_DUPLICATED,
    ERROR_MESSAGE_UNSUPPORTED_ARTEFACT,
)


class Game:
    def __init__(self, die: Die, number_of_simulations: int):
        self.number_of_simulations = number_of_simulations
        self.players: List[Player] = []
        self.snakes: List[Snake] = []
        self.ladders: List[Ladder] = []
        self.die: Die = die
        self.activation_points_map: Dict[int, Artefact] = dict()
        self.termination_points: Set[int] = set()
        self.lucky_positions: Set[int] = set()
        self.curr_player_ndx: int = 0
        self.game_stats: List[GameStats] = []
        self.sim_stats: SimulationStats = SimulationStats()

        for n in range(number_of_simulations):
            self.game_stats.append(GameStats())

    def reset_game_state(self) -> None:
        self.curr_player_ndx = 0

        for player in self.players:
            player.init_player_stats()

    def add_players(self, players: List[Player]) -> None:
        player: Player
        for player in players:
            self.players.append(player)

    def update_lucky_positions(self, snake: Snake, heads_of_snakes_on_board: List[int]):
        # This method records lucky positions (1 or 2 positions aways from snakes)
        lucky_positions_after_snake = [snake.head + 1, snake.head + 2]
        lucky_positions_before_snake = [snake.head - 1, snake.head - 2]

        for after in lucky_positions_after_snake:
            if (
                after not in heads_of_snakes_on_board
                and after <= Const.BOARD_POSITION_MAX
            ):
                self.lucky_positions.add(after)
        for before in lucky_positions_before_snake:
            if (
                before not in heads_of_snakes_on_board
                and before >= Const.BOARD_POSITION_MIN
            ):
                self.lucky_positions.add(before)

    def add_artefacts(self, artefacts: List[Artefact]) -> Tuple[bool, str]:
        # Ensure that the snakes and the ladders do not start at the same position
        # (take into consideration snakes and ladders in this list, and alse those
        # already placed on the board)
        all_activation_points = [
            artefact.activation_point for artefact in artefacts
        ] + list(self.activation_points_map.keys())
        all_activation_points_unique = set(all_activation_points)
        logging.debug(f"add_artefact: {all_activation_points=}")
        logging.debug(f"add_artefact: {all_activation_points_unique=}")
        if len(all_activation_points) != len(all_activation_points_unique):
            return False, ERROR_MESSAGE_ACTIVATION_DUPLICATED

        # Ensure that the snakes and the ladders do not have the start and the end
        # on the same position
        # (take into consideration snakes and ladders in this list, and alse those
        # already placed on the board)
        all_termination_points = [
            artefact.termination_point for artefact in artefacts
        ] + list(self.termination_points)
        all_termination_points_unique = set(all_termination_points)
        logging.debug(f"add_artefacts: {all_termination_points=}")
        logging.debug(f"add_artefacts: {all_termination_points_unique=}")
        overlaps = all_activation_points_unique & all_termination_points_unique
        logging.debug(
            f"add_artefacts: Overlap between all (old and new) activation and termination points = {overlaps}"
        )
        if len(overlaps):
            return (False, ERROR_MESSAGE_ACTIVATION_CLASH)

        # Update internal records of activation, termination
        new_activation_points_map = {
            artefact.activation_point: artefact for artefact in artefacts
        }
        self.activation_points_map.update(new_activation_points_map)
        self.termination_points = all_termination_points_unique
        logging.debug(f"add_artefacts: Updated {self.activation_points_map=}")
        logging.debug(f"add_artefacts: Updated {self.termination_points=}")

        # Finally add all the artefacts to the board
        heads_of_snakes_on_board = [
            x[0] for x in self.activation_points_map.items() if isinstance(x[1], Snake)
        ]
        for artefact in artefacts:
            if isinstance(artefact, Snake):
                self.update_lucky_positions(artefact, heads_of_snakes_on_board)
                self.snakes.append(artefact)
            elif isinstance(artefact, Ladder):
                self.ladders.append(artefact)
            else:
                return (
                    False,
                    ERROR_MESSAGE_UNSUPPORTED_ARTEFACT,
                )

        logging.debug(f"add_artefacts: {len(self.lucky_positions)=}")
        logging.debug(f"add_artefacts: {self.lucky_positions=}")

        return True, ""

    def play(self, simulation_number) -> Tuple[bool, Union[Player, None]]:
        winner: Union[Player, None] = None
        curr_streak = []

        # Do not proceed, if no players are added
        if len(self.players) == 0:
            return (False, None)

        # simulation_number is expected to be 1-based
        if simulation_number < 1 or simulation_number > self.number_of_simulations:
            print(
                f"Invalid simulation number ({simulation_number}). Expected number between 1 and {self.number_of_simulations}"
            )
            return (False, None)

        simulation_number_offset = simulation_number - 1

        while True:
            winner = self.spot_winner()
            if winner:
                break

            curr_player: Player = self.players[self.curr_player_ndx]

            die_roll = self.die.roll()
            self.move_token(curr_player, die_roll)

            curr_player.number_of_rolls += 1
            curr_streak.append(die_roll)
            if die_roll != Const.DIE_ROLL_REPEAT:
                if sum(curr_streak) > sum(curr_player.max_streak):
                    curr_player.max_streak = curr_streak
                self.curr_player_ndx = (self.curr_player_ndx + 1) % len(self.players)
                curr_streak = []

        self.record_game_stat(winner, simulation_number_offset)
        return (True, winner)

    def record_game_stat(self, winner: Player, simulation_number_offset):
        # TODO: Write test for game_stat calculations
        game_stat = self.game_stats[simulation_number_offset]
        game_stat.game_number_of_rolls_to_win = winner.number_of_rolls
        player: Player
        for player in self.players:
            if sum(player.max_streak) > sum(game_stat.game_max_streak):
                game_stat.game_max_streak = player.max_streak
            game_stat.game_total_lucky_rolls += player.number_of_lucky_rolls
            game_stat.game_total_unlucky_rolls += player.number_of_unlucky_rolls
            game_stat.game_total_distance_slid += player.total_distance_slid
            game_stat.game_total_distance_climbed += player.total_distance_climbed
            game_stat.game_max_distance_slide = max(
                player.max_distance_slid, game_stat.game_max_distance_slide
            )
            game_stat.game_max_distance_climbed = max(
                player.max_distance_climbed, game_stat.game_max_distance_climbed
            )

    def spot_winner(self) -> Union[Player, None]:  # TODO: Write test for this
        player: Player
        for player in self.players:
            if player.token_position == Const.BOARD_POSITION_MAX:
                return player
        return None

    def move_token(self, player: Player, die_roll: int) -> int:
        """
        This method moves the token on the board and also maintains
        player's own state and stats
        """
        logging.debug(f"Moving {player.name} by {die_roll}")
        if player.token_position + die_roll > Const.BOARD_POSITION_MAX:
            # Bounce back if we are overshooting the board
            die_roll = Const.BOARD_POSITION_MAX - (player.token_position + die_roll)
            logging.info(f"{player.name} bouncing back by {die_roll}")

        # Check if this the last lucky roll from the lucky zone
        if (
            player.token_position <= Const.BOARD_LAST_LUCKY_ZONE_BEGIN
            and player.token_position + die_roll == Const.BOARD_POSITION_MAX
        ):
            # TODO: Write a test for this
            logging.info(
                f"{player.name} rolled a last lucky roll {die_roll} while at {player.token_position}"
            )
            player.number_of_lucky_rolls += 1

        player.token_position += die_roll

        # Check if the player missed a snake by 1 or 2 positions
        if player.token_position in self.lucky_positions:
            # TODO: Write a test for this
            logging.info(
                f"{player.name} avoided a snake by landing on a lucky position: {player.token_position}"
            )
            player.number_of_lucky_rolls += 1

        # Act if we have arrived at the head of snake, or start of a ladder
        if player.token_position in self.activation_points_map:
            artefact: Artefact = self.activation_points_map[player.token_position]
            player.token_position = artefact.termination_point
            if isinstance(artefact, Snake):
                player.number_of_unlucky_rolls += 1
                player.total_distance_slid += artefact.distance
                player.max_distance_slid = max(
                    artefact.distance, player.max_distance_slid
                )
                logging.info(
                    f"{player.name} encountered snake and slid {artefact.distance} units from {artefact.activation_point} to {artefact.termination_point}"
                )
            elif isinstance(artefact, Ladder):
                player.number_of_lucky_rolls += 1
                player.total_distance_climbed += artefact.distance
                player.max_distance_climbed = max(
                    artefact.distance, player.max_distance_climbed
                )
                logging.info(
                    f"{player.name} encountered ladder and climbed {artefact.distance} units from {artefact.activation_point} to {artefact.termination_point}"
                )
        return die_roll

    def run_simulations(self, print_progress=False):
        for simulation_number in range(1, self.number_of_simulations + 1):
            if print_progress:
                print(f"Game simulation #{simulation_number} running...")
            self.play(simulation_number)
            self.reset_game_state()

    def calculate_simultation_statistics(self):
        # TODO: Write test for these simulations-level calculations
        self.sim_stats.number_of_simulations = len(self.game_stats)

        sum_number_of_win_rolls = 0
        sum_distance_climbed = 0
        sum_distance_slid = 0
        sum_unlucky_rolls = 0
        sum_lucky_rolls = 0

        for game_stat in self.game_stats:
            self.sim_stats.min_number_of_win_rolls = min(
                game_stat.game_number_of_rolls_to_win,
                self.sim_stats.min_number_of_win_rolls,
            )
            self.sim_stats.max_number_of_win_rolls = max(
                game_stat.game_number_of_rolls_to_win,
                self.sim_stats.max_number_of_win_rolls,
            )
            sum_number_of_win_rolls += game_stat.game_number_of_rolls_to_win

            self.sim_stats.min_distance_climbed = min(
                game_stat.game_total_distance_climbed,
                self.sim_stats.min_distance_climbed,
            )
            self.sim_stats.max_distance_climbed = max(
                game_stat.game_total_distance_climbed,
                self.sim_stats.max_distance_climbed,
            )
            sum_distance_climbed += game_stat.game_total_distance_climbed

            self.sim_stats.min_distance_slid = min(
                game_stat.game_total_distance_slid, self.sim_stats.min_distance_slid
            )
            self.sim_stats.max_distance_slid = max(
                game_stat.game_total_distance_slid, self.sim_stats.max_distance_slid
            )
            sum_distance_slid += game_stat.game_total_distance_slid

            self.sim_stats.biggest_climb = max(
                game_stat.game_max_distance_climbed, self.sim_stats.biggest_climb
            )
            self.sim_stats.biggest_slide = max(
                game_stat.game_max_distance_slide, self.sim_stats.biggest_slide
            )

            self.sim_stats.min_unlucky_rolls = min(
                game_stat.game_total_unlucky_rolls, self.sim_stats.min_unlucky_rolls
            )
            self.sim_stats.max_unlucky_rolls = max(
                game_stat.game_total_unlucky_rolls, self.sim_stats.max_unlucky_rolls
            )
            sum_unlucky_rolls += game_stat.game_total_unlucky_rolls

            self.sim_stats.min_lucky_rolls = min(
                game_stat.game_total_lucky_rolls, self.sim_stats.min_lucky_rolls
            )
            self.sim_stats.max_lucky_rolls = max(
                game_stat.game_total_lucky_rolls, self.sim_stats.max_lucky_rolls
            )
            sum_lucky_rolls += game_stat.game_total_lucky_rolls

            if sum(game_stat.game_max_streak) > sum(self.sim_stats.max_streak):
                self.sim_stats.max_streak = game_stat.game_max_streak

        self.sim_stats.avg_number_of_win_rolls = round(
            sum_number_of_win_rolls / self.sim_stats.number_of_simulations, 2
        )
        self.sim_stats.avg_distance_climbed = round(
            sum_distance_climbed / self.sim_stats.number_of_simulations, 2
        )
        self.sim_stats.avg_distance_slid = round(
            sum_distance_slid / self.sim_stats.number_of_simulations, 2
        )
        self.sim_stats.avg_unlucky_rolls = round(
            sum_unlucky_rolls / self.sim_stats.number_of_simulations, 2
        )
        self.sim_stats.avg_lucky_rolls = round(
            sum_lucky_rolls / self.sim_stats.number_of_simulations, 2
        )
