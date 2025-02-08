import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from threading import Thread
import time
from collections import deque
import logging

# Configure logging for better debugging and monitoring
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants for the simulation
G = 1.0  # Gravitational constant
dt = 0.01  # Time step
num_steps = 10000  # Number of simulation steps
agent_states = {}
missions = deque()

class Agent:
    def __init__(self, name, role, capabilities):
        self.name = name
        self.role = role
        self.capabilities = capabilities
        self.memory = deque(maxlen=1000)  # Limit memory size to avoid excessive growth
        self.position = np.random.uniform(-2, 2, 2)
        self.velocity = np.zeros(2)

    def update(self, other_agents):
        if "manipulate_gravity" in self.capabilities and np.random.random() < 0.1:
            global G
            G += np.random.uniform(-0.05, 0.05)  # Randomly adjust gravity
        force = self._calculate_force(other_agents)
        self.velocity += force * dt
        self.position += self.velocity * dt
        self.memory.append((self.position.copy(), self.velocity.copy()))

    def _calculate_force(self, other_agents):
        force = np.zeros(2)
        for agent in other_agents:
            if agent != self:
                distance_vector = agent.position - self.position
                distance = np.linalg.norm(distance_vector)
                if distance > 1e-6:  # Avoid division by zero
                    force += G * distance_vector / (distance ** 3)
        return force

class Simulation:
    def __init__(self):
        self.agents = [
            Agent("Seraph", "Leader", ["manipulate_gravity", "spawn_entity"]),
            Agent("Echo", "Explorer", ["observe", "report"]),
            Agent("Nova", "Builder", ["construct", "stabilize"])
        ]
        self.fig, self.ax = plt.subplots()
        self.lines = [self.ax.plot([], [], label=agent.name)[0] for agent in self.agents]
        self.ax.set_xlim(-5, 5)
        self.ax.set_ylim(-5, 5)
        self.ax.legend()
        self.ax.set_title("Agent Simulation")

    def run(self):
        self.animation = FuncAnimation(self.fig, self.update_plot, frames=None, interval=int(dt * 1000), blit=True)
        plt.show()

    def update_plot(self, i):
        for agent in self.agents:
            agent.update([a for a in self.agents if a != agent])
        self.execute_missions()
        for line, agent in zip(self.lines, self.agents):
            positions, _ = zip(*agent.memory)
            if positions:
                x, y = zip(*positions)
                line.set_data(x, y)
        return self.lines

    def execute_missions(self):
        if missions:
            mission = missions.popleft()
            if mission['type'] == 'change_gravity':
                global G
                G = mission['new_value']
                logger.info(f"Changed gravity to {G}")
            elif mission['type'] == 'spawn_entity':
                new_agent = Agent(mission['name'], "Newbie", ["observe"])
                self.agents.append(new_agent)
                self.lines.append(self.ax.plot([], [], label=new_agent.name)[0])
                self.ax.legend()
                logger.info(f"New agent {new_agent.name} spawned")

def community_mission():
    while True:
        mission = {
            'type': 'change_gravity',
            'new_value': np.random.uniform(0.5, 1.5)
        }
        missions.append(mission)
        time.sleep(np.random.uniform(5, 15))  # Random wait time between missions

if __name__ == "__main__":
    sim = Simulation()
    Thread(target=sim.run, daemon=True).start()
    Thread(target=community_mission, daemon=True).start()
