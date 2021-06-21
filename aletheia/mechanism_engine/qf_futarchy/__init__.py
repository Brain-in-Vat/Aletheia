'''
predict project in futarchy
next round come out
'''
from aletheia.mechanism_engine.predict_markets.lmsr import LMSRMarket
from aletheia.mechanism_engine.qf import QuadraticFunding


class QFFutarchy:
    def __init__(self, pass_ratio=0.8, projects=[0, 1]):
        self.projects = projects
        self.lmsr = LMSRMarket(self.projects)
        self.fee = 0.03
        self.fee_pool = 0
        self.round = 0
        self.clr = QuadraticFunding()
        self.grant_history = []
        self.history_market = []
        self.history_clr = []
        self.award_list = []
        self.pass_ratio = pass_ratio
        self.pool = 0

    def finish_round(self):
        result = {}
        prices = self.lmsr.price_calcs()
        prices = sorted(prices, key=lambda x: x[1], reverse=True)
        choice = [price[0] for price in prices]

        pass_indice = int(self.pass_ratio * len(self.projects))
        self.lmsr.set_answer(choice[:pass_indice])
        if self.history_market:
            last_market = self.history_market[-1]
            last_market.set_answer(choice)

            result['award_predict_winner'] = self.award_predict_winner()

        result['award_vote_winner'] = self.award_vote_winner()

        self.history_market.append(self.lmsr)

        self.compute_grants_from_market()
        self.lmsr = LMSRMarket(self.projects)

        # self.clr.grants = {
        #     key:value for key,value in self.clr.grants.items() if key in choice
        # }
        self.grant_history.append(self.clr.clr_calcs())
        result['cls_grants'] = self.clr.clr_calcs()
        self.history_clr.append(self.clr)
        self.clr = QuadraticFunding()
        return result

    def award_predict_winner(self):
        if len(self.award_list) == len(self.history_market):
            return {}
        last_market = self.history_market[-1]
        trades = last_market.trades
        answer = last_market.answer

        trades = {k: v for k, v in trades.items() if k in answer}

        users = {}
        for k, v in trades.items():
            trades = v['trades']
            for trade in trades:
                if trade['id'] in users:
                    users[trade['id']] += trade['amount']
                else:
                    users[trade['id']] = trade['amount']

        self.award_list.append(1)
        return users

    def compute_grants_from_market(self):
        last_market = self.lmsr

        trades = last_market.trades
        answer = last_market.answer

        trades = {k: v for k, v in trades.items() if k in answer}

        users = {}
        for k, v in trades.items():
            trades = v['trades']
            for trade in trades:
                if trade['id'] in users:
                    users[trade['id']] += trade['amount']
                else:
                    users[trade['id']] = trade['amount']
            for user_id, amount in users.items():
                self.clr.grant(k, user_id, amount)

    def award_vote_winner(self):
        last_market = self.lmsr
        trades = last_market.trades
        answer = last_market.answer
        pool = last_market.pool

        trades = {k: v for k, v in trades.items() if k in answer}

        users = {}
        for k, v in trades.items():
            trades = v['trades']
            for trade in trades:
                if trade['id'] in users:
                    users[trade['id']] += trade['amount']
                else:
                    users[trade['id']] = trade['amount']
        total = sum(list(users.values()))
        users = {
            k: pool * (v / total) for k, v in users.items()
        }
        return users
