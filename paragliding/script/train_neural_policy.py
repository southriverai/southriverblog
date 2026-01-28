"""
Generate training data for neural network policy.
Predicts: If we leave the current thermal, will we find stronger lift?
"""
from argparse import ArgumentParser, Namespace
from pathlib import Path

import numpy as np
import torch
from tqdm import tqdm

from paragliding.flight_conditions import FlightConditions, FlightConditionsDistribution
from paragliding.flight_policy import FlightPolicyNeverTermal
from paragliding.flight_policy_neural import FlightPolicyNeuralNetwork
from paragliding.model import AircraftModel, FlightState
from paragliding.respository import Repository
from paragliding.simulator import Simulator
from paragliding.simulator_crude import SimulatorCrude
from paragliding.tools_sim import simulate_flight


def generate_training_data(
    num_flights: int = 10000,
    termal_time_step_s: float = 10.0,
) -> tuple[np.ndarray, np.ndarray]:
    aircraft_model = AircraftModel(
        velocity_max_m_s=10,
        sink_max_m_s=-1,
    )
    """
    Generate training data by simulating flights and collecting decision points.

    For each thermal decision point:
    - Extract features (X)
    - Check if next thermal has stronger lift than current (y)

    Returns:
        X: numpy array of shape (n_samples, 13) - features
        y: numpy array of shape (n_samples,) - labels (1 if next thermal stronger, 0 otherwise)
    """
    all_features = []
    all_labels = []

    # Use a policy that always uses thermals to collect decision points
    policy = FlightPolicyNeverTermal()
    policy_neural = FlightPolicyNeuralNetwork(
        model_path=Path("data", "database_model", "neural_policy.pth"),
        threshold=0.0,
    )

    for _ in tqdm(range(num_flights)):
        # uniform random climb between 0.1 and 4 m/s
        termal_net_climb_mean_m_s = np.random.uniform(0.1, 4)
        flight_conditions = FlightConditions(
            take_off_time_s=0,
            take_off_altitude_m=1000,
            landing_time_s=3600 * 6,
            distance_max_m=3600 * 6 * 10,
            termal_ceiling_m=1000,
            termal_net_climb_min_m_s=0.1,
            termal_net_climb_mean_m_s=termal_net_climb_mean_m_s,
            termal_net_climb_std_m_s=0.5,
            termal_net_climb_max_m_s=8,
            termal_distance_min_m=1000,
            termal_distance_mean_m=2000,
            termal_distance_std_m=1000,
            termal_distance_max_m=10000,
        )
        # Simulate a flight
        experiment_output = simulate_flight(flight_conditions, aircraft_model, policy, termal_time_step_s)

        flight_state = experiment_output.flight_state
        termals = experiment_output.termals

        # Track which thermal we're currently in
        current_termal_idx = 0

        # Go through flight state and identify when we're thermaling
        for state_idx in range(1, len(flight_state.list_distance_m)):
            # Check current climb rate
            if state_idx >= len(flight_state.list_altitude_m):
                continue

            # Calculate climb rate at this point
            if state_idx > 0:
                climb_m = flight_state.list_altitude_m[state_idx] - flight_state.list_altitude_m[state_idx - 1]
                time_diff = flight_state.list_time_s[state_idx] - flight_state.list_time_s[state_idx - 1]
                if time_diff > 0:
                    climb_rate = climb_m / time_diff
                else:
                    continue
            else:
                continue

            # Check if we're climbing (in a thermal)
            if climb_rate > 0.01:  # Small threshold to avoid noise
                # Find which thermal we're in
                current_distance = flight_state.list_distance_m[state_idx]

                # Update current_termal_idx if we've moved to a new thermal
                while current_termal_idx < len(termals) and current_distance > termals[current_termal_idx].distance_end_m:
                    current_termal_idx += 1

                # Check if we're actually in a thermal location
                if current_termal_idx < len(termals):
                    current_termal = termals[current_termal_idx]
                    if current_termal.distance_start_m <= current_distance <= current_termal.distance_end_m:
                        # We're in a thermal - this is a decision point
                        # Check if there's a next thermal to compare
                        if current_termal_idx < len(termals) - 1:
                            next_termal = termals[current_termal_idx + 1]

                            # Check if flight lands before reaching the next thermal
                            # We need to verify we successfully reach the next thermal location
                            lands_before_next = False
                            reached_next_thermal = False

                            # Look ahead through future states to see if we reach next thermal
                            for future_idx in range(state_idx + 1, len(flight_state.list_distance_m)):
                                if future_idx >= len(flight_state.list_distance_m):
                                    break

                                future_distance = flight_state.list_distance_m[future_idx]

                                # Check if we land before reaching next thermal
                                if future_idx < len(flight_state.list_altitude_m):
                                    if flight_state.list_altitude_m[future_idx] <= 0:
                                        # Landed before reaching next thermal
                                        lands_before_next = True
                                        break

                                # Check if we've reached the next thermal location
                                if future_distance >= next_termal.distance_start_m:
                                    reached_next_thermal = True
                                    break

                            # If we didn't reach the next thermal in the lookahead, check final state
                            if not reached_next_thermal and not lands_before_next:
                                final_distance = flight_state.list_distance_m[-1]
                                if final_distance < next_termal.distance_start_m:
                                    # Flight ended before reaching next thermal
                                    final_altitude = flight_state.list_altitude_m[-1] if len(flight_state.list_altitude_m) > 0 else 0
                                    if final_altitude <= 0:
                                        lands_before_next = True

                            # Create a snapshot of flight state at this point
                            snapshot_state = FlightState(
                                list_time_s=flight_state.list_time_s[: state_idx + 1].copy(),
                                list_altitude_m=flight_state.list_altitude_m[: state_idx + 1].copy(),
                                list_distance_m=flight_state.list_distance_m[: state_idx + 1].copy(),
                                is_landed=False,
                            )

                            # Extract features
                            features = policy_neural._extract_features(snapshot_state, aircraft_model)

                            # Label: 1 if next thermal is stronger AND we successfully reach it
                            # If we land before reaching next thermal, label as 0 (didn't find stronger lift)
                            if lands_before_next:
                                label = 0.0  # Landed before reaching next thermal - didn't find stronger lift
                            elif reached_next_thermal:
                                # Successfully reached next thermal location
                                label = 1.0 if next_termal.net_climb_m_s > current_termal.net_climb_m_s else 0.0
                            else:
                                # Flight ended before reaching next thermal (but didn't crash)
                                # This could be due to max time/distance - treat conservatively as 0
                                label = 0.0

                            all_features.append(features)
                            all_labels.append(label)

                            # Sample every N steps to avoid too many similar samples
                            # Skip ahead to get diverse samples
                            if state_idx % 10 == 0:  # Sample every 10th step when in thermal
                                pass

    # Convert to numpy arrays
    X = np.array(all_features, dtype=np.float32)
    y = np.array(all_labels, dtype=np.float32)

    return X, y


def get_training_data() -> tuple[np.ndarray, np.ndarray]:
    """Get training data from file or generate it."""
    repository = Repository.get_instance()

    path_file_training_data = Path("data", "database_training", "training_data.npz")
    if path_file_training_data.exists():
        X, y = load_training_data(path_file_training_data)
    else:
        X, y = generate_training_data()
        save_training_data(
            path_file_training_data,
            X,
            y,
        )
    return X, y


def train_model(X: np.ndarray, y: np.ndarray) -> None:
    """Train model."""
    model_path = Path("data", "database_model", "neural_policy.pth")

    model = FlightPolicyNeuralNetwork(
        model_path=model_path,
    )
    model.train(X, y, epoch_count=5000, lr=0.001)
    model.save()
    return model


def do_train_rl(
    policy: FlightPolicyNeuralNetwork,
    simulator: Simulator,
    rollout_count: int,
    simulations_per_rollout: int,
    epochs_per_rollout: int,
    learning_rate: float,
) -> None:
    """Train model."""
    # preserve best policy (most mean distance)
    best_distance = 0
    for rollout_idx in range(rollout_count):
        print(f"Rolling out {rollout_idx} of {rollout_count}")
        simulation_results = simulator.simulate_batch(policy, simulations_per_rollout)
        # comput mean distance traveled
        list_distance_m = []
        for experiment_output in simulation_results.list_experiment_outputs:
            list_distance_m.append(experiment_output.flight_state.list_distance_m[-1])
        mean_distance = np.mean(list_distance_m)
        if best_distance < mean_distance:
            best_distance = mean_distance
            policy.save_file(Path("best_model.pth"))
        print(f"Mean distance: {mean_distance}")
        input_matrix, output_matrix = policy.convert_to_matrixes(simulation_results)

        input__tensor = torch.FloatTensor(input_matrix)
        output_tensor = torch.FloatTensor(output_matrix)
        policy.network.train()
        optimizer = torch.optim.Adam(policy.network.parameters(), lr=learning_rate)
        criterion = torch.nn.MSELoss()  # Use MSE for regression (continuous targets), not BCELoss (binary classification)
        list_loss = []
        pbar = tqdm(range(epochs_per_rollout))
        for _ in pbar:
            optimizer.zero_grad()
            output = policy.network(input__tensor)
            loss = criterion(output, output_tensor)
            loss.backward()
            optimizer.step()
            loss_value = loss.item()
            list_loss.append(loss_value)
            pbar.set_postfix({"loss": loss_value})
        policy.network.eval()
        policy.save()
        # plot loss function
        # import matplotlib.pyplot as plt  # pyright: ignore[reportMissingImports]

        # plt.plot(list_loss)
        # plt.xlabel("Epoch")
        # plt.ylabel("Loss")
        # plt.title("Loss Function")
        # plt.show()


def train_direct() -> None:
    # Example usage - create flight conditions and aircraft model

    # Generate training data
    print("Generating training data...")
    X, y = get_training_data()

    print(f"Generated {len(X)} training samples")
    print(f"Features shape: {X.shape}")
    print(f"Labels shape: {y.shape}")
    print(f"Positive samples (stronger lift ahead): {np.sum(y == 1.0)}")
    print(f"Negative samples (weaker lift ahead): {np.sum(y == 0.0)}")

    # train model
    print("Training model...")
    model = train_model(X, y)


def train_rl() -> None:
    model_path = Path("data", "database_model", "neural_policy.pth")
    policy = FlightPolicyNeuralNetwork(
        model_path=model_path,
    )
    if Path("best_model.pth").exists():
        # load best model
        policy.load_path_file(Path("best_model.pth"))

    aircraft_model = AircraftModel(
        velocity_max_m_s=10,
        sink_max_m_s=-1,
    )
    flight_condition_distribution = FlightConditionsDistribution(
        termal_net_climb_mean_min_m_s=0.5,
        termal_net_climb_mean_max_m_s=0.5,
    )
    simulator = SimulatorCrude(
        flight_condition_distribution=flight_condition_distribution,
        aircraft_model=aircraft_model,
    )
    do_train_rl(
        policy,
        simulator,
        rollout_count=200,
        simulations_per_rollout=1000,
        epochs_per_rollout=100,
        learning_rate=0.002,
    )


def parse_args() -> Namespace:
    parser = ArgumentParser(description="Train neural policy")
    parser.add_argument(
        "mode", type=str, nargs="?", default="direct", choices=["direct", "rl"], help="Training mode: 'direct' or 'rl' (default: direct)"
    )
    return parser.parse_args()


if __name__ == "__main__":
    repository = Repository.initialize()
    args = parse_args()
    print(f"Running in {args.mode} mode")
    if args.mode == "direct":
        train_direct()
    elif args.mode == "rl":
        train_rl()
    else:
        raise ValueError(f"Invalid mode: {args.mode}")
