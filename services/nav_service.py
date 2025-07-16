import threading
from typing import List, Tuple
import numpy as np
import logging

# Core navigation modules
from core.navigation.old.navigator import Navigator
from core.navigation.old.obstacle_avoidance import ObstacleAvoidance
from core.navigation.old.algorithms import PathfindingAlgorithms
from core.navigation.old.utils import haversine

# Service modules
from services.gps_service import GPSService
from services.obstacle_service import ObstacleService

logger = logging.getLogger("NavigationService")

class NavigationService:
    """
    High-level navigation service integrating GPS routing, obstacle avoidance,
    and grid-based pathfinding.
    """
    def __init__(self, google_maps_api_key: str, safety_distance: float = 1.0):
        self.navigator = Navigator(google_maps_api_key)
        self.obstacle_avoidance = ObstacleAvoidance(safety_distance)

    def plan_route(self, origin: str, destination: str, mode: str = "walking") -> List[Tuple[float, float]]:
        try:
            route_data = self.navigator.get_route(origin, destination, mode)
            coordinates = self.navigator.get_route_coordinates(route_data)
            return coordinates
        except Exception as e:
            logger.error(f"Route planning failed: {e}")
            return []

    def avoid_obstacles_on_route(
        self,
        current_pos: Tuple[float, float],
        target_pos: Tuple[float, float],
        depth_map: np.ndarray
    ) -> List[Tuple[float, float]]:
        try:
            obstacles = self.obstacle_avoidance.detect_obstacles(depth_map)
            return self.obstacle_avoidance.calculate_avoidance_path(current_pos, target_pos, obstacles)
        except Exception as e:
            logger.error(f"Obstacle avoidance failed: {e}")
            return []

    def compute_grid_path(
        self,
        grid: List[List[int]],
        start: Tuple[int, int],
        end: Tuple[int, int],
        algorithm: str = "a_star"
    ) -> List[Tuple[int, int]]:
        try:
            if algorithm == "dijkstra":
                return PathfindingAlgorithms.dijkstra(grid, start, end)
            return PathfindingAlgorithms.a_star(grid, start, end)
        except Exception as e:
            logger.error(f"Pathfinding failed: {e}")
            return []

    def distance_between_coords(self, coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
        return haversine(coord1, coord2)


class NavService:
    """
    Voice-based interface wrapper for user commands to GPS and obstacle modules.
    """
    def __init__(self):
        self.gps = GPSService()
        self.obstacle = ObstacleService()

    def navigate_to(self, location: str):
        try:
            self.gps.navigate(location)
        except Exception as e:
            logger.error(f"GPS navigation failed: {e}")

    def move_command(self, direction: str):
        try:
            self.obstacle.execute_movement(direction)
        except Exception as e:
            logger.error(f"Movement command failed: {e}")
