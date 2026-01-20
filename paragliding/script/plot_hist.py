from paragliding.model import (
    AircraftModel,
    FlightConditions,
    FlightPolicyAlwaysTermal,
    FlightPolicyNeverTermal,
    FlightPolicyThreeZones,
)
from paragliding.tools_plot import plot_flight_hists
from paragliding.tools_sim import simulate_flight_many

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

flight_policy_nt = FlightPolicyNeverTermal()
flight_policy_at = FlightPolicyAlwaysTermal()
flight_policy_tn = FlightPolicyThreeZones(0.9, 0.5)
flight_distances, flight_durations = simulate_flight_many(
    flight_conditions,
    aircraft_model,
    flight_policy_tn,
    flight_count=1000,
    termal_time_step_s=10,
)
plot_flight_hists(flight_distances, flight_durations)
