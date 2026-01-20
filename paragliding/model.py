from abc import ABC, abstractmethod
from typing import Any

import numpy as np
from pydantic import BaseModel


class FlightAction(BaseModel):
    velocity_m_s: float
    use_termal: bool


# class AircraftModel(BaseModel):
#     velocity_max_m_s: float
#     velocity_min_m_s: float
#     velocity_best_glide_m_s: float
#     list_velocity_m_s: List[float]
#     list_sink_rate_m_s: List[float]

#     def get_sink_rate_m_s(self, velocity_m_s: float) -> float:
#         if velocity_m_s < self.velocity_min_m_s:
#             raise Exception(f"Velocity {velocity_m_s} is below the minimum velocity {self.velocity_min_m_s}")
#         if velocity_m_s > self.velocity_max_m_s:
#             raise Exception(f"Velocity {velocity_m_s} is above the maximum velocity {self.velocity_max_m_s}")
#         return interp1d(self.list_velocity_m_s, self.list_sink_rate_m_s)(velocity_m_s)


class AircraftModel(BaseModel):
    velocity_max_m_s: float
    sink_max_m_s: float


class FlightState(BaseModel):
    list_time_s: list[float]
    list_altitude_m: list[float]
    list_distance_m: list[float]
    is_landed: bool
    cache: dict[str, Any] = {}

    def current_climb_m_s(self) -> float:
        if len(self.list_altitude_m) < 2:
            return 0
        current_climb_m = self.list_altitude_m[-1] - self.list_altitude_m[-2]

        if self.list_time_s[-2] == self.list_time_s[-1]:
            print(self.list_time_s)
            raise Exception("Time step is 0")
        current_climb_m_s = current_climb_m / (self.list_time_s[-1] - self.list_time_s[-2])
        return current_climb_m_s

    def get_node_climb_m_s(self, node_index: int) -> float:
        if node_index == 0:
            return 0
        if node_index >= len(self.list_time_s):
            return 0
        node_climb_m = self.list_altitude_m[node_index] - self.list_altitude_m[node_index - 1]
        node_climb_m_s = node_climb_m / (
            self.list_time_s[node_index] - self.list_time_s[node_index - 1]
        )
        self.cache[node_index] = node_climb_m_s
        return node_climb_m_s

    def termal_climbs(self) -> list[float]:
        # merges all consequetive nodes with climb and produces one average number for each termal
        if len(self.list_time_s) < 2:
            return []

        if "termal_climbs" in self.cache:
            node_index = self.cache["termal_climbs"]["node_index"]
            termal_climbs = self.cache["termal_climbs"]["termal_climbs"]
            current_termal_climbs = self.cache["termal_climbs"]["current_termal_climbs"]
        else:
            node_index = 1
            termal_climbs = []
            current_termal_climbs = []
        while node_index < len(self.list_time_s):
            node_climb_m_s = self.get_node_climb_m_s(node_index)
            if node_climb_m_s > 0:
                current_termal_climbs.append(node_climb_m_s)
            elif len(current_termal_climbs) > 0:
                termal_climbs.append(np.mean(current_termal_climbs))
                current_termal_climbs = []
            node_index += 1
        self.cache["termal_climbs"] = {
            "termal_climbs": termal_climbs,
            "current_termal_climbs": current_termal_climbs,
            "node_index": node_index,
        }
        return termal_climbs


class Termal(BaseModel):
    distance_start_m: float
    distance_end_m: float
    net_climb_m_s: float


class FlightConditions(BaseModel):
    take_off_time_s: float
    take_off_altitude_m: float
    landing_time_s: float
    distance_max_m: float
    termal_ceiling_m: float
    termal_net_climb_min_m_s: float
    termal_net_climb_mean_m_s: float
    termal_net_climb_std_m_s: float
    termal_net_climb_max_m_s: float
    termal_distance_min_m: float
    termal_distance_mean_m: float
    termal_distance_std_m: float
    termal_distance_max_m: float

    def sample_termal(self, last_distance_end_m) -> Termal:
        distance_from_last_termal_m = np.random.normal(
            self.termal_distance_mean_m, self.termal_distance_std_m
        )
        distance_start_m = np.clip(
            distance_from_last_termal_m, self.termal_distance_min_m, self.termal_distance_max_m
        )
        distance_start_m += last_distance_end_m
        net_climb_m_s = np.random.normal(
            self.termal_net_climb_mean_m_s, self.termal_net_climb_std_m_s
        )
        net_climb_m_s = np.clip(
            net_climb_m_s, self.termal_net_climb_min_m_s, self.termal_net_climb_max_m_s
        )
        return Termal(
            distance_start_m=distance_start_m,
            distance_end_m=distance_start_m + 200,
            net_climb_m_s=net_climb_m_s,
        )

    def sample_termals(self) -> list[Termal]:
        termals = [self.sample_termal(0)]
        while termals[-1].distance_end_m < self.distance_max_m:
            termals.append(self.sample_termal(termals[-1].distance_end_m))
        return termals

    @staticmethod
    def series_termal(
        termals: list[Termal],
        distance_max_m: float,
    ) -> tuple[list[float], list[float]]:
        """
        Produce a blocky series derived from sample_termals for plotting.
        Returns:
            Tuple of (distance_series, thermal_strength_series)
            Both series have the same length and represent thermal strength as constant blocks.
        """
        # Initialize lists with starting point at distance 0
        distance_series = [0.0]
        thermal_strength_series = [0.0]  # No thermal at start

        # For each thermal, add points at start and end to create blocky series
        for termal in termals:
            # Add point just before thermal starts (thermal strength = 0)

            distance_series.append(termal.distance_start_m)
            thermal_strength_series.append(0.0)

            # Add point at thermal start (thermal strength = termal strength)
            distance_series.append(termal.distance_start_m)
            thermal_strength_series.append(termal.net_climb_m_s)

            # Add point at thermal end (thermal strength = termal strength)
            distance_series.append(termal.distance_end_m)
            thermal_strength_series.append(termal.net_climb_m_s)

            # Add point just after thermal ends (thermal strength = 0)
            if termal.distance_end_m < distance_max_m:
                distance_series.append(termal.distance_end_m)
                thermal_strength_series.append(0.0)

        # Ensure we end at max distance
        if distance_series[-1] < distance_max_m:
            distance_series.append(distance_max_m)
            thermal_strength_series.append(0.0)

        return distance_series, thermal_strength_series


class FlightPolicy(ABC):
    policy_name: str

    def __init__(self, policy_name: str):
        self.policy_name = policy_name

    @abstractmethod
    def use_termal(self, flight_state: FlightState, aircraft_model: AircraftModel) -> bool:
        pass


class FlightPolicyNeverTermal(FlightPolicy):
    def __init__(self):
        super().__init__(policy_name="NeverTermal")

    def use_termal(
        self,
        flight_state: FlightState,
        aircraft_model: AircraftModel,
    ) -> bool:
        return False


class FlightPolicyAlwaysTermal(FlightPolicy):
    def __init__(self):
        super().__init__(policy_name="AlwaysTermal")

    def use_termal(
        self,
        flight_state: FlightState,
        aircraft_model: AircraftModel,
    ) -> bool:
        # if we experience climb since the last node we keep termaling
        if len(flight_state.list_altitude_m) < 2:
            return False
        last_climb = flight_state.list_altitude_m[-1] - flight_state.list_altitude_m[-2]
        if last_climb > 0:
            return True
        else:
            return False


class FlightPolicyThreeZones(FlightPolicy):
    def __init__(self, progress_quantile: float, lift_zone_quantile: float):
        super().__init__(policy_name=f"ThreeZones {progress_quantile} {lift_zone_quantile}")
        self.progress_quantile = progress_quantile
        self.lift_zone_quantile = lift_zone_quantile
        self.explore_termal_count = 2

    def use_termal(
        self,
        flight_state: FlightState,
        aircraft_model: AircraftModel,
    ) -> bool:
        # Simple three-zone policy: use termal if below starting altitude (survival zone)
        if len(flight_state.list_altitude_m) < 1:
            return False
        altitude = flight_state.list_altitude_m[-1]
        starting_altitude = flight_state.list_altitude_m[0]  # asume we start at ceiling
        progress_altitude = starting_altitude * 0.66
        lift_altitude = starting_altitude * 0.33
        current_climb_m_s = flight_state.current_climb_m_s()
        if current_climb_m_s <= 0:
            # if we are not climbing, we do not use termal
            return False
        termal_climbs = flight_state.termal_climbs()
        if len(termal_climbs) < self.explore_termal_count:
            # if we have not experienced many termals, we do use termal just to try
            return True

        progress_threshold = np.quantile(termal_climbs, self.progress_quantile)
        lift_threshold = np.quantile(termal_climbs, self.lift_zone_quantile)

        # If below starting altitude, use termal for survival
        if altitude > progress_altitude:
            return current_climb_m_s > progress_threshold
        elif altitude > lift_altitude:
            return current_climb_m_s > lift_threshold
        else:
            # we are in the survival zone so we use termal to survive
            return True
