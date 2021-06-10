"""to be down
"""
from mesa.time import BaseScheduler


class Scheduler(object):
    def __init__(self):
        self.agents = {}

    def setp(self):
        for agent in self.agents.values():
            agent.step()

    def add(self, agent):
        # self.agents.add(agent)
        self.agents[agent._id] = agent


class RandomActivation(BaseScheduler):
    """A scheduler which activates each agent once per step, in random order,
    with the order reshuffled every step.

    This is equivalent to the NetLogo 'ask agents...' and is generally the
    default behavior for an ABM.

    Assumes that all agents have a step(model) method.

    """

    def step(self) -> None:
        """Executes the step of all agents, one at a time, in
        random order.

        """
        for agent in self.agent_buffer(shuffled=True):
            agent.step()
        self.steps += 1
        self.time += 1
