import numpy as np
from typing import List
from pydantic import BaseModel
from abc import ABC, abstractmethod
from scipy.interpolate import interp1d

class FlightAction(BaseModel):
    velocity_m_s: float
    use_termal: bool

class AircraftModel(BaseModel):
    velocity_max_m_s: float
    velocity_min_m_s: float
    velocity_best_glide_m_s: float
    list_velocity_m_s: List[float]
    list_sink_rate_m_s: List[float]

    def get_sink_rate_m_s(self, velocity_m_s: float) -> float:
        if velocity_m_s < self.velocity_min_m_s:
            raise Exception(f"Velocity {velocity_m_s} is below the minimum velocity {self.velocity_min_m_s}")
        if velocity_m_s > self.velocity_max_m_s:
            raise Exception(f"Velocity {velocity_m_s} is above the maximum velocity {self.velocity_max_m_s}")
        return interp1d(self.list_velocity_m_s, self.list_sink_rate_m_s)(velocity_m_s)




class AircraftModelSimple(BaseModel):
    velocity_max_m_s: float
    sink_max_m_s: float


class FlightState(BaseModel):
    list_time_s: List[float]
    list_altitude_m: List[float]
    list_distance_m: List[float]
    list_termal_net_rise_current_m_s: List[float]
    is_landed: bool

    def fly_distance(self, time_taken_s: float, distance_m: float, altitude_m: float, termal_net_rise_current_m_s: float, is_landed: bool) -> None:
        self.list_time_s.append(self.list_time_s[-1] + time_taken_s)
        self.list_distance_m.append(self.list_distance_m[-1] + distance_m)
        self.list_altitude_m.append(self.list_altitude_m[-1] + altitude_m)
        self.list_termal_net_rise_current_m_s.append(termal_net_rise_current_m_s)
        self.is_landed = is_landed

class Termal(BaseModel):
    distance_from_last_termal_m: float
    net_rise_m_s: float

class FlightConditions(BaseModel):
    take_off_time_s: float
    take_off_altitude_m: float
    landing_time_s: float
    termal_ceiling_m: float
    termal_net_rise_mean_m_s: float
    termal_net_rise_std_m_s: float
    termal_distance_mean_m: float
    termal_distance_std_m: float


    def sample_termal(self) -> Termal:
        termal_distance_min_m = 100
        distance_from_last_termal_m = np.random.normal(self.termal_distance_mean_m, self.termal_distance_std_m)
        distance_from_last_termal_m = max(distance_from_last_termal_m, termal_distance_min_m)
        net_rise_m_s = np.random.normal(self.termal_net_rise_mean_m_s, self.termal_net_rise_std_m_s)
        net_rise_m_s = max(net_rise_m_s, 0.5)
        return Termal(distance_from_last_termal_m=distance_from_last_termal_m, net_rise_m_s=net_rise_m_s)


class FlightPolicy(ABC):
    policy_name: str
    def __init__(self, policy_name: str):
        self.policy_name = policy_name

    @abstractmethod
    def get_flight_action(self, flight_state: FlightState, aircraft_model: AircraftModel) -> FlightAction:
        pass


class FlightPolicySimple(ABC):
    policy_name: str
    def __init__(self, policy_name: str):
        self.policy_name = policy_name

    @abstractmethod
    def use_termal(self, flight_state: FlightState, aircraft_model: AircraftModel) -> bool:
        pass



class FlightPolicySimpleNeverTermal(FlightPolicySimple):

    def __init__(self):
        super().__init__(policy_name="MaxVelocityNeverTermal")

    def get_flight_action(self, flight_state: FlightState, aircraft_model: AircraftModel) -> bool:
        return False

class FlightPolicySimpleAlwaysTermal(FlightPolicySimple):

    def __init__(self):
        super().__init__(policy_name="MaxVelocityNeverTermal")

    def get_flight_action(self, flight_state: FlightState, aircraft_model: AircraftModel) -> bool:
        return False





class FlightPolicyMaxVelocityNeverTermal(FlightPolicy):

    def __init__(self):
        super().__init__(policy_name="MaxVelocityNeverTermal")

    def get_flight_action(self, flight_state: FlightState, aircraft_model: AircraftModel) -> FlightAction:
        return FlightAction(velocity_m_s=aircraft_model.velocity_max_m_s, use_termal=False)



class FlightPolicyMaxVelocityAlwaysTermal(FlightPolicy):

    def __init__(self):
        super().__init__(policy_name="MaxVelocityAlwaysTermal")

    def get_flight_action(self, flight_state: FlightState, aircraft_model: AircraftModel) -> FlightAction:
        return FlightAction(velocity_m_s=aircraft_model.velocity_max_m_s, use_termal=True)
