'''
This is the python code part of zero intelligence agent.
pre require:
    owlready2
    mesa
'''
from mesa.agent import Agent
from owlready2 import set_datatype_iri, World, sync_reasoner_pellet

agent_base = 'zlagent.owl'
set_datatype_iri(float, 'http://www.w3.org/2001/XMLSchema#float')


class ZLAgent(Agent):
    def __init__(self, kb_path, unique_id, model):
        super().__init__(unique_id, model)
        self.kb_path = kb_path
        if not self.kb_path:
            self.kb_path = agent_base
        self.world = World()
        self.onto = self.world.get_ontology(self.kb_path)
        self.onto.load()
        self.unique_id = unique_id
        self.model = model

    def think(self):
        """reason in kb using predefined rulers
        reason process dont introduce any new individuals
        """
        try:
            with self.onto:
                sync_reasoner_pellet(self.world, infer_property_values=True,
                                     infer_data_property_values=True, debug=2)

        except Exception as e:
            print(e)
        self._replace_ready_property()

    def _replace_ready_property(self):
        # update goal
        individuals = self.onto.individuals()
        for individual in individuals:
            property_names = [
                property._name for property in individual.get_properties()]
            update_paris = []
            for property_name in property_names:
                if property_name.endswith('Ready'):
                    update_paris.append((property_name, property_name[:-5]))
            if update_paris:
                for property_ready, property in update_paris:
                    ready_value = eval('individual.' + property_ready)
                    now_value = eval('individual.' + property)
                    if not ready_value:
                        continue

                    if isinstance(ready_value, list):
                        individual.__dict__[property_ready] = []
                        if isinstance(now_value, list):
                            individual.__dict__[property] = ready_value
                        else:
                            individual.__dict__[property] = ready_value[0]
                    else:
                        individual.__dict__[property_ready] = None
                        if isinstance(now_value, list):
                            individual.__dict__[property] = [ready_value]
                        else:
                            individual.__dict__[property] = ready_value

    def observe(self):
        """ here update the knowlege of agent 
            the zlagent focus on the trade price when they make descisions
        """
        self.onto.noToken.currentPrice = 0.5
        self.onto.yesToken.currentPrice = 0.5
        self.onto.GNO.myBanlance = 10
        self.onto.mySelf.myWealth = 10

    def execute(self):
        """here u write the execute logical
        """
        print('this agent is executing')
        pass

    def step(self):
        self.observe()
        self.think()
        self.execute()

    def print_beleif(self):
        """
        """

        pass

    def add_belief(self):
        pass


if __name__ == '__main__':
    agent = ZLAgent(None, None, None)
    agent.step()
