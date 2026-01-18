import matplotlib.pyplot as plt

from paragliding.model import FlightState, AircraftModel, FlightPolicy
from typing import List

def plot_flight(flight_state: FlightState):
    fig, axes = plt.subplots(3, 1, figsize=(15, 5))

    # plot time distance
    axes[0].plot(flight_state.list_time_s, flight_state.list_distance_m)
    axes[0].set_xlabel("Time (s)")
    axes[0].set_ylabel("Distance (m)")
    axes[0].set_title("Distance vs Time")
    axes[0].set_ylim(bottom=0)
    axes[0].grid(True)

    # plot time altitude
    axes[1].plot(flight_state.list_time_s, flight_state.list_altitude_m)
    axes[1].set_xlabel("Time (s)")
    axes[1].set_ylabel("Altitude (m)")
    axes[1].set_title("Altitude vs Time")
    axes[1].set_ylim(bottom=0)
    axes[1].grid(True)

    # plot time termal net rise current
    axes[2].plot(flight_state.list_time_s, flight_state.list_termal_net_rise_current_m_s)
    axes[2].set_xlabel("Time (s)")
    axes[2].set_ylabel("Thermal Net Rise (m/s)")
    axes[2].set_title("Thermal Net Rise vs Time")
    axes[2].set_ylim(bottom=0)
    axes[2].grid(True)

    plt.tight_layout()
    plt.show()



def plot_flights(list_flight_states: List[FlightState], list_flight_policies: List[FlightPolicy]):
    fig, axes = plt.subplots(3, 1, figsize=(15, 5))

    plt.tight_layout()
    plt.show()

def plot_polar(aircraft_model: AircraftModel):
    plt.plot(aircraft_model.list_velocity_m_s, aircraft_model.list_sink_rate_m_s)
    plt.xlabel("Velocity (m/s)")
    plt.ylabel("Sink Rate (m/s)")
    plt.title("Polar")
    plt.show()
