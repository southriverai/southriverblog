from paragliding.model import AircraftModel, FlightState, FlightConditions, FlightPolicy, Termal, FlightAction

def simulate_termal(flight_conditions: FlightConditions, aircraft_model: AircraftModel, flight_state: FlightState, flight_action: FlightAction, termal: Termal):
    altitude_to_ceiling_m = flight_conditions.termal_ceiling_m - flight_state.list_altitude_m[-1]
    flight_time_remaining_s = flight_conditions.landing_time_s - flight_state.list_time_s[-1]
    time_to_node_s = altitude_to_ceiling_m / termal.net_rise_m_s
    print(f"time_to_node_s: {time_to_node_s} flight_time_remaining_s: {flight_time_remaining_s}")
    if time_to_node_s > flight_time_remaining_s:
        print("land out of time")
        # we dont reach the ceiling before the landing time, we just fly to the ceiling and land
        time_to_node_s = flight_time_remaining_s
        is_landed = True
    else:
        is_landed = False

    distance_to_node_m = 0 # we are termal node so we dont fly any distance
    altitude_to_node_m = termal.net_rise_m_s * time_to_node_s
    flight_state.fly_distance(time_to_node_s, distance_to_node_m, altitude_to_node_m, termal.net_rise_m_s, is_landed=is_landed)


def simulate_progress(flight_conditions: FlightConditions, aircraft_model: AircraftModel, flight_state: FlightState, flight_action: FlightAction, termal: Termal):
    time_s = flight_state.list_time_s[-1]
    velocity_m_s = flight_action.velocity_m_s
    sink_rate_m_s = aircraft_model.get_sink_rate_m_s(velocity_m_s)
    time_to_termal_s  = termal.distance_from_last_termal_m / velocity_m_s
    if time_s + time_to_termal_s > flight_conditions.landing_time_s:
        print("land out of time")
        # we were forced to land before we reached the termal so we just travel the remaining distance at the current velocity
        remaining_flight_time_s = flight_conditions.landing_time_s - time_s
        remaining_distance_m = velocity_m_s * remaining_flight_time_s
        remaining_altitude_m = sink_rate_m_s * remaining_flight_time_s
        flight_state.fly_distance(remaining_flight_time_s, remaining_distance_m, remaining_altitude_m, 0, is_landed=True)
    else:
        print("not out of time")
        # check if we have reached actual termal
        altitute_at_termal_m = flight_state.list_altitude_m[-1] + sink_rate_m_s * time_to_termal_s
        if altitute_at_termal_m < 0:
            print("land out of altitude")
            # we were forced to land before we reaced the termal se we had to land
            time_to_node_s = flight_state.list_altitude_m[-1] / sink_rate_m_s
            distance_to_node_m = velocity_m_s * time_to_node_s
            altitude_to_node_m = 0
            flight_state.fly_distance(time_to_node_s, distance_to_node_m, altitude_to_node_m, 0, is_landed=True)
        else:
            # we just fly to the next termal
            time_to_node_s = time_to_termal_s
            distance_to_node_m = termal.distance_from_last_termal_m
            altitude_to_node_m = sink_rate_m_s * time_to_termal_s
            #print(f"fly to termal time {time_to_termal_s}  distance:{termal.distance_from_last_termal_m} sink:{sink_to_termal_m}")
            flight_state.fly_distance(time_to_node_s, distance_to_node_m, altitude_to_node_m, termal.net_rise_m_s, is_landed=False)


def simulate_flight(flight_conditions: FlightConditions, aircraft_model: AircraftModel, flight_policy: FlightPolicy) -> FlightState:
    time_s = flight_conditions.take_off_time_s
    flight_state = FlightState(
        list_time_s=[time_s],
        list_altitude_m=[flight_conditions.take_off_altitude_m],
        list_distance_m=[0],
        list_termal_net_rise_current_m_s=[0],
        is_landed=False,)

    while True:

        # sample a termal
        termal = flight_conditions.sample_termal()
        flight_action = flight_policy.get_flight_action(flight_state, aircraft_model)
        if flight_action.use_termal:
            print("Use termal")
            simulate_termal( flight_conditions, aircraft_model, flight_state, flight_action, termal)
            print(f"Time: {flight_state.list_time_s[-1]} Distance: {flight_state.list_distance_m[-1]} Altitude: {flight_state.list_altitude_m[-1]}")

        if not flight_state.is_landed:
            print("Use progress")
            simulate_progress(flight_conditions, aircraft_model, flight_state,flight_action, termal)
            print(f"Time: {flight_state.list_time_s[-1]} Distance: {flight_state.list_distance_m[-1]} Altitude: {flight_state.list_altitude_m[-1]}")

        else:
            print("Landed")
            break
    return flight_state
