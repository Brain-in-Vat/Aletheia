from enum import Enum

class BaseSystem(object):
    def __init__(self, states, governance):
        self.states = states
        self.governance = governance

    def update(self):
        pass


class FutarchySystem(BaseSystem):
    """the origin futarchy system
    """

    def __init__(self, forum=None):
        self.failed_proposals = []
        self.activate_proposals = []
        self.passed_proposals = []
        self.forum = forum

    def update(self):
        """
        update the system time to t + 1
        """
        pass

    def observe(self, agent_id):
        """
        observe from the agent
        """
        pass

    def propose(self, proposal, agent):
        pass


class SimpleFutarchySystem(FutarchySystem):
    def __init__(self, forum=None, predict_market=None, duration=14):
        super().__init__(forum)
        self.predict_market = predict_market
        self.orders = []
        self.time_stick = 0
        self.day = 0
        self.duration = duration
        # self.vote_actions = {
        #     'yes': [],
        #     'no': []
        # }
        self.vote_actions = {}
        self.voted_agents = set()

    def update(self):
        self.time_stick += 1

    def propose(self, proposal):
        proposal.time = self.day
        self.activate_proposals.append(proposal)
        self.predict_market.submit(-1, proposal)
        self.vote_actions[proposal._id] = {
            'yes': [],
            'no': []
        }

    def vote(self, agent, proposal_id, vote_type):
        if agent.unique_id in self.voted_agents or agent.token < 1:
            return
        vote_action = self.vote_actions[proposal_id]
        if vote_type == 'yes':
            vote_action['yes'].append((agent.unique_id, agent.token))
        elif vote_type == 'no':
            vote_action['no'].append((agent.unique_id, agent.token))
        self.voted_agents.add(agent.unique_id)

    def step(self):
        # self.time_stick += 1
        # self.day = int(self.time_stick/24)
        self.day += 1
        remove_list = []
        for proposal in self.activate_proposals:
            if self.day - proposal.time >= self.duration:
                # self.activate_proposals.remove(proposal)
                # remove_list.append(proposal)
                vote_action = self.vote_actions[proposal._id]

                yes_amount = sum(x[1] for x in vote_action['yes'])
                no_amount = sum(x[1] for x in vote_action['no'])

                if yes_amount > no_amount:
                    proposal.state = 2
                    self.passed_proposals.append(proposal)
                else:
                    proposal.state = 3
                    self.failed_proposals.append(proposal)

        for proposal in remove_list:
            self.activate_proposals.remove(proposal)

    def observe(self, agent):
        return self.activate_proposals

