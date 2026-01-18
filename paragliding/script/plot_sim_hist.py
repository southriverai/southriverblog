from paragliding.tools_sim import simulate_flight
from paragliding.tools_plot import plot_flight,plot_polar
from paragliding.model import FlightConditions, FlightPolicyMaxVelocityNeverTermal, FlightPolicyMaxVelocityAlwaysTermal, AircraftModel

flight_conditions = FlightConditions(
    take_off_time_s=0,
    take_off_altitude_m=1000,
    landing_time_s=3600,
    termal_ceiling_m=1000,
    termal_net_rise_mean_m_s=1,
    termal_net_rise_std_m_s=1,
    termal_distance_mean_m=1000,
    termal_distance_std_m=1000,
)

aircraft_model = AircraftModel(
    velocity_max_m_s=10,
    velocity_min_m_s=1,
    velocity_best_glide_m_s=5,
    list_velocity_m_s=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    list_sink_rate_m_s=[-0.1, -0.2, -0.3, -0.4, -0.5, -0.6, -0.7, -0.8, -0.9, -1.0],
)

#flight_policy_never_termal = FlightPolicyMaxVelocityNeverTermal()
flight_policy_always_termal = FlightPolicyMaxVelocityAlwaysTermal()
flight_state = simulate_flight(flight_conditions, aircraft_model, flight_policy_always_termal)
#plot_polar(aircraft_model)
plot_flight(flight_state)