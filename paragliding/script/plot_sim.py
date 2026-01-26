from pathlib import Path

from paragliding.flight_policy import (
    FlightPolicyThreeZones,
)
from paragliding.flight_policy_neural import FlightPolicyNeuralNetwork
from paragliding.flight_conditions import FlightConditions
from paragliding.model import AircraftModel
from paragliding.tools_plot import plot_flight
from paragliding.tools_sim import simulate_flight

flight_conditions = FlightConditions(
    take_off_time_s=0,
    take_off_altitude_m=1000,
    landing_time_s=3600 * 6,
    distance_max_m=3600 * 6 * 10,
    termal_ceiling_m=1000,
    termal_net_climb_min_m_s=0.1,
    termal_net_climb_mean_m_s=0.5,
    termal_net_climb_std_m_s=0.5,
    termal_net_climb_max_m_s=8,
    termal_distance_min_m=1000,
    termal_distance_mean_m=2000,
    termal_distance_std_m=1000,
    termal_distance_max_m=10000,
)
aircraft_model = AircraftModel(
    velocity_max_m_s=10,
    sink_max_m_s=-1,
)

# flight_policy_nt = FlightPolicyNeverTermal()
# flight_policy_at = FlightPolicyAlwaysTermal()
flight_policy_tn = FlightPolicyThreeZones(0.9, 0.5)

model_path = Path("data", "database_model", "neural_policy.pth")
# make sure partent dir exists
model_path.parent.mkdir(parents=True, exist_ok=True)
flight_policy_nn = FlightPolicyNeuralNetwork(
    model_path=model_path,
    threshold=0.8,
)
experiment_result = simulate_flight(
    flight_conditions,
    aircraft_model,
    flight_policy_nn,
    termal_time_step_s=10,
)

plot_flight(experiment_result)
