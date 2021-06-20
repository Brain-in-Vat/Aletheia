from mesa import Model
from aletheia.mechanism_engine.scheduler import RandomActivation
from mesa.datacollection import  DataCollector
from mesa.space import Grid
from aletheia.mechanism_engine.predict_markets.lmsr import LMSRMarket
from aletheia.mechanism_engine.qf import QuadraticFunding
# from .agents.randomagent import RandomAgent
from aletheia.examples.agents.randomagent import FixZLAgent, RandomAgent


class QFModel(Model):
    def __init__(self, project_num = 10, beliefs=[], tokens=[], pass_ratio=0.9):
        self.qf = QuadraticFunding()
        self.schedule = RandomActivation(self)
        agent_ids = range(len(beliefs))
        # todo add agents
        for agent_id, belief,  token in zip(agent_ids, beliefs, tokens):
            agent = FixZLAgent(agent_id, self, token, belief)
            self.schedule.add(agent)

        # for i in range(10):
        #     agent = RandomAgent(i, self, 10)
        #     self.schedule.add(agent)

        self.projects = range(0, project_num)
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
        

def evaluate(code, agent_number=10, project_number=10):
    '''
    code = [1, 2, 10..]
    '''
    origin_beliefs = code[0, agent_number]
    beliefs = origin_beliefs

    tmp = []
    for belief in beliefs:
        tmp_belief = {i:0 for i in range(project_number)}
        tmp_belief[belief] = 1
        tmp.append(tmp_belief)
        
    tokens = code[agent_number : agent_number * 2]
    qfmodel = QFModel()
    while qfmodel.running:
        qfmodel.step()



if __name__ == '__main__':
    qfmodel = QFModel()
    while qfmodel.running:
        qfmodel.step()
    # qfmodel.show()