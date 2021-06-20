from mesa import Agent, Model
import random


class RandomAgent(Agent):
    def __init__(self, unique_id, model, token):
        super().__init__(unique_id, model)
        self.token = token
        self.model = model
        
    def donate(self):
        projects = self.model.projects
        project = random.choice(projects)
        
        if 'qf_futarchy' in dir(self.model):
            self.model.qf_futarchy.lmsr.buy(project, 1, self.unique_id)
        elif 'qf' in dir(self.model):
            self.model.qf.grant(project, self.unique_id, 1)
            
    def step(self):
        dice = random.random()
        if dice <= 0.5:
            self.donate()
            
# fix agent
"""
the agent is controlled by simple zero aligent rules
when the actual price is below his expect, it will buy it
otherwise, it wont do anything
"""
class FixZLAgent(Agent):
    def __init__(self, unique_id, model, token, beliefs):
        super().__init__(unique_id, model)
        self.token = token
        self.model = model
        self.beliefs = beliefs
        self.grant = {}
        self.brain_token = 0
        
    def award_token(self, token):
        self.token += token
        
    def award_brain_token(self, brain_token):
        self.brain_token += brain_token
        
    def donate(self):
        def buy(project):
            token_cost = self.model.qf_futarchy.lmsr.calc_price(project, 1)

            if self.token + self.brain_token > token_cost:
                self.model.qf_futarchy.lmsr.buy(project, 1, self.unique_id)
                if token_cost >= self.brain_token:
                    self.brain_token -= token_cost
                else:
                    token_cost = token_cost - self.brain_token
                    self.brain_token = 0
                    self.token = self.token - token_cost
                
        def grant(project):
            grant_cost = self.beliefs[project]
            if self.token > self.beliefs[project]:
                self.token = self.token - grant_cost
                self.model.qf.grant(project, self.unique_id, self.beliefs[project])

        projects = self.model.projects

        if 'qf_futarchy' in dir(self.model):
            for project in projects:
                if self.beliefs[project] > self.model.qf_futarchy.lmsr.calc_current_price(project):
                    buy(project)
        elif 'qf' in dir(self.model):
            for project in projects:
                if self.grant[project] != True:
                    # self.model.qf.grant(project, self.unique_id, self.beliefs[project])
                    grant(project)
                
    def step(self):
        dice = random.random()
        if dice <= 0.5:
            self.donate()
                