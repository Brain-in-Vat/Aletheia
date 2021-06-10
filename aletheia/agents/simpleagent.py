import math
from mesa import Agent, Model
import random

# class Agent(object):
#     def __init__(self, _id, position, states):
#         self._id = _id
#         self.position = position
#         self.states = states


class SpatialAgent(Agent):
    """ 
    A Spatial Vote agent
    agent with x,y represents it's opinion
    """

    def __init__(self, pos, model, system, forum, knowlege, _id=None):
        """
        create a new voter
        Args:
            pos: the opinon position
            model: the model 
            system: the simluated system
            forum: social concact net
            knowlege: knowlege represent of this agent
            _id: id
        each time, the agent will focus on one proposal
        """
        self.pos = pos
        self.model = model
        self.system = system
        self.forum = forum
        self._id = _id
        self.unique_id = _id
        self.knowlege = knowlege
        self.like_threshold = 0.7
        self.hate_threshold = 1
        self.condition = 'Unknown'

    def observe(self, system):
        # infos = system.observe(self)
        proposals = system.get_activate_proposals()
        favorite_proposal = None
        shortest_distance = 10000
        for proposal in proposals:
            if system.is_voted(self._id, proposal._id):
                continue
            else:
                dist = self.likes(proposal)
                if dist < shortest_distance:
                    shortest_distance = dist
                    favorite_proposal = proposal
        return favorite_proposal, dist

    def likes(self, proposal):
        x = self.pos
        y = proposal.pos
        sum_result = sum([math.pow(i-j, 2)for i, j in zip(x, y)])
        dist = math.sqrt(sum_result)
        return dist

    def think(self):
        """this step, agent try to reason his belief, intent
        """
        pass

    def check_intent(self):
        pass

    def update_intent(self):
        pass

    def check_plan(self):
        pass

    def execute_plan(self):
        """
        """
        def vote(amount):
            pass
        pass

    def step(self):
        print('voted')
        proposal, dist = self.observe(self.system)
        if proposal and dist < self.like_threshold:
            self.system.stack(0.1, self._id, proposal._id, 'yes')
            self.condition = 'Yes'
        elif proposal and dist > self.hate_threshold:
            self.system.stack(0.1, self._id, proposal._id, 'yes')
            self.condition = 'No'
        else:
            self.condition = 'Unknown'

    @property
    def x(self):
        return self.pos[0]

    @property
    def y(self):
        return self.pos[1]


class FutarchyRandomAgent(Agent):
    def __init__(self, unique_id: int, model: Model, market, system, pos, token=10) -> None:
        super().__init__(unique_id, model)
        self.unique_id = unique_id
        self.model = model
        self.market = market
        self.system = system
        self.token = token
        self.no_token = 0
        self.yes_token = 0
        self.pos = pos
        self.wealth = self.token
        self.voted = False
        self.belief = 0.5

    def set_type(self):
        self._type = 1

    def step(self) -> None:
        proposals = self.system.observe(self)
        if proposals:
            target = proposals[0]
        else:
            return
        dice = random.random()
        val = 0
        if dice < 0.25:
            price = self.market.calc_price(target._id, 1, 0)
            if price <= self.token:
                val = self.market.buy(
                    target._id, self.unique_id, 'yes_token', 1)
                self.yes_token += 1
                self.system.vote(self, target._id, 'yes')
                self.voted = True

        elif dice > 0.25 and dice < 0.5:
            if self.yes_token >= 1:
                val = self.market.sell(
                    target._id, self.unique_id, 'yes_token', 1)
                self.yes_token -= 1
        elif dice > 0.5 and dice < 0.75:

            if self.no_token >= 1:
                val = self.market.sell(
                    target._id, self.unique_id, 'no_token', 1)
                self.no_token -= 1
        elif dice > 0.75:
            price = self.market.calc_price(target._id, 0, 1)
            if price <= self.token:
                val = self.market.buy(
                    target._id, self.unique_id, 'no_token', 1)
                self.no_token += 1
            self.system.vote(self, target._id, 'no')
            self.voted = True

        self.token -= val
        self.wealth = self.token + self.no_token * self.market.calc_current_price(target._id, 'no') + \
            self.yes_token * self.market.calc_current_price(target._id, 'yes')
        # self.wealth = self.token + self.no_token * self.market.calc_price(target._id, 0, 1)
        # self.wealth = self.token + self.yes_token * self.market.calc_price(target._id, 1, 0)
        # return super().step()


class FutarchyBuyAgent(Agent):
    def __init__(self, unique_id: int, model: Model, market, system, pos, belief, join_time, token=10) -> None:
        super().__init__(unique_id, model)
        self.unique_id = unique_id
        self.model = model
        self.market = market
        self.system = system
        self.token = token
        self.no_token = 0
        self.yes_token = 0
        self.pos = pos
        self.wealth = self.token
        self.voted = False
        self.belief = belief
        self.join_time = join_time
        self.vote = 'unknown'
        self.init_token = token

    def set_type(self):
        self._type = 2
        pass

    def step(self):
        if self.system.day < self.join_time:
            return
        proposals = self.system.observe(self)
        if proposals:
            target = proposals[0]
        else:
            return

        def buy_yes_token(_id, amount):
            pay = self.market.calc_price(_id, amount, 0)
            pay = (1 + self.market.fee)*pay
            if pay <= self.token:
                val = self.market.buy(_id, self.unique_id, 'yes_token', amount)
                self.yes_token += amount
                self.token -= val

        def buy_no_token(_id, amount):
            price = self.market.calc_price(_id, 0, amount)
            price = (1 + self.market.fee)*price
            if price <= self.token:
                val = self.market.buy(_id, self.unique_id, 'no_token', amount)
                self.no_token += amount
                self.token -= val

        def sell_yes_token(_id, amount):
            if self.yes_token >= amount:
                val = self.market.sell(
                    _id, self.unique_id, 'yes_token', amount)
                self.yes_token -= amount
                self.token -= val

        def sell_no_token(_id, amount):
            if self.no_token >= amount:
                val = self.market.sell(_id, self.unique_id, 'no_token', amount)
                self.no_token -= amount
                self.token -= val

        def vote_yes(_id, amount=None):
            if not self.voted:
                self.system.vote(self, _id, 'yes')
                self.voted = True
                self.vote = 'yes'

        def vote_no(_id, amount=None):
            if not self.voted:
                self.system.vote(self, _id, 'no')
                self.voted = True
                self.vote = 'no'

        fee = self.market.fee
        yes_price = self.market.calc_current_price(target._id, 'yes')
        yes_cost = yes_price + yes_price*fee
        yes_sell = (1 - fee)*yes_price
        no_price = self.market.calc_current_price(target._id, 'no')
        no_cost = no_price + no_price*fee
        no_sell = (1-fee)*no_price
        if self.belief > 0.5:
            if yes_cost < self.belief:
                buy_yes_token(target._id, 1)
                # print('I amd {}, type buy, has token {},yes cost: {}, beleif: {}, action: buy yes'.format(
                #     self.unique_id, self.token, yes_cost, self.belief))

        elif self.belief < 0.5:

            if no_cost < 1 - self.belief:
                buy_no_token(target._id, 1)
        #         print('I am {}, type buy, has token {}, yes cost: {}, beleif: {}, action: buy no'.format(
        #             self.unique_id, self.token, no_cost, self.belief))

        # print('current prices yes: {}, no: {}'.format(self.market.calc_current_price(
        #     target._id, 'yes'), self.market.calc_current_price(target._id, 'no')))

        if self.belief > 0.5:
            vote_yes(target._id, 1)
        elif self.belief < 0.5:
            vote_no(target._id, 1)

        # self.token -= val
        self.wealth = self.token + self.no_token * self.market.calc_current_price(target._id, 'no') + \
            self.yes_token * self.market.calc_current_price(target._id, 'yes')
        # self.wealth = self.token + self.no_token * self.market.calc_price(target._id, 0, 1)
        # self.wealth = self.token + self.yes_token * self.market.calc_price(target._id, 1, 0)
        # return super().step()


class FutarchyBuyAndSellAgent(FutarchyBuyAgent):

    def set_type(self):
        self._type = 3

    def update_belief(self):
        proposals = self.system.observe(self)
        if proposals:
            target = proposals[0]
        else:
            return
        proposal_id = target._id
        # agent_number = self.model.agent_number
        if self.system.day >= 2:
            vote_action = self.system.vote_actions[target._id]
            yes_amount = sum(x[1] for x in vote_action['yes'])
            no_amount = sum(x[1] for x in vote_action['no'])
            if yes_amount + no_amount < self.model.agent_number/10:
                self.belief = 0.5
                return
            self.belief = yes_amount / (yes_amount + no_amount)
            if self.belief > 0.55:
                self.belief = 1
            elif self.belief < 0.45:
                self.belief = 0
        else:
            self.belief = 0.5

    def step(self):
        if self.system.day < self.join_time:
            return

        proposals = self.system.observe(self)
        if proposals:
            target = proposals[0]
        else:
            return
        self.update_belief()

        def buy_yes_token(_id, amount):
            pay = self.market.calc_price(_id, amount, 0)
            pay = (1 + self.market.fee)*pay
            if pay <= self.token:
                val = self.market.buy(_id, self.unique_id, 'yes_token', amount)
                self.yes_token += amount
                self.token -= val

        def buy_no_token(_id, amount):
            price = self.market.calc_price(_id, 0, amount)
            price = (1 + self.market.fee)*price
            if price <= self.token:
                val = self.market.buy(_id, self.unique_id, 'no_token', amount)
                self.no_token += amount
                self.token -= val

        def sell_yes_token(_id, amount):
            if self.yes_token >= amount:
                val = self.market.sell(
                    _id, self.unique_id, 'yes_token', amount)
                self.yes_token -= amount
                self.token -= val

        def sell_no_token(_id, amount):
            if self.no_token >= amount:
                val = self.market.sell(_id, self.unique_id, 'no_token', amount)
                self.no_token -= amount
                self.token -= val

        def vote_yes(_id, amount=None):
            if not self.voted:
                self.system.vote(self, _id, 'yes')
                self.voted = True
                self.vote = 'yes'

        def vote_no(_id, amount=None):
            if not self.voted:
                self.system.vote(self, _id, 'no')
                self.voted = True
                self.vote = 'no'

        fee = self.market.fee
        yes_price = self.market.calc_current_price(target._id, 'yes')
        yes_cost = yes_price + yes_price*fee
        yes_sell = (1 - fee)*yes_price
        no_price = self.market.calc_current_price(target._id, 'no')
        no_cost = no_price + no_price*fee
        no_sell = (1-fee)*no_price
        if self.belief > 0.5:
            if yes_cost < self.belief:
                buy_yes_token(target._id, 1)
                # print('I am {}, type buy and sell, has token {}, yes cost: {}, beleif: {}, action: buy yes'.format(
                #     self.unique_id, self.token, yes_cost, self.belief))
            if yes_sell > self.belief:
                sell_yes_token(target._id, 1)
                # print('I am {}, type buy and sell, has token {}, yes sell: {}, beleif: {}, action: sell yes'.format(
                #     self.unique_id, self.token, yes_sell, self.belief))
        elif self.belief < 0.5:
            if no_cost < 1 - self.belief:
                buy_no_token(target._id, 1)
                # print('I am {}, type buy and sell, has token {}, no cost: {}, beleif: {}, action: buy no'.format(
                #     self.unique_id, self.token, no_cost, self.belief))

            if no_sell > 1 - self.belief:
                sell_no_token(target._id, 1)
                # print('I am {}, type buy and sell, has token {}, no sell: {}, beleif: {}, action: sell no'.format(
                #     self.unique_id, self.token, no_sell, self.belief))
        # print('current prices yes: {}, no: {}'.format(self.market.calc_current_price(
        #     target._id, 'yes'), self.market.calc_current_price(target._id, 'no')))

        if self.belief > 0.5:
            vote_yes(target._id, 1)
        elif self.belief < 0.5:
            vote_no(target._id, 1)

        # self.token -= val
        self.wealth = self.token + self.no_token * self.market.calc_current_price(target._id, 'no') + \
            self.yes_token * self.market.calc_current_price(target._id, 'yes')
