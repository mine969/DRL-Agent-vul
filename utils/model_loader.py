"""
Utility functions for loading trained models and checkpoints
"""

import torch
import glob
import re
import os


def find_latest_checkpoint(checkpoint_dir="checkpoints", pattern="improved_mock_*.pth"):
    """
    Find the checkpoint with the highest episode number.

    Args:
        checkpoint_dir: Directory containing checkpoints
        pattern: Glob pattern for checkpoint files

    Returns:
        tuple: (episode_number, checkpoint_path) or (0, None) if no checkpoints found
    """
    checkpoint_pattern = os.path.join(checkpoint_dir, pattern)
    checkpoints = glob.glob(checkpoint_pattern)

    if not checkpoints:
        return 0, None

    latest_ep = 0
    latest_path = None

    for cp in checkpoints:
        try:
            # Match ep{number} in the filename
            match = re.search(r"ep(\d+)", cp)
            if match:
                ep = int(match.group(1))
                if ep > latest_ep:
                    latest_ep = ep
                    latest_path = cp
        except:
            continue

    return latest_ep, latest_path


def load_model_smart(
    agent, model_path="dqn_web_sec_model.pth", auto_checkpoint=True, verbose=True
):
    """
    Smart model loading: tries latest checkpoint first, then falls back to base model.

    Args:
        agent: DQNAgent instance to load weights into
        model_path: Path to base model (fallback)
        auto_checkpoint: If True, try to load latest checkpoint first
        verbose: Print loading messages

    Returns:
        int: Episode number loaded from (0 if base model or fresh start)
    """
    device = torch.device(
        "cuda"
        if torch.cuda.is_available()
        else "mps" if torch.backends.mps.is_available() else "cpu"
    )

    # Try latest checkpoint first
    if auto_checkpoint:
        latest_ep, checkpoint_path = find_latest_checkpoint()
        if latest_ep > 0 and checkpoint_path:
            try:
                # Support both brain (DQNAgent) and q_network (ImprovedDQNAgent)
                network = getattr(agent, "brain", None) or getattr(
                    agent, "q_network", None
                )
                if network is None:
                    raise AttributeError(
                        "Agent has no recognizable brain or q_network attribute"
                    )

                checkpoint = torch.load(checkpoint_path, map_location=device)

                # Unwrap checkpoint if necessary
                state_dict = checkpoint
                if isinstance(checkpoint, dict):
                    if "q_network_state_dict" in checkpoint:
                        state_dict = checkpoint["q_network_state_dict"]
                    elif "model_state_dict" in checkpoint:
                        state_dict = checkpoint["model_state_dict"]
                    elif "brain_state_dict" in checkpoint:
                        state_dict = checkpoint["brain_state_dict"]

                network.load_state_dict(state_dict)

                # Support target_brain (DQNAgent) and target_network (ImprovedDQNAgent)
                target_network = getattr(agent, "target_brain", None) or getattr(
                    agent, "target_network", None
                )
                if target_network:
                    target_network.load_state_dict(network.state_dict())

                if verbose:
                    print(f"Loaded latest checkpoint: Episode {latest_ep}")
                    print(f"File: {checkpoint_path}")
                return latest_ep
            except Exception as e:
                if verbose:
                    print(f"Failed to load checkpoint {checkpoint_path}: {e}")
                    print(f"   Falling back to base model...")

    # Fallback to base model
    try:
        network = getattr(agent, "brain", None) or getattr(agent, "q_network", None)
        if network is None:
            raise AttributeError(
                "Agent has no recognizable brain or q_network attribute"
            )

        network.load_state_dict(torch.load(model_path, map_location=device))

        target_network = getattr(agent, "target_brain", None) or getattr(
            agent, "target_network", None
        )
        if target_network:
            target_network.load_state_dict(network.state_dict())

        if verbose:
            print(f"Loaded base model: {model_path}")
        return 0
    except Exception as e:
        if verbose:
            print(f"❌ Failed to load model {model_path}: {e}")
            print(f"No model found. Starting fresh.")
        return 0


def get_best_model_path(prefer_checkpoint=True):
    """
    Get the best model path to use (latest checkpoint or base model).

    Args:
        prefer_checkpoint: If True, prefer latest checkpoint over base model

    Returns:
        str: Path to the best model to use
    """
    if prefer_checkpoint:
        latest_ep, checkpoint_path = find_latest_checkpoint()
        if latest_ep > 0 and checkpoint_path:
            return checkpoint_path

    return "dqn_web_sec_model.pth"
