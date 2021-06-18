from . import PredictMarket
import math
from enum import Enum



class TokenType(Enum):
    yes_token = 'yes_token'
    no_token = 'no_token'

class  LMSRMarket(PredictMarket):
    def __init__(self, choices, b=300):
        self.choices = choices
        self.amounts = {choice: 0 for choice in choices}
        self.finished = False
        self.answer = []
        self.trades = {
            choice: {'id': choice, 'trades': []} for choice in choices
        }
        self.fee = 0.03
        self.b = b
        self.pool = 0
        
    def set_answer(self, choices):
        self.answer = choices
        self.finished = True
        
    def buy(self, choice, amount, user_id):
        if choice not in self.choices:
            raise Exception('unknown choice')
        val = self.calc_price(choice, amount)
        self.amounts[choice] += amount
        fee = self.fee * amount
        self.pool += fee
        self.trades[choice]['trades'].append(
            {'id': user_id, 'amount': amount, 'fee': fee}
        )
        return val
    
    def sell(self, choice, amount, user_id):
        if choice not in self.choices:
            raise Exception('unknown choice')
        val = self.calc_price(choice, -amount)
        self.amounts[choice] -= amount
        fee = self.fee * amount
        self.pool += fee
        self.trades[choice]['trades'].append(
            {'id': user_id, 'amount': -amount, 'fee': fee}
        )
        return val
    
    def calc_price(self, choice, amount):
        if self.finished and choice in self.answer:
            return amount
        elif self.finished:
            return 0
        tmp_amounts = {key: value for key,value in self.amounts.items()}       
        
        tmp_amounts[choice] += amount
        c_n = self.b *math.log(
            sum([math.exp(x/self.b) for x in tmp_amounts.keys()])
        )
        
        c_p = self.b * math.log(
            sum([math.exp(x/self.b) for x in self.amounts.keys()])
        )
        
        val = c_n - c_p
        val = round(val, 2)
        return val
        
    def calc_current_price(self, choice):
        c_p = sum([math.exp(x/self.b) for x in self.amounts.values()])
        
        return math.exp(self.amounts[choice]/self.b) / c_p
    
    def price_calcs(self):
        prices = [
            (choice, self.calc_current_price(choice)) for choice in self.choices
        ]
        return prices
        

        


class LMSR(PredictMarket):
    def __init__(self, fee=0.02) -> None:
        super().__init__()
        self.proposal_map = {}
        self.fee = fee

    def submit(self, agent, proposal):
        self.proposals.append(proposal)
        self.proposal_map[proposal._id] = proposal

    def buy(self, proposal_id, agent, token_type, amount):
        proposal = self.proposal_map[proposal_id]
        token_type = TokenType(token_type)
        val = 0
        if token_type == TokenType.yes_token:
            val = (1 + self.fee)*self.calc_price(proposal._id, amount, 0)
            proposal.yes_token += amount
        elif token_type == TokenType.no_token:
            val = (1 + self.fee)*self.calc_price(proposal._id, 0, amount)
            proposal.no_token += amount
        else:
            raise Exception('unknown token type')
        return val

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
            val = (1 - self.fee)*self.calc_price(proposal._id, -amount, 0)
            proposal.no_token -= amount
        else:
            raise Exception('unknown token type')
        return val

    def calc_price(self, proposal_id, yes_token, no_token):
        """compute the price of current proposal
        """
        proposal = self.proposal_map[proposal_id]
        b = proposal.b_number
        p_w = proposal.yes_token
        p_l = proposal.no_token
        if proposal.state == 2:
            return yes_token
        elif proposal.state == 3:
            return no_token

        c_n = b * math.log(math.exp((p_w + yes_token)/b) +
                           math.exp((p_l + no_token)/b))
        c_p = b * math.log(math.exp(p_w/b) + math.exp(p_l/b))
        val = c_n - c_p
        val = round(val, 2)
        return val

    def calc_current_price(self, proposal_id, token_type):
        proposal = self.proposal_map[proposal_id]
        b = proposal.b_number
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

        yes_part = math.exp(p_w/b)
        no_part = math.exp(p_l/b)
        if token_type == 'yes':
            return yes_part / (yes_part + no_part)
        else:
            return no_part/(yes_part + no_part)
