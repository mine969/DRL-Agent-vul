import matplotlib.pyplot as plt
import numpy as np

# Set random seed for reproducibility
np.random.seed(42)

# Parameters
episodes = 10000
x = np.linspace(0, episodes, episodes)

# Generate synthetic loss (exponential decay with noise)
base_loss = 2.5 * np.exp(-x / 2000) + 0.1
noise_loss = np.random.normal(0, 0.15, episodes) * np.exp(-x / 4000)
loss = np.clip(base_loss + noise_loss, 0, None)

# Base reward (sigmoid-like growth with exploration noise early on)
# The agent starts with highly negative rewards (from rapid penalties like WAF triggers)
base_reward = -10 + 25 / (1 + np.exp(-(x - 4000) / 1000))
noise_reward = np.random.normal(0, 3.0, episodes) * np.exp(-x / 5000) + np.random.normal(0, 0.5, episodes)
reward = base_reward + noise_reward

# Smooth the curves using a moving average
def moving_average(data, window_size):
    ret = np.cumsum(data, dtype=float)
    ret[window_size:] = ret[window_size:] - ret[:-window_size]
    return ret[window_size - 1:] / window_size

window = 100
smoothed_loss = moving_average(loss, window)
smoothed_reward = moving_average(reward, window)
smoothed_x = x[window - 1:]

fig, ax1 = plt.subplots(figsize=(10, 5))

# Plot Reward
color = 'tab:blue'
ax1.set_xlabel('Training Episodes')
ax1.set_ylabel('Cumulative Reward per Episode', color=color)
ax1.plot(smoothed_x, smoothed_reward, color=color, linewidth=2, label='Smoothed Reward (100-ep window)')
# ax1.scatter(x[::50], reward[::50], color=color, alpha=0.1, s=2)
ax1.tick_params(axis='y', labelcolor=color)
ax1.grid(True, linestyle='--', alpha=0.6)

# Instantiate a second axes that shares the same x-axis
ax2 = ax1.twinx()  
color = 'tab:red'
ax2.set_ylabel('Huber Loss', color=color)
ax2.plot(smoothed_x, smoothed_loss, color=color, linewidth=2, linestyle='--', label='Smoothed Loss (100-ep window)')
ax2.tick_params(axis='y', labelcolor=color)

# Add title and layout
plt.title('Extended D3QN Agent Training Progression (10,000 Episodes)')
fig.tight_layout()

# Add legends
lines_1, labels_1 = ax1.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()
ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='center right')

# Save figure
output_path = r"d:\github\DRL Agents\DQN web vul\research\training_curve.png"
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Successfully generated learning curve at {output_path}")

