from pathlib import Path

from paragliding.experiment import ExperimentOutputBatch
from paragliding.flight_conditions import FlightConditionsDistribution
from paragliding.flight_policy import FlightPolicyAlwaysTermal, FlightPolicyNeverTermal, FlightPolicyThreeZones
from paragliding.model import AircraftModel
from paragliding.simulator_crude import SimulatorCrude
from paragliding.tools_plot import plot_flight_hists

flight_conditions_distribution = FlightConditionsDistribution(
    termal_net_climb_mean_min_m_s=0.5,
    termal_net_climb_mean_max_m_s=0.5,
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

# flight_policies.append(
#     FlightPolicyNeuralNetwork(
#         model_path=Path("data", "database_model", "neural_policy.pth"),
#         threshold=0.8,
#     )
# )
simulator = SimulatorCrude(
    flight_condition_distribution=flight_conditions_distribution,
    aircraft_model=aircraft_model,
)

experiment_result_baches: list[ExperimentOutputBatch] = []
labels = []
for flight_policy in flight_policies:
    path_file_result = f"result_{flight_policy.get_hash()}.json"
    if Path(path_file_result).exists():
        experiment_output_batch = ExperimentOutputBatch.model_validate_json(Path(path_file_result).read_text())
        experiment_result_baches.append(experiment_output_batch)
    else:
        experiment_output_batch = simulator.simulate_batch(
            flight_policy,
            num_simulations=1000,
        )
        experiment_result_baches.append(experiment_output_batch)
        Path(path_file_result).write_text(experiment_output_batch.model_dump_json())
    labels.append(flight_policy.policy_name)
plot_flight_hists(experiment_result_baches, labels)
