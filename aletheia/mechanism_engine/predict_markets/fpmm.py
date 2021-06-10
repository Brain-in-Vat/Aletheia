from . import PredictMarket
import math
from enum import Enum


class TokenType(Enum):
    yes_token = 'yes_token'
    no_token = 'no_token'


class FPMM(PredictMarket):
    def __init__(self, fee=0.02, constant=100) -> None:
        super().__init__()
        self.proposal_map = {}
        self.fee = fee
        self.constant = constant

    def submit(self, agent, proposal):
        self.proposals.append(proposal)
        self.proposal_map[proposal._id] = proposal

    def buy(self, proposal_id, agent, token_type, amount):
        proposal = self.proposal_map[proposal_id]
        token_type = TokenType(token_type)
        val = 0
        amount = (1 - self.fee) * amount
        if token_type == TokenType.yes_token:
            val = self.calc_price(proposal._id, amount, 0)
            proposal.yes_token += val
        elif token_type == TokenType.no_token:
            val = self.calc_price(proposal._id, 0, amount)
            proposal.no_token += val
        else:
            raise Exception('unknown token type')
        return amount

    def sell(self, proposal_id, agent, token_type, amount):
        proposal = self.proposal_map[proposal_id]
        token_type = TokenType(token_type)
        val = 0
        if token_type == TokenType.yes_token:
            if amount > proposal.yes_token:
                return 0
            val = (1 - self.fee)*self.calc_price(proposal._id, -amount, 0)
            proposal.yes_token -= amount
        elif token_type == TokenType.no_token:
            if amount > proposal.no_token:
                return 0
            val = (1 - self.fee)*self.calc_price(proposal._id, 0, -amount)
            proposal.no_token -= amount
        else:
            raise Exception('unknown token type')
        return -val

    def calc_price(self, proposal_id, yes_token, no_token):
        """compute the price of current proposal
        """
        proposal = self.proposal_map[proposal_id]
        p_w = proposal.yes_token
        p_l = proposal.no_token
        if proposal.state == 2:
            return yes_token
        elif proposal.state == 3:
            return no_token

        val = 0

        # alpha = yes_token / p_w
        # belta = no_token / p_l
        if yes_token:
            delta_x = yes_token
            x_1 = p_w + delta_x
            delta_y = self.constant/x_1 - p_l
            val = delta_x + delta_y
        elif no_token:
            delta_x = no_token
            x_1 = p_l + delta_x
            delta_y = self.constant/x_1 - p_w
            val = delta_y + delta_x
        return val

    def calc_current_price(self, proposal_id, token_type):
        proposal = self.proposal_map[proposal_id]
        p_w = proposal.yes_token
        p_l = proposal.no_token
        # if proposal.state == 2 and token_type == 'yes':
        #     return 1
        # elif proposal.state == 2 and token_type == 'no':
        #     return 0

        # if proposal.state == 3 and token_type == 'yes':
        #     return 0
        # elif proposal.state == 3 and token_type == 'no':
        #     return 1
        # yes_part = math.exp(p_w/b)
        # no_part = math.exp(p_l/b)
        if token_type == 'yes':
            b = 1 - (p_w + p_l)
            delta_x = (b + math.sqrt(b*b + 4*p_l))
            return 1 - delta_x/2
        else:
            b = 1 - (p_w + p_l)
            delta_x = (b + math.sqrt(b*b + 4*p_w))
            return 1 - delta_x/2
