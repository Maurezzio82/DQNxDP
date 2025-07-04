# Test environment for the network trained for the swing up task

from SwingUpPendulumEnvDQL import SwingUpPendulum
import matplotlib.pyplot as plt
import numpy as np

import torch
import torch.nn as nn
import torch.nn.functional as F

# This function is only for the purposes of having the angle
# value go from 0 to 2pi instead of from -pi to pi
def wrap_to_2pi(theta):
    return theta % (2 * np.pi)

class DQN(nn.Module):

    def __init__(self, n_observations, n_actions, n_l1 = 256, n_l2 = 128):
        super(DQN, self).__init__()
        self.layer1 = nn.Linear(n_observations, n_l1)
        self.layer2 = nn.Linear(n_l1, n_l2)
        self.layer3 = nn.Linear(n_l2, n_actions)

    # Called with either one element to determine next action, or a batch
    # during optimization. Returns tensor([[left0exp,right0exp]...]).
    def forward(self, x):
        x = F.relu(self.layer1(x))
        x = F.relu(self.layer2(x))
        return self.layer3(x)
    

name = input("Enter network name:\n")
PATH = "Trained_Networks/" + name + ".pth"

Q_net = torch.load(PATH, weights_only=False)
env = SwingUpPendulum()

import time

# Load the trained model (assuming Q_net is already trained)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Create the environment
state, _ = env.reset()

# Convert state to tensor
state = torch.tensor(state, dtype=torch.float32, device=device).unsqueeze(0)


thetas = []
theta_dots = []
torques = []

# Run a test episode
done = False
sim_max_it = env.max_it
it = 0

print('Simulating...')
while not done and it < sim_max_it:
    it += 1
    with torch.no_grad():  # No gradient needed for testing
        action = Q_net(state).max(1).indices.view(1, 1).item()

    # Take action
    next_state, reward, terminated, truncated, _ = env.step(action)

    # Update state
    state = torch.tensor(next_state, dtype=torch.float32, device=device).unsqueeze(0)
    
    #save states and actions for plotting
    thetas.append(wrap_to_2pi(env.state[0]))
    theta_dots.append(env.state[1])
    torques.append(env.valid_actions[action]/10)

    # Render environment
    time.sleep(0.02)  # Small delay to slow down rendering
    
    # Check if episode is over
    done = terminated or truncated
print('Simulation completed')

plt.figure(figsize=(10, 4))
plt.plot(thetas, label='θ')
plt.plot(theta_dots, label='ω')
plt.plot(torques, label = 'τ=u')
plt.xlabel('Time step')
plt.ylabel('State value')
plt.title('State Variables Over Time')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
