from pathlib import Path

from paragliding.experiment import ExperimentOutputBatch
from paragliding.flight_policy import (
    FlightPolicyAlwaysTermal,
    FlightPolicyNeverTermal,
    FlightPolicyThreeZones,
)
from paragliding.flight_policy_neural import FlightPolicyNeuralNetwork
from paragliding.model import (
    AircraftModel,
    FlightConditions,
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
flight_policies = []
flight_policies.append(FlightPolicyThreeZones(0.9, 0.5))
# flight_policies.append(FlightPolicyThreeZones(0.7, 0.4))
# flight_policies.append(FlightPolicyThreeZones(0.7, 0.3))
# flight_policies.append(FlightPolicyThreeZones(0.7, 0.2))
# flight_policies.append(FlightPolicyThreeZones(0.7, 0.1))


# flight_policies.append(FlightPolicyThreeZones(0.6, 0.6))
# flight_policies.append(FlightPolicyThreeZones(0.6, 0.5))
flight_policies.append(FlightPolicyThreeZones(0.6, 0.4))  # p95
# flight_policies.append(FlightPolicyThreeZones(0.6, 0.3))
# flight_policies.append(FlightPolicyThreeZones(0.6, 0.2))
# flight_policies.append(FlightPolicyThreeZones(0.6, 0.1))
# flight_policies.append(FlightPolicyThreeZones(0.6, 0.0))

# flight_policies.append(FlightPolicyThreeZones(0.5, 0.4))
flight_policies.append(FlightPolicyThreeZones(0.5, 0.3))  # p50
# flight_policies.append(FlightPolicyThreeZones(0.5, 0.2))
# flight_policies.append(FlightPolicyThreeZones(0.5, 0.1))
# flight_policies.append(FlightPolicyThreeZones(0.5, 0.0))

flight_policies.append(
    FlightPolicyNeuralNetwork(
        model_path=Path("data", "database_model", "neural_policy.pth"),
        threshold=0.8,
    )
)

experiment_result_baches: list[ExperimentOutputBatch] = []
labels = []
for flight_policy in flight_policies:
    path_file_result = f"result_{flight_policy.get_hash()}.json"
    if Path(path_file_result).exists():
        experiment_output_batch = ExperimentOutputBatch.model_validate_json(
            Path(path_file_result).read_text()
        )
        experiment_result_baches.append(experiment_output_batch)
    else:
        experiment_output_batch = simulate_flight_many(
            flight_conditions,
            aircraft_model,
            flight_policy,
            flight_count=1000,
            termal_time_step_s=10,
        )
        experiment_result_baches.append(experiment_output_batch)
        Path(path_file_result).write_text(experiment_output_batch.model_dump_json())
    labels.append(flight_policy.policy_name)
plot_flight_hists(experiment_result_baches, labels)
