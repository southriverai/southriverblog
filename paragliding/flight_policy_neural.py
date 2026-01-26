import hashlib
from pathlib import Path

import numpy as np
import torch
from torch import nn
from tqdm import tqdm

from paragliding.flight_policy import FlightPolicyBase
from paragliding.model import AircraftModel, FlightState


class ThermalPolicyNetwork(nn.Module):
    """
    Neural network for thermal policy decision making.
    Input features:
    - 10 deciles of past lift (10 values)
    - Current altitude (1 value)
    - Current lift (1 value)
    - Time since takeoff (1 value)
    Total: 13 input features
    Output: Single value (probability of using thermal)
    """

    def __init__(
        self,
        input_size: int = 13,
        hidden_sizes: list[int] | None = None,
        dropout: float = 0.1,
    ):
        super().__init__()

        # Use default hidden sizes if not provided
        if hidden_sizes is None:
            hidden_sizes = [64, 32]

        layers = []
        prev_size = input_size

        for hidden_size in hidden_sizes:
            # Ensure hidden_size is an integer
            if not isinstance(hidden_size, int):
                raise TypeError(
                    f"hidden_size must be an integer, got {type(hidden_size)}: {hidden_size}"
                )
            layers.append(nn.Linear(prev_size, hidden_size))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(dropout))
            prev_size = hidden_size

        # Output layer: single value (probability)
        layers.append(nn.Linear(prev_size, 1))
        layers.append(nn.Sigmoid())  # Output probability between 0 and 1

        self.network = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.network(x)


class FlightPolicyNeuralNetwork(FlightPolicyBase):
    """
    Flight policy that uses a neural network to decide whether to use thermal.

    The network predicts: "If we leave the current thermal, will we find stronger lift?"
    - If prediction > threshold: Leave thermal (return False) - stronger lift ahead
    - If prediction <= threshold: Stay in thermal (return True) - current thermal is better

    Features:
    - 10 deciles of past lift (from all climb rates)
    - Current altitude
    - Current lift rate
    - Time since takeoff
    """

    def __init__(
        self,
        model_path: Path,
        threshold: float,
    ):
        """
        Initialize neural network policy.

        Args:
            model_path: Path to saved model weights (if None, uses random initialization)
            hidden_sizes: List of hidden layer sizes
            dropout: Dropout probability
            threshold: Decision threshold (if output > threshold, leave thermal to find stronger lift)
        """
        super().__init__(policy_name="NeuralNetwork")
        hidden_sizes = [64, 32]
        dropout = 0.1
        self.threshold = threshold

        # Use default hidden sizes if not provided
        if hidden_sizes is None:
            hidden_sizes = [64, 32]

        # Initialize network
        self.network = ThermalPolicyNetwork(
            input_size=13,  # 10 deciles + altitude + current_lift + time
            hidden_sizes=hidden_sizes,
            dropout=dropout,
        )

        self.model_path = model_path
        # Load weights if provided
        if self.model_path.exists():
            print(f"Loading model weights from {self.model_path}")
            self.network.load_state_dict(torch.load(self.model_path, map_location="cpu"))
            # Set to evaluation mode
            self.network.eval()
        else:
            print(f"Model weights not found at {self.model_path}. Using random initialization.")
            self._init_weights()

    def _init_weights(self) -> None:
        for module in self.network.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                nn.init.zeros_(module.bias)
            elif isinstance(module, nn.Conv2d):
                nn.init.xavier_uniform_(module.weight)
                nn.init.zeros_(module.bias)
            elif isinstance(module, nn.ConvTranspose2d):
                nn.init.xavier_uniform_(module.weight)
                nn.init.zeros_(module.bias)
            elif isinstance(module, nn.Conv3d):
                nn.init.xavier_uniform_(module.weight)
                nn.init.zeros_(module.bias)
            elif isinstance(module, nn.ConvTranspose3d):
                nn.init.xavier_uniform_(module.weight)
                nn.init.zeros_(module.bias)
            elif isinstance(module, nn.BatchNorm2d):
                nn.init.ones_(module.weight)
                nn.init.zeros_(module.bias)

    def _extract_features(
        self, flight_state: FlightState, aircraft_model: AircraftModel
    ) -> np.ndarray:
        """
        Extract features from flight state.

        Returns:
            numpy array of shape (13,) with:
            - 10 deciles of past lift
            - Current altitude (normalized)
            - Current lift rate
            - Time since takeoff (normalized)
        """
        # Get all past climb rates using helper method
        past_climbs = flight_state.all_climbs()

        # Calculate 10 deciles of past lift
        if len(past_climbs) == 0:
            deciles = [0.0] * 10
        else:
            deciles = [
                np.quantile(past_climbs, q / 10.0) for q in range(1, 11)
            ]  # 10th, 20th, ..., 100th percentile

        # Current altitude (normalized by starting altitude)
        if len(flight_state.list_altitude_m) > 0:
            starting_altitude = flight_state.list_altitude_m[0]
            current_altitude = flight_state.list_altitude_m[-1]
            normalized_altitude = current_altitude / starting_altitude
        else:
            normalized_altitude = 0.0
        # Current lift rate
        current_lift = flight_state.current_climb_m_s()

        # Time since takeoff (normalized by max expected time, e.g., 6 hours)
        if len(flight_state.list_time_s) > 0:
            time_since_takeoff = flight_state.list_time_s[-1] - flight_state.list_time_s[0]
            # Normalize: assume max flight time is 6 hours (21600 seconds)
            max_time_s = 21600.0
            normalized_time = min(time_since_takeoff / max_time_s, 1.0)
        else:
            normalized_time = 0.0

        # Combine all features
        features = np.array(
            [*deciles, normalized_altitude, current_lift, normalized_time], dtype=np.float32
        )

        return features

    def use_termal(self, flight_state: FlightState, aircraft_model: AircraftModel) -> bool:
        """
        Use neural network to decide whether to use thermal.

        The network predicts: "If we leave, will we find stronger lift?"
        - If prediction > threshold: Leave thermal (return False) - stronger lift ahead
        - If prediction <= threshold: Stay in thermal (return True) - current thermal is better

        Returns:
            True to stay in thermal, False to leave thermal
        """
        # if we are not in current thermal, return Fasle

        if flight_state.current_climb_m_s() <= 0.01:
            return False
        # Extract features
        features = self._extract_features(flight_state, aircraft_model)

        # Convert to tensor and add batch dimension
        features_tensor = torch.FloatTensor(features).unsqueeze(0)

        # Forward pass (no gradient computation needed for inference)
        with torch.no_grad():
            output = self.network(features_tensor)
            probability = output.item()
        # print(f"Probability: {probability}, threshold: {self.threshold},")

        # Decision logic:
        # Network predicts: "Will we find stronger lift if we leave?"
        # If probability > threshold: Yes, stronger lift ahead -> Leave thermal (return False)
        # If probability <= threshold: No, stay in current thermal (return True)
        return probability <= self.threshold

    def get_hash(self) -> str:
        """Generate hash including threshold for uniqueness."""
        hash_string = f"{self.policy_name}_{self.threshold}"
        return hashlib.sha256(hash_string.encode()).hexdigest()

    def train(
        self,
        X: np.ndarray,
        y: np.ndarray,
        epoch_count,
        lr: float,
    ) -> None:
        """Train model."""
        X_tensor = torch.FloatTensor(X)
        y_tensor = torch.FloatTensor(y).unsqueeze(
            1
        )  # Reshape to [batch_size, 1] to match output shape
        self.network.train()
        optimizer = torch.optim.Adam(self.network.parameters(), lr=lr)
        criterion = torch.nn.BCELoss()
        list_loss = []
        for _ in tqdm(range(epoch_count)):
            optimizer.zero_grad()
            output = self.network(X_tensor)
            loss = criterion(output, y_tensor)
            loss.backward()
            optimizer.step()
            list_loss.append(loss.item())
        self.network.eval()
        # plot loss function
        import matplotlib.pyplot as plt  # pyright: ignore[reportMissingImports]

        plt.plot(list_loss)
        plt.xlabel("Epoch")
        plt.ylabel("Loss")
        plt.title("Loss Function")
        plt.show()



def train_rl(
        self,
        model_id:str,
        policy,
        simulator,
        rollout_count:int,
        simulations_per_rollout:int,
        epochs_per_rollout: int,
        learning_rate: float,
    ) -> None:
        """Train model."""
        for rollout_idx in range(rollout_count):
            simulation_results = simulator.simulate(policy, simulations_per_rollout)
            input_matrix, output_matrix = policy.convert_to_matrixes(simulation_results)

            input__tensor = torch.FloatTensor(input_matrix)
            output_tensor = torch.FloatTensor(output_matrix)
            policy.network.train()
            optimizer = torch.optim.Adam(self.network.parameters(), lr=learning_rate)
            criterion = torch.nn.BCELoss()
            list_loss = []
            for _ in tqdm(range(epochs_per_rollout)):
                optimizer.zero_grad()
                output = self.network(input__tensor)
                loss = criterion(output, output_tensor)
                loss.backward()
                optimizer.step()
                list_loss.append(loss.item())
            self.network.eval()
            # plot loss function
            import matplotlib.pyplot as plt  # pyright: ignore[reportMissingImports]

            plt.plot(list_loss)
            plt.xlabel("Epoch")
            plt.ylabel("Loss")
            plt.title("Loss Function")
            plt.show()

    def save(self) -> None:
        """Save model."""
        print(f"Saving model to {self.model_path}")
        # make sure partent dir exists
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        # save model
        torch.save(self.network.state_dict(), self.model_path)
        print(f"Model saved to {self.model_path}")
