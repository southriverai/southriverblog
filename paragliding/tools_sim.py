import numpy as np
import matplotlib.pyplot as plt

from pydantic import BaseModel

from model import AircraftModel, FlightState, FlightConditions, FlightPolicy

def simulate_flight(flight_conditions: FlightConditions, flight_policy: FlightPolicy, aircraft_model: AircraftModel):
    time_s = flight_conditions.take_off_time
    distance_m = 0
    altitude_m = flight_conditions.take_off_altitude
    flight_state = FlightState(
        list_time_s=[time_s],
        list_altitude_m=[altitude_m],
        list_distance_m=[distance_m],
        list_termal_net_rise_current_m_s=[0],
        is_landed=False,)

    while not flight_state.is_landed():
        velocity_m_s = flight_policy.get_velocity_m_s(flight_state, aircraft_model)
        sink_rate_m_s = aircraft_model.get_sink_rate_m_s(velocity_m_s)



        # sample a termal
        distance_to_termal_m, net_rise_m_s = flight_conditions.sample_termal()
        # check if we made it here before the landing time runs out
        time_to_termal_s  = distance_to_termal_m / velocity_m_s
        if time_s + time_to_termal_s > flight_conditions.landing_time_s:
            # we were forced to land before we reached the termal so we just travel the remaining distance at the current velocity
            remaining_flight_time_s = flight_conditions.landing_time_s - time_s
            remaining_distance_m = velocity_m_s * remaining_flight_time_s
            remaining_altitude_m = sink_rate_m_s * remaining_flight_time_s
            flight_state.fly_distance(remaining_flight_time_s, remaining_distance_m, remaining_altitude_m, 0, is_landed=True)
        else:
            remaining_altitude_m = sink_rate_m_s * remaining_flight_time_s
            flight_state.fly_distance(time_to_termal_s, distance_to_termal_m, net_rise_m_s, is_landed=False)

        # if we do make it here, we are in the termal and we have to decide how to continue

        time
        flight_state = FlightState(time=time_s, altitude=altitude_m, termal_net_rise_current=0)




        flight_state = flight_policy.get_flight_state(flight_state)
        return flight_state
