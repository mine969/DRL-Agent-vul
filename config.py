"""
Configuration Management
========================

Centralized configuration for the DRL Web Vulnerability Scanner.
All configuration options are defined here for easy modification and maintenance.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict
import os
from pathlib import Path


@dataclass
class AgentConfig:
    """DQN Agent configuration parameters."""

    state_dim: int = 15
    action_dim: int = 50  # UPDATED: Mock targets restricted space (was 100/150)
    action_dim_full: int = 150  # Full action space for general targets
    learning_rate: float = 0.0001
    gamma: float = 0.99
    epsilon_start: float = 1.0
    epsilon_end: float = 0.01
    epsilon_decay: float = 0.995
    memory_size: int = 100000
    batch_size: int = 64  # REDUCED: 4096 -> 64 for stability
    target_update_frequency: int = 100
    device: str = "auto"  # Let torch decide based on availability

    # Neural Network Architecture
    hidden_sizes: List[int] = None

    def __post_init__(self):
        if self.hidden_sizes is None:
            self.hidden_sizes = [256, 128]  # Simplified for 11-dim state space


@dataclass
class TrainingConfig:
    """Training configuration parameters."""

    max_episodes: int = 10000
    max_steps_per_episode: int = 50  # UPDATED: Reduced from 100 for faster episodes
    checkpoint_frequency: int = 50  # UPDATED: Save every 50 episodes (was 10/100)
    checkpoint_dir: str = "checkpoints"
    log_frequency: int = 10
    save_best_model: bool = True

    # Phase-based learning
    enable_phase_progression: bool = True
    actions_per_phase_unlock: int = 5

    # Reward shaping (NORMALIZED for DQN Stability [-1, 1])
    base_reward: float = -0.01  # Cost of time
    vulnerability_reward: float = 1.0  # Confirmed exploit
    api_discovery_reward: float = 0.1  # Discovery
    auth_bypass_reward: float = 2.0  # High value exploit
    ctf_flag_reward: float = 5.0  # Ultimate goal
    phase_bonus: float = 0.1  # Small shaping bonus
    phase_completion_bonus: float = 0.2
    phase_skip_penalty: float = -0.05
    waf_penalty: float = -0.1
    rate_limit_penalty: float = -0.1
    juice_shop_penalty: float = -0.05


@dataclass
class EnvironmentConfig:
    """Environment configuration parameters."""

    default_target_url: str = "http://localhost:5001"
    timeout: int = 10
    max_retries: int = 3
    retry_backoff: float = 1.5

    # Target applications
    mock_targets: Dict[str, Dict[str, any]] = None

    def __post_init__(self):
        if self.mock_targets is None:
            self.mock_targets = {
                "ecommerce": {
                    "name": "E-Commerce Platform",
                    "script": "env/target_app_ecommerce.py",
                    "port": 5002,
                    "url": "http://localhost:5002",
                },
                "social": {
                    "name": "Social Media Platform",
                    "script": "env/target_app_social.py",
                    "port": 5003,
                    "url": "http://localhost:5003",
                },
                "banking": {
                    "name": "Banking Application",
                    "script": "env/target_app_banking.py",
                    "port": 5004,
                    "url": "http://localhost:5004",
                },
                "blog": {
                    "name": "Blog Platform",
                    "script": "env/target_app_blog.py",
                    "port": 5005,
                    "url": "http://localhost:5005",
                },
                "fileshare": {
                    "name": "File Sharing Platform",
                    "script": "env/target_app_fileshare.py",
                    "port": 5006,
                    "url": "http://localhost:5006",
                },
            }


@dataclass
class ScanConfig:
    """Autonomous scanning configuration."""

    crawl_depth: int = 30
    max_urls: int = 1000
    intensity: int = 3  # 1-5 scale
    stealth_level: str = "medium"  # low, medium, high, paranoid

    # Stealth settings
    use_proxies: bool = False
    proxy_list_file: str = "proxies.txt"
    request_delay: float = 1.0
    randomize_user_agent: bool = True

    # Scan modes
    modes: Dict[str, Dict[str, any]] = None

    def __post_init__(self):
        if self.modes is None:
            self.modes = {
                "auto": {
                    "crawl_depth_multiplier": 1.0,
                    "intensity_multiplier": 1.0,
                    "request_delay": 1.0,
                },
                "aggressive": {
                    "crawl_depth_multiplier": 1.5,
                    "intensity_multiplier": 2.0,
                    "request_delay": 0.5,
                },
                "osint": {
                    "crawl_depth_multiplier": 1.0,
                    "intensity_multiplier": 0.0,  # No attacks
                    "request_delay": 2.0,
                },
                "specific": {
                    "crawl_depth_multiplier": 1.0,
                    "intensity_multiplier": 1.0,
                    "request_delay": 1.0,
                },
            }


@dataclass
class ReportConfig:
    """Report generation configuration."""

    output_dir: str = "reports"
    formats: List[str] = None
    include_exploit_steps: bool = True
    include_remediation: bool = True
    include_cvss: bool = True
    severity_levels: List[str] = None

    def __post_init__(self):
        if self.formats is None:
            self.formats = ["markdown", "html"]
        if self.severity_levels is None:
            self.severity_levels = ["Critical", "High", "Medium", "Low", "Info"]


@dataclass
class ProjectConfig:
    """Main project configuration combining all sub-configs."""

    agent: AgentConfig = None
    training: TrainingConfig = None
    environment: EnvironmentConfig = None
    scan: ScanConfig = None
    report: ReportConfig = None

    # Paths
    project_root: Path = None
    data_dir: Path = None
    logs_dir: Path = None

    def __post_init__(self):
        if self.agent is None:
            self.agent = AgentConfig()
        if self.training is None:
            self.training = TrainingConfig()
        if self.environment is None:
            self.environment = EnvironmentConfig()
        if self.scan is None:
            self.scan = ScanConfig()
        if self.report is None:
            self.report = ReportConfig()

        # Setup paths
        if self.project_root is None:
            self.project_root = Path(__file__).parent.resolve()

        if self.data_dir is None:
            self.data_dir = self.project_root / "data"
            self.data_dir.mkdir(exist_ok=True)

        if self.logs_dir is None:
            self.logs_dir = self.project_root / "logs"
            self.logs_dir.mkdir(exist_ok=True)

        # Ensure checkpoint directory exists
        checkpoint_dir = self.project_root / self.training.checkpoint_dir
        checkpoint_dir.mkdir(exist_ok=True)

        # Ensure report directory exists
        report_dir = self.project_root / self.report.output_dir
        report_dir.mkdir(exist_ok=True)


# Global configuration instance
config = ProjectConfig()


def get_config() -> ProjectConfig:
    """Get the global configuration instance."""
    return config


def load_config_from_env() -> ProjectConfig:
    """Load configuration from environment variables."""
    cfg = ProjectConfig()

    # Agent config from env
    if os.getenv("AGENT_LEARNING_RATE"):
        cfg.agent.learning_rate = float(os.getenv("AGENT_LEARNING_RATE"))
    if os.getenv("AGENT_BATCH_SIZE"):
        cfg.agent.batch_size = int(os.getenv("AGENT_BATCH_SIZE"))

    # Training config from env
    if os.getenv("MAX_EPISODES"):
        cfg.training.max_episodes = int(os.getenv("MAX_EPISODES"))
    if os.getenv("CHECKPOINT_FREQUENCY"):
        cfg.training.checkpoint_frequency = int(os.getenv("CHECKPOINT_FREQUENCY"))

    # Scan config from env
    if os.getenv("CRAWL_DEPTH"):
        cfg.scan.crawl_depth = int(os.getenv("CRAWL_DEPTH"))
    if os.getenv("SCAN_INTENSITY"):
        cfg.scan.intensity = int(os.getenv("SCAN_INTENSITY"))
    if os.getenv("STEALTH_LEVEL"):
        cfg.scan.stealth_level = os.getenv("STEALTH_LEVEL")

    return cfg
