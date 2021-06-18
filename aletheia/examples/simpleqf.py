from mesa import Model
from aletheia.mechanism_engine.scheduler import RandomActivation
from mesa.datacollection import  DataCollector
from mesa.space import Grid
from aletheia.mechanism_engine.predict_markets.lmsr import LMSRMarket
from aletheia.mechanism_engine.qf import QuadraticFunding
# from .agents.randomagent import RandomAgent
from aletheia.examples.agents.randomagent import RandomAgent


class QFModel(Model):
    def __init__(self):
        self.qf = QuadraticFunding()
        self.schedule = RandomActivation(self)
        # todo add agents
        for i in range(10):
            agent = RandomAgent(i, self, 10)
            self.schedule.add(agent)

        self.projects = range(1, 10)
        self.dead_line = 13
        self.count = 0
        self.running = True

    def step(self):
        self.schedule.step()
        
        if self.count >= self.dead_line:
            self.running = False

        self.count += 1
        self.show()
        
    def show(self):
        result = self.qf.clr_calcs()
        print(result)
        

def evaluate(model):
    pass


if __name__ == '__main__':
    qfmodel = QFModel()
    while qfmodel.running:
        qfmodel.step()
    # qfmodel.show()