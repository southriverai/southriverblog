import matplotlib.pyplot as plt

from paragliding.model import AircraftModel, FlightConditions, FlightPolicy, FlightState, Termal


def plot_flight_hists(flight_distances: list[float], flight_durations: list[float]):
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    axes[0].hist(flight_distances, bins=20)
    axes[0].set_xlabel("Distance (km)")
    axes[0].set_ylabel("Frequency")
    axes[0].set_title("Distance Distribution")
    axes[1].hist(flight_durations, bins=20)
    axes[1].set_xlabel("Duration (s)")
    axes[1].set_ylabel("Frequency")
    axes[1].set_title("Duration Distribution")
    plt.tight_layout()
    plt.show()


def plot_flight(
    flight_state: FlightState,
    termals: list[Termal],
):
    fig, axes = plt.subplots(3, 1, figsize=(12, 8))

    # Convert distances to kilometers
    distance_km = [d / 1000.0 for d in flight_state.list_distance_m]
    distance_max_km = flight_state.list_distance_m[-1] / 1000.0

    # plot distance vs time
    axes[0].plot(distance_km, flight_state.list_time_s)
    axes[0].set_xlabel("Distance (km)")
    axes[0].set_ylabel("Time (s)")
    axes[0].set_title("Distance vs Time")
    axes[0].set_xlim(left=0, right=distance_max_km)
    axes[0].grid(True)

    # plot distance vs altitude
    axes[1].plot(distance_km, flight_state.list_altitude_m)
    axes[1].set_xlabel("Distance (km)")
    axes[1].set_ylabel("Altitude (m)")
    axes[1].set_title("Distance vs Altitude")
    axes[1].set_xlim(left=0, right=distance_max_km)
    axes[1].set_ylim(bottom=0)
    axes[1].grid(True)

    # plot flight conditions (thermal strength vs distance)
    distance_series, thermal_strength_series = FlightConditions.series_termal(
        termals, flight_state.list_distance_m[-1]
    )
    # Convert distance from meters to kilometers for better readability
    distance_series_km = [d / 1000.0 for d in distance_series]

    axes[2].step(
        distance_series_km,
        thermal_strength_series,
        where="post",
        linewidth=2,
        color="blue",
        label="Thermal Strength",
        alpha=0.8,
    )
    axes[2].fill_between(
        distance_series_km,
        thermal_strength_series,
        step="post",
        alpha=0.3,
        color="blue",
        label="_nolegend_",
    )
    axes[2].set_xlabel("Distance (km)")
    axes[2].set_ylabel("Thermal Strength (m/s)")
    axes[2].set_title(f"Thermal Conditions Along Flight Path (0 to {distance_max_km:.1f} km)")
    axes[2].set_xlim(left=0, right=distance_max_km)
    axes[2].set_ylim(bottom=0)
    axes[2].grid(True, alpha=0.3)
    axes[2].legend()

    plt.tight_layout()
    plt.show()


def plot_flights(list_flight_states: list[FlightState], list_flight_policies: list[FlightPolicy]):
    fig, axes = plt.subplots(3, 1, figsize=(15, 5))

    plt.tight_layout()
    plt.show()


def plot_polar(aircraft_model: AircraftModel):
    plt.plot(aircraft_model.list_velocity_m_s, aircraft_model.list_sink_rate_m_s)
    plt.xlabel("Velocity (m/s)")
    plt.ylabel("Sink Rate (m/s)")
    plt.title("Polar")
    plt.show()


def plot_flight_conditions(flight_conditions: FlightConditions):
    """
    Plot thermal strengths along the flight distance from 0 to max distance.
    Uses the series_termal function to get blocky series for plotting.
    """
    # Get blocky series from series_termal function
    distance_series, thermal_strength_series = flight_conditions.series_termal()

    # Convert distance from meters to kilometers
    distance_series_km = [d / 1000.0 for d in distance_series]
    distance_max_km = flight_conditions.distance_max_m / 1000.0

    # Create the plot
    fig, ax = plt.subplots(1, 1, figsize=(12, 6))

    # Plot the step-like series (blocky/step plot)
    # Using step='post' to make the steps appear at the right positions
    ax.step(
        distance_series_km,
        thermal_strength_series,
        where="post",
        linewidth=2,
        color="blue",
        label="Thermal Strength",
        alpha=0.8,
    )

    # Fill the area under the curve for better visualization
    ax.fill_between(
        distance_series_km,
        thermal_strength_series,
        step="post",
        alpha=0.3,
        color="blue",
        label="_nolegend_",
    )

    ax.set_xlabel("Distance (km)")
    ax.set_ylabel("Thermal Strength (m/s)")
    ax.set_title(f"Thermal Conditions Along Flight Path (0 to {distance_max_km:.1f} km)")
    ax.set_xlim(left=0, right=distance_max_km)
    ax.set_ylim(bottom=0)
    ax.grid(True, alpha=0.3)
    ax.legend()

    plt.tight_layout()
    plt.show()
