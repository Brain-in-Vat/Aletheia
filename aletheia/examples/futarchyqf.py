from mesa import Model
from aletheia.mechanism_engine.scheduler import RandomActivation
from mesa.datacollection import DataCollector
from mesa.space import Grid
from aletheia.mechanism_engine.predict_markets.lmsr import LMSRMarket
from aletheia.mechanism_engine.qf import QuadraticFunding
from aletheia.mechanism_engine.qf_futarchy import  QFFutarchy
from aletheia.examples.agents.randomagent import RandomAgent, FixZLAgent
from aletheia.scenario_search.ga import GA
from aletheia.scenario_search.losspool import qf_loss, futarchy_loss

class QFFutarchyModel(Model):
    def __init__(self, projects_num = 10, beliefs=[], tokens=[], pass_ratio=0.9):
        # self.qf = QuadraticFunding()
        self.schedule = RandomActivation(self)
        # todo add agents
        agent_ids = range(len(beliefs))
        for agent_id, belief, token in zip(agent_ids, beliefs, tokens):
            # agent = RandomAgent(i, self, 10)
            agent = FixZLAgent(agent_id, self, token, belief)
            self.schedule.add(agent)
       
        self.projects = range(0, projects_num)
        self.dead_line = 13
        self.count = 0
        self.running = True
        self.qf_futarchy = QFFutarchy(pass_ratio=pass_ratio, projects = self.projects)
        self.results = []
        
    def step(self):
        self.schedule.step()
        
        result = self.qf_futarchy.finish_round()
        self.results.append(result)

        if self.count >= self.dead_line:
            self.running = False
        self.count += 1
        

def evaluate(code, agent_number=10):
    '''
    code = [1, 2, 10..]
    '''
    project_number = max(code[:agent_number])
    beliefs = code[agent_number: agent_number * 2]
    tmp = []
    for belief in beliefs:
        tmp_belief = {i:0 for i in range(project_number)}
        tmp_belief[belief] = 1
        tmp.append(tmp_belief)
        
    tokens = code[agent_number*2: agent_number*3]

    qffutarchyModel = QFFutarchyModel(project_number, tmp, tokens)
    while qffutarchyModel.running:
        qffutarchyModel.step()   
        
    # compute loss
    results = qffutarchyModel.results
    print(results)
    # expect = []
    # tmp = {}
    # for belief in beliefs:
    #     if belief not in tmp.keys():
    #         tmp[belief] = 1
    #     else:
    #         tmp[belief] += 1
    # beliefs = [(k,v) for k,v in tmp.items()]
    # beliefs = sorted(beliefs, key=lambda x: x[1], reverse=True)
    # beliefs = beliefs[: int(len(beliefs) * 0.9)]
    # expect = [belief[0] for belief in beliefs]

    


if __name__ == '__main__':
    # qffutarchyModel = QFFutarchyModel()
    # while qffutarchyModel.running:
    #     qffutarchyModel.step()
    evaluate([1]*30, 10)