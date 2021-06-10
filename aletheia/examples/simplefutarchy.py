from mesa import Model
from aletheia.mechanism_engine.scheduler import RandomActivation
from mesa.datacollection import DataCollector
from mesa.space import Grid
from aletheia.mechanism_engine.predict_markets.lmsr import LMSR
from aletheia.mechanism_engine.predict_markets.fpmm import FPMM
from aletheia.mechanism_engine.futarchy.proposal import Proposal, FutarchyProposal, FPMMProposal
from aletheia.mechanism_engine.futarchy import SimpleFutarchySystem
from aletheia.agents.simpleagent import FutarchyBuyAgent, FutarchyBuyAndSellAgent, FutarchyRandomAgent
import random

class Futarchy(Model):
    """
    """

    def __init__(self, b_number, agent_number, kind1, kind2, kind3, times_per_day, fee=0.2, belief_rate=0.6, amm='lmsr') -> None:
        """
        """
        kinds = [kind1, kind2, kind3]
        # proposal = FutarchyProposal(None, 0, [], b_number)
        self.schedule = RandomActivation(self)
        if amm == 'lmsr':
            self.market = LMSR(fee=fee)
            proposal = FutarchyProposal(None, 0, [], b_number)
        else:
            self.market = FPMM(fee=fee, constant=100)
            proposal = FPMMProposal(None, 0, [], constant=100)
        self.current_proposal = proposal
        self.system = SimpleFutarchySystem(
            forum=None, predict_market=self.market)
        self.system.propose(proposal)
        self.grid = Grid(10, 10, torus=False)
        self.count = 0
        self.agent_numer = sum(kinds)
        self.times_per_day = times_per_day
        for i in range(0, 10):
            for j in range(0, 10):
                if j + i*10 < kinds[0]:
                    # agent = FutarchyRandomAgent(j+i*10, self, self.market, self.system, (i, j))
                    # agent = OntoAgent(None, j+i*10, self,
                    #                   self.market, self.system, (i, j), strategy=0)
                    if j+i*10 < kinds[0]*belief_rate:
                        agent = FutarchyBuyAgent(
                            j+i*10, self, self.market, self.system, (i, j), 1, token=2000)
                    else:
                        agent = FutarchyBuyAgent(
                            j+i*10, self, self.market, self.system, (i, j), 0.0, token=2000)

                    self.grid.place_agent(agent, (i, j))
                    self.schedule.add(agent)
                    # agent.set_proposal(proposal._id, 1.0)
                elif j + i*10 < kinds[0] + kinds[1]:
                    # agent = OntoAgent(None, j+i*10, self,
                    #                   self.market, self.system, (i, j), strategy=1)
                    if j + i*10 < kinds[0] + kinds[1]/3 + 1:
                        agent = FutarchyBuyAndSellAgent(
                            j+i*10, self, self.market, self.system, (i, j), 0.5, token=2000)
                    else:
                        agent = FutarchyBuyAndSellAgent(
                            j+i*10, self, self.market, self.system, (i, j), 0.5, token=2000)
                    self.grid.place_agent(agent, (i, j))
                    self.schedule.add(agent)
                    # agent.set_proposal(proposal._id, 0.0)

                elif j + i*10 < kinds[0] + kinds[1] + kinds[2]:
                    agent = FutarchyRandomAgent(
                        j+i*10, self, self.market, self.system, (i, j), token=2000)
                    self.grid.place_agent(agent, (i, j))
                    self.schedule.add(agent)
                else:
                    continue

        self.running = True
        self.datacollector = DataCollector(
            {
                "yes_token_price": lambda m: self.count_type(m, m.market, 'yes'),
                "no_token_price": lambda m: self.count_type(m, m.market, 'no')
            }
        )
        self.datacollector.collect(self)

        self.countcollector = DataCollector(
            {
                "vote_yes": lambda m: self.count_token(m, 'yes'),
                "vote_no": lambda m: self.count_token(m, 'no')
            }
        )
        self.countcollector.collect(self)

    def step(self):
        # self.schedule.agents
        # index = self.count % self.agent_numer
        for i in range(self.times_per_day):
            index = random.randint(0, self.agent_numer - 1)
            current_agent = self.schedule.agents[index]
            current_agent.step()
            # self.schedule.step()

        self.datacollector.collect(self)
        self.countcollector.collect(self)
        # if self.count % (12*self.agent_numer) == 0 and self.count > 0:
        self.system.step()
        if self.count >= 13:
            self.running = False
        self.count += 1

    @staticmethod
    def count_type(model, market, voter_condition):
        """
        """
        if not model.system.activate_proposals:
            return 0
        proposal = model.system.activate_proposals[0]
        if voter_condition == 'yes':

            # val = market.calc_price(proposal._id, 1, 0)
            # val = proposal.yes_token
            val = market.calc_current_price(proposal._id, 'yes')
        else:
            # val = market.calc_price(proposal._id, 0, 1)
            val = market.calc_current_price(proposal._id, 'no')
            # val = proposal.no_token
        return val

    @staticmethod
    def count_token(model, voter_condition):
        """

        """
        # system = model.system
        # proposal_idk= model.current_proposal._id
        # if voter_condition == 'yes':
        #     return len(system.vote_actions[proposal_id]['yes'])
        # else:
        #     return len(system.vote_actions[proposal_id]['no'])
        count = 0
        if voter_condition == 'yes':
            for voter in model.schedule.agents:
                count += voter.yes_token
        else:
            for voter in model.schedule.agents:
                count += voter.no_token
        return count