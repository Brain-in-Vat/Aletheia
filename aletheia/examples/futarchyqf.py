from aletheia.scenario_search.loss import belief_loss, token_loss
from mesa import Model
from aletheia.mechanism_engine.scheduler import RandomActivation
from mesa.datacollection import DataCollector
from mesa.space import Grid
from aletheia.mechanism_engine.predict_markets.lmsr import LMSRMarket
from aletheia.mechanism_engine.qf import QuadraticFunding
from aletheia.mechanism_engine.qf_futarchy import QFFutarchy
from aletheia.examples.agents.randomagent import RandomAgent, FixZLAgent
from aletheia.scenario_search.ga import GA
from aletheia.scenario_search.losspool import qf_loss, futarchy_loss
from aletheia.settings import BASE_DIR
import os


class QFFutarchyModel(Model):
    def __init__(self, projects_num=10, beliefs=[], tokens=[], pass_ratio=0.9):
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
        self.qf_futarchy = QFFutarchy(
            pass_ratio=pass_ratio, projects=self.projects)
        self.results = []

    def step(self):
        for i in range(14):
            self.schedule.step()

        result = self.qf_futarchy.finish_round()
        self.results.append(result)

        award_vote_winner = result.get('award_vote_winner')
        if award_vote_winner:
            for k, v in award_vote_winner.items():
                self.schedule.agents[k].award_token(v)

        award_predict_winner = result.get('award_predict_winner')
        if award_predict_winner:
            for k, v in award_predict_winner.items():
                self.schedule.agents[k].award_brain_token(v)

        if self.count >= self.dead_line:
            self.running = False
        self.count += 1


def evaluate(code, agent_number=10, project_number=5):
    '''
    code = [1, 2, 10..]
    '''
    # project_number = max(code[:agent_number])
    origin_beliefs = code[0: agent_number]
    beliefs = origin_beliefs
    tmp = []
    for belief in beliefs:
        tmp_belief = {i: 0 for i in range(project_number)}
        tmp_belief[belief] = 1
        tmp.append(tmp_belief)

    tokens = code[agent_number: agent_number * 2]

    qffutarchyModel = QFFutarchyModel(project_number, tmp, tokens)
    while qffutarchyModel.running:
        qffutarchyModel.step()

    # compute loss
    expect = []
    tmp = {}
    for belief in beliefs:
        if belief not in tmp.keys():
            tmp[belief] = 1
        else:
            tmp[belief] += 1
    beliefs = [(k, v) for k, v in tmp.items()]
    beliefs = sorted(beliefs, key=lambda x: x[1], reverse=True)
    beliefs = beliefs[: int((project_number + 1) * 0.9)]
    expect = [belief[0] for belief in beliefs]

    results = qffutarchyModel.results
    # print(results)
    avg_qf_loss = 0
    for result in results:
        qf_result = result['cls_grants']
        qf_result = [x['id'] for x in qf_result]
        qf_loss = belief_loss(expect, qf_result)
        avg_qf_loss += qf_loss
    avg_qf_loss = avg_qf_loss/len(results)

    truth_index = []
    false_index = []
    for index, belief in enumerate(origin_beliefs):
        if belief in expect:
            truth_index.append(index)
        else:
            false_index.append(index)

    agents = qffutarchyModel.schedule.agents

    origin = tokens
    after = [
        a.token + a.brain_token for a in agents
    ]

    token_changed = [t2 - t1 for t1, t2 in zip(origin, after)]

    value2 = token_loss(origin, after, truth_index, false_index)
    loss_metric = {
        'grant_loss': avg_qf_loss,
        'token_loss': value2
    }
    return avg_qf_loss + 0.05 * value2, {'results': results, 'token_changed': token_changed, 'loss_metric': loss_metric}


def compute_experiment(result_path='result.json'):
    agent_number = 10
    project_number = 5
    run = GA(
        popsize=100,
        bound={(0, agent_number): (0, project_number),
               (agent_number, 2*agent_number): (0, 200)},
        evaluate=evaluate,
        result_path=os.path.join(BASE_DIR, 'tmp', result_path),
        NGEN=100,
        CXPB=0.8,
        MUTPB=0.4
    )
    run.GA_main()


if __name__ == '__main__':
    compute_experiment('result2.json')
